# AUdoc — Feature D: Owner-Approval Email Gate for Data Deletion

**Scope:** close a real gap in the Danger Zone's data-deletion actions —
one of the two deletion paths already emails the site owner for approval,
the other does not. This plan makes both go through the same
owner-approval gate, and fixes a couple of small inconsistencies found
along the way.

**Status: partially implemented already.** This is not a from-scratch
build — read §0 carefully before changing anything, since roughly half of
this already exists and works correctly. Do not touch the parts marked
"already correct — do not change."

---

## 0. Ground truth — what's actually in the repo right now

`app/views.py`, `admin_clear_all_data` (superuser-only, gated by
`@_admin_required` + an explicit `request.user.is_superuser` check) handles
**two different actions** depending on the `confirmation` POST value, and
they are **not equally protected today**:

### 0.1 Full wipe (`confirmation == 'DELETE_ALL_STUDENT_DATA'`) — already correct, do not change the shape of this

1. Admin types the exact phrase `DELETE_ALL_STUDENT_DATA` and their own
   password in the Danger Zone modal (`admin_panel.html`, `#purgeForm`,
   `dzOpenPurgeModal(true)`).
2. `admin_clear_all_data` verifies the password, signs a token with
   `django.core.signing.TimestampSigner`, and emails a confirm link to a
   **hardcoded** address, `"sayankumarr@gmail.com"`, valid for 1 hour.
3. Nothing is deleted yet at this point — the admin sees "a confirmation
   email has been sent," which is correct, keep this message shape.
4. Only when that emailed link is opened does
   `admin_confirm_clear_all_data(request, token)` actually run the
   deletion — it unsigns the token (1-hour `max_age`), and if it decodes
   to `"DELETE_ALL_STUDENT_DATA"`, wipes every student-related model in
   FK-safe order and all non-staff `User` accounts.

This is already the exact "admin requests → owner approves by email →
only then it executes" pattern being asked for. **Keep this working
exactly as it does today** — don't rename `admin_clear_all_data`,
`admin_confirm_clear_all_data`, their URLs, the confirmation phrase, or
the password-check step on the request side.

### 0.2 Selective delete (`confirmation == 'CONFIRMED_SELECTIVE_DELETE'`) — this is the gap

Same modal, same password check — but for this branch, `admin_clear_all_data`
skips the email/token step entirely and **deletes the selected categories
immediately**, in the same request, with no owner approval at all:

```python
elif confirmation == 'CONFIRMED_SELECTIVE_DELETE':
    selected_data = request.POST.get('selected_data', '')
    categories = [c.strip() for c in selected_data.split(',') if c.strip()]
    ...
    for cat in categories:
        if cat in deletion_map:
            model_class, display_name = deletion_map[cat]
            count = model_class.objects.count()
            model_class.objects.all().delete()   # <-- runs immediately, no approval
```

This lets any superuser permanently wipe an entire category — all
Appointments, all Blood Donations, all Blood Requests, all Login Logs,
etc. — with nothing but their own password. For a clinic's appointment or
blood-donation history, that's not meaningfully less destructive than the
full wipe, it's just narrower in scope. **This is the actual gap to
close.**

### 0.3 Two smaller things found while reading this code

- The full-wipe path has **no `log_security_event` call anywhere** —
  neither when the email is sent nor when the deletion actually executes.
  The selective-delete path *does* call `log_security_event("selective_data_delete", ...)`.
  So today, the *more* destructive action is the one with *no* audit trail.
  Worth fixing alongside this change (see §3.4).
- The approval email address is a **hardcoded string literal**,
  `"sayankumarr@gmail.com"`, directly in `views.py`. Works, but fragile —
  should be a setting sourced from an environment variable, the same way
  `RESEND_API_KEY` already is (see `AUdoc_back/settings.py` line ~258:
  `RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")`). See §3.1.

---

## 1. What to build

Extend the exact same "sign a token → email the owner → only the emailed
link executes anything" pattern from §0.1 to also cover selective delete,
and add two things neither path has today: an explicit **decline** option
(right now, not clicking the link is the only way to "decline" — there's
no button, no record of a decline, no notification to whoever asked), and
a **mandatory reason** field so the owner has context to decide quickly
without needing to ask.

Both deletion types should end up sharing **one mechanism**, not two
parallel copies of the same email/token logic — partly for less code to
maintain, partly because this is the same shape of problem the site
already discussed adding to a *different* Danger Zone action (an
emergency site-shutdown button) in an earlier planning conversation. That
shutdown/approval feature is **not** part of this plan and should not be
built here — but design the mechanism below so it *could* be reused for
that later without rework, rather than building something
deletion-specific that would need to be redone.

### 1.1 Stay stateless — no new database table

The existing full-wipe flow needs **zero new models or migrations** — the
signed token itself carries everything (`TimestampSigner` handles the
1-hour expiry natively; the payload carries the rest). Keep it that way
for the selective-delete path too, rather than introducing an
`ApprovalRequest` model. Encode a small JSON payload instead of the bare
string currently used, so one token can describe either action type:

```python
import json
payload = json.dumps({
    "action": "FULL_WIPE",              # or "SELECTIVE_DELETE"
    "categories": categories,           # [] for FULL_WIPE, the chosen list otherwise
    "requested_by_id": request.user.id,
    "requested_by_email": request.user.email,
    "reason": reason,                   # new — see §1.2
})
token = signer.sign(payload)
```

(Today's full-wipe signs the bare string `"DELETE_ALL_STUDENT_DATA"` — 
switching to a JSON payload is a deliberate, required change so the same
token shape works for both actions and can carry the reason + requester
info. `admin_confirm_clear_all_data` needs updating to decode JSON instead
of comparing a bare string — see §3.2.)

### 1.2 Mandatory reason field

Neither deletion path today asks the requesting admin *why*. Add a
required textarea to the same Danger Zone modal (`#purgeForm` in
`admin_panel.html`) — the owner should never have to open the app and
guess why someone wants to wipe, say, every blood request on file. Block
submission client-side if it's empty, and re-validate server-side (reject
with `messages.error` if missing — same pattern already used for the
confirmation-phrase mismatch).

### 1.3 Decline path

Add one new view + URL, shared by both action types since declining does
the same thing either way — log it, don't touch any data, tell the
requester:

```python
path("manage/data-purge/decline/<str:token>/", views.admin_decline_data_action, name="admin_decline_data_action"),
```

```python
@_admin_required
def admin_decline_data_action(request, token):
    from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
    import json
    try:
        signer = TimestampSigner()
        payload = json.loads(signer.unsign(token, max_age=3600))
        log_security_event("data_deletion_declined", request, {
            "action": payload["action"],
            "categories": payload.get("categories", []),
            "reason": payload.get("reason", ""),
        }, level="info")
        _notify_requester_of_decision(payload, approved=False)
        messages.info(request, "Deletion request declined. No data was changed.")
    except (SignatureExpired, BadSignature):
        messages.error(request, "This link has expired or is invalid.")
    return redirect(f"{reverse('admin_dashboard')}?tab=danger-zone")
```

Put a second button/link in the approval email next to the existing
"CONFIRM & DELETE" one — same token, different URL, so one email carries
both options rather than needing two separate emails.

### 1.4 Notify the requester of the outcome

Small addition, closes the loop for whichever admin clicked the original
button — right now they have no way to find out what the owner decided
short of checking whether their data disappeared. Add a helper:

```python
def _notify_requester_of_decision(payload, approved: bool, deleted_summary: str = ""):
    requester_email = payload.get("requested_by_email")
    if not requester_email:
        return
    outcome = "approved and completed" if approved else "declined"
    subject = f"Your data deletion request was {outcome}"
    body = (
        f"Your request to delete {'ALL student data' if payload['action'] == 'FULL_WIPE' else ', '.join(payload.get('categories', []))} "
        f"was {outcome} by the site owner."
        + (f"\n\n{deleted_summary}" if deleted_summary else "")
    )
    msg = EmailMultiAlternatives(subject, body, None, [requester_email])
    send_email_async(msg)
```

Call this from both `admin_confirm_clear_all_data` (after a successful
deletion, `approved=True`, with a short summary of what was deleted) and
`admin_decline_data_action` (`approved=False`).

---

## 2. Exact changes, file by file

### 2.1 `AUdoc_back/settings.py`

Add, near the other `os.environ.get(...)`-backed settings (next to
`RESEND_API_KEY`, ~line 258):

```python
# Who gets asked to approve destructive Danger Zone actions (data purges,
# and in future, site shutdown). Falls back to the address already
# hardcoded in views.py today, so behavior doesn't change unless this is
# explicitly set.
OWNER_APPROVAL_EMAIL = os.environ.get("OWNER_APPROVAL_EMAIL", "sayankumarr@gmail.com")
```

### 2.2 `app/views.py` — `admin_clear_all_data`

- Full-wipe branch (`confirmation == 'DELETE_ALL_STUDENT_DATA'`): keep the
  existing password check and email-sending shape, but (a) read the new
  `reason` field and reject if blank, (b) switch the signed payload from
  a bare string to the JSON shape in §1.1, (c) read the approval address
  from `settings.OWNER_APPROVAL_EMAIL` instead of the hardcoded string,
  (d) add a `log_security_event("data_deletion_requested", ...)` call
  right after the email sends successfully (closes the gap in §0.3).
- Selective-delete branch (`confirmation == 'CONFIRMED_SELECTIVE_DELETE'`):
  **stop deleting anything here.** Instead, mirror exactly what the
  full-wipe branch does — validate `reason` is present, build the same
  JSON payload with `"action": "SELECTIVE_DELETE"` and the chosen
  `categories`, sign it, email `settings.OWNER_APPROVAL_EMAIL`, log a
  `data_deletion_requested` security event, and show the same "sent for
  approval" message shape the full-wipe branch already uses. **Do not
  actually delete any records in this branch anymore** — deletion only
  happens in `admin_confirm_clear_all_data`, for both action types.

### 2.3 `app/views.py` — `admin_confirm_clear_all_data`

- Decode the token payload as JSON (§1.1) instead of comparing a bare
  string.
- If `payload["action"] == "FULL_WIPE"`: run exactly the deletion logic
  that's already there today, unchanged.
- If `payload["action"] == "SELECTIVE_DELETE"`: run the same
  category-driven deletion loop currently sitting in the selective-delete
  *request* branch (the `for cat in categories: ... .delete()` block) —
  it's moving here, not being rewritten.
- After either deletion completes, call
  `log_security_event("data_deletion_executed", ...)` (new — closes the
  other half of the §0.3 gap) and `_notify_requester_of_decision(payload, approved=True, deleted_summary=...)`.
- Keep the existing `SignatureExpired` / `BadSignature` handling as-is.

### 2.4 `app/views.py` — new views/URLs

- `admin_decline_data_action` (§1.3).
- `_notify_requester_of_decision` helper (§1.4) — put it near
  `_terminate_non_staff_sessions`/other small private helpers already in
  this file, for consistency with existing organization.

`app/urls.py` — one new line:
```python
path("manage/data-purge/decline/<str:token>/", views.admin_decline_data_action, name="admin_decline_data_action"),
```

### 2.5 `app/templates/app/admin_panel.html`

- Add a required `<textarea>` for "Reason for this deletion" inside
  `#purgeForm`/the purge modal — same visual style as the existing
  confirmation-phrase input, wired into the existing
  `dzOpenPurgeModal`/submit JS so it's sent as a normal POST field
  (e.g. `reason`) alongside `confirmation`, `selected_data`, and
  `admin_password`.
- No other template changes needed — the messaging after submit already
  flows through the existing `{% if messages %}` block, so "your
  selective delete request has been sent to the owner for approval" shows
  up automatically once the view sends that message, same as full-wipe
  already does today.
- Update the email HTML built in `admin_clear_all_data` to also state the
  reason and, for selective delete, which categories were requested —
  keep the same visual style already used there (red accent, "CONFIRM &
  DELETE" button) and add a second, less prominent "Decline" link/button
  pointing at the new decline URL.

---

## 3. Non-breaking checklist

- [ ] Existing full-wipe UX is unchanged from the requesting admin's
      point of view: same modal, same typed phrase
      (`DELETE_ALL_STUDENT_DATA`), same password field, same "email sent"
      message — the only *new* required input is the reason textarea.
- [ ] `admin_clear_all_data` and `admin_confirm_clear_all_data` keep their
      exact names and URL patterns — nothing that links to them elsewhere
      needs to change.
- [ ] Selective delete **no longer deletes anything synchronously** —
      write a test asserting a `CONFIRMED_SELECTIVE_DELETE` POST leaves
      every model's row count unchanged, and only
      `admin_confirm_clear_all_data` (via the emailed link) actually
      removes rows.
- [ ] `OWNER_APPROVAL_EMAIL` defaults to the exact address already
      hardcoded today, so nothing breaks for anyone who doesn't set the
      env var.
- [ ] A token signed under the *old* bare-string format
      (`signer.sign("DELETE_ALL_STUDENT_DATA")`) that might already be
      sitting unopened in someone's inbox at deploy time will fail to
      `json.loads()` — decide whether that's acceptable (most likely yes,
      since these links expire in 1 hour and this is a rarely-used
      action) or add a fallback that treats a plain-string unsign result
      as an implicit `FULL_WIPE` with no reason/requester. Recommend the
      former (accept the edge case) unless a purge was literally
      mid-flight at deploy time.
- [ ] Run `python manage.py check` after every file change, not just at
      the end.

---

## 4. Testing plan

Add `app/tests_data_deletion_approval.py` covering:

- Submitting `CONFIRMED_SELECTIVE_DELETE` with valid categories and a
  reason sends exactly one email to `settings.OWNER_APPROVAL_EMAIL` and
  **does not** change any row counts.
- Submitting either deletion type with a blank `reason` is rejected
  (`messages.error`, no email sent, no deletion).
- Visiting `admin_confirm_clear_all_data` with a valid, unexpired
  `SELECTIVE_DELETE` token deletes exactly the categories encoded in the
  token and nothing else.
- Visiting the same confirm URL a second time with an already-expired
  token (mock `max_age=3600` having elapsed) shows the existing
  "expired" message and changes nothing.
- Visiting `admin_decline_data_action` with a valid token changes nothing,
  logs a `data_deletion_declined` security event, and sends exactly one
  notification email to the original requester's address (not the
  owner's).
- The existing full-wipe flow, end to end, still results in the same rows
  being deleted as it does today — this is the regression test that
  matters most, since §2.3 is the one piece of already-working code being
  touched.

---

## 5. Appendix — explicitly out of scope for this plan

- **Site-shutdown approval** — discussed separately, not part of this
  change. The mechanism above (JSON-payload signed tokens, confirm/decline
  pair, requester notification) was deliberately shaped so that feature
  could reuse the same pattern later rather than inventing a second one,
  but do not build it as part of this plan.
- **Visible "pending approval" status in `/manage/`** — since this stays
  stateless (§1.1), there's no database row to display a live pending-request
  list from. Adding that later would mean introducing a lightweight model
  after all — deliberately not doing that now, per the instruction to
  keep everything else fixed and minimize new surface area.
