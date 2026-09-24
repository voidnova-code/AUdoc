# AUdoc — Prescription Feature Set: Implementation Plan

**Scope:** (A) Digital medical-history / prescription form, (B) Medicine stock
packs-and-strips support, (C) Digital Prescription delivered by email +
downloadable as PNG.

**Audience:** an engineer or coding agent implementing directly against the
real AUdoc Django repo (`AUdoc_back/`). Every file path, model, and function
name below was verified against the actual codebase — nothing here is
guessed. Where a change is still open, it says so explicitly.

**Prime directive:** every phase must end with `python manage.py check`
passing and the existing test files (`app/tests_maintenance.py`,
`app/tests_prescription.py`) still green, before moving to the next phase.
Additive changes only — do not rename existing URL names, view names, or
template IDs unless a step below says to.

---

## 0. Ground truth (verified facts to design against)

These are load-bearing facts about the existing codebase. Get these wrong
and any of the three features below will misbehave in production.

| Fact | Detail |
|---|---|
| Email sending pattern | `django.core.mail.EmailMultiAlternatives(subject, body, from_email=None, to=[...])` → `.attach_alternative(html, "text/html")` → **`send_email_async(msg)`** (a threaded, fire-and-forget helper already defined near the top of `app/views.py`, ~line 77). All transactional emails in this app follow this exact pattern — do not introduce a second pattern. |
| Email HTML style | Inline HTML strings built as Python triple-quoted f-strings directly inside the view function (no separate template file for emails). Footer convention: `background:#f4f8fc; border-top:1px solid #e5edf5;`, text `© 2026 AUdoc — Assam University Silchar Campus Health`, `Academic Block C, Room 101 | health@au.edu`. Accent color varies by email type (blue `#1a5c96` for OTP, red `#c41e3a` for blood donation) — use the site's primary green `#4a7c59` / `#2e5c3a` for prescription emails, since that's the brand color used throughout the student-facing app and the two prescription artifacts already shown to the client. |
| Image library | **Pillow is already in `requirements.txt`** (`Pillow>=9.5.0`). No new dependency needed for server-side PNG generation. Do **not** add `weasyprint`, `imgkit`, `wkhtmltoimage`, or `playwright` — these need system binaries/browser downloads that are not confirmed available on the Render deployment and risk breaking the build. |
| No bundled fonts | There are currently **no `.ttf`/`.otf` files anywhere in the repo**. Pillow's `ImageFont.load_default()` is a tiny bitmap font and will look unprofessional. A font must be added (see §3.2). |
| Student auth | Students log in via `app.backends.StudentIDBackend` (OTP, no password) and get a **real Django session** — `request.user.is_authenticated` works normally for them. The link from `User` to student identity is `request.user.student_profile.student_id` (`StudentProfile` is a `OneToOneField` to `User`). Staff/doctors have no `student_profile`. |
| No student-facing history/prescription page exists yet | Confirmed via `app/urls.py` — there is no route for a student to view or download their own history/prescription today. This is new ground, not a rename. |
| `MedicalHistory` fields | `student_id` (CharField, **not a FK**), `doctor_name` (CharField, plain text snapshot, not a FK), `appointment_date`, `illness`, `symptoms`, `medicines` (M2M through `PrescribedMedicine`), `created_at`, `updated_at`. There is **no** doctor registration number or specialization stored on this model — don't invent one in the rendered prescription; either omit it or look it up via `Doctor.objects.filter(name=doctor_name).first()` as a best-effort (name match is not guaranteed unique, treat as decorative only). |
| `Appointment.email` | Confirmed field, `EmailField`, always populated at booking time. This is the send-to address for the prescription email. |
| `PrescribedMedicine` already has full dosage-schedule fields | See §1 — this was implemented in a prior phase and is the data source for both the on-screen prescription and the rendered PNG. |
| `Medicine.pack_size` already exists | See §2 — added in a prior phase, default `1`. |

---

## 1. Feature A — Digital Prescription Data Capture (Medical History form)

**Status: implemented.** This section documents what already exists so
whoever works on Feature C (§3) knows exactly what data is available to
render, and so this work can be verified/ported into the live repo rather
than redone.

### 1.1 Model — `app/models.py`, `PrescribedMedicine`

Each prescribed medicine line is now a real prescription entry, not just a
name + quantity:

```python
class PrescribedMedicine(models.Model):
    FOOD_TIMING_CHOICES = [
        ("BEFORE", "Before Food"), ("AFTER", "After Food"),
        ("WITH", "With Food"), ("ANYTIME", "Anytime"),
    ]
    ROUTE_CHOICES = [
        ("ORAL", "Oral"), ("TOPICAL", "Topical / Apply"), ("DROPS", "Drops"),
        ("INJECTION", "Injection"), ("INHALER", "Inhaler"), ("OTHER", "Other"),
    ]
    medical_history = models.ForeignKey('MedicalHistory', on_delete=models.CASCADE)
    medicine        = models.ForeignKey('Medicine', on_delete=models.CASCADE)
    quantity        = models.PositiveIntegerField(default=1)          # total units dispensed
    dosage          = models.CharField(max_length=100, blank=True, default="")   # e.g. "500mg"
    take_morning    = models.BooleanField(default=False)
    take_afternoon  = models.BooleanField(default=False)
    take_evening    = models.BooleanField(default=False)
    take_night      = models.BooleanField(default=False)
    food_timing     = models.CharField(max_length=10, choices=FOOD_TIMING_CHOICES, default="AFTER")
    duration_days   = models.PositiveIntegerField(default=1)
    route           = models.CharField(max_length=10, choices=ROUTE_CHOICES, default="ORAL")
    instructions    = models.CharField(max_length=300, blank=True, default="")

    # Helper properties used everywhere this gets displayed:
    #   frequency_pattern -> "1-0-0-1"  (Morning-Afternoon-Evening-Night)
    #   doses_per_day      -> int
    #   schedule_display    -> "500mg · Morning, Night · After Food · 3 days"
```

Migration: `app/migrations/0042_prescribedmedicine_dosage_and_more.py`
(additive `AddField`s + one `AlterField` on `quantity` for its new
`verbose_name` — safe on existing rows, all new fields have defaults).

### 1.2 View — `app/views.py`, `save_medical_history`

Rewritten to accept a **JSON payload** (was a bare `"id:qty,id:qty"` string)
via `MedicalHistoryForm.prescription_data` (renamed from `medicine_ids`).
Server-side validation on every line: `duration_days` clamped 1–90,
`quantity` clamped 1–1000, invalid `food_timing`/`route` values fall back to
safe defaults, unknown `medicine_id`s are silently skipped (never a 500).
Stock deduction (FEFO — first-expiring batch first) and
`MedicineStockTransaction` logging already fire automatically here — **this
is the "Add Medical History also updates the medicine transaction"
automation** referenced in Feature B; it does not need to change for
Feature B or C.

### 1.3 Form — `app/forms.py`, `MedicalHistoryForm`

`medicine_ids` → renamed `prescription_data` (hidden `CharField`, JSON).
`illness` field now has `list="commonIllnessList"` for datalist autocomplete.

### 1.4 New helpers — `app/views.py`

- `_medicines_with_stock()` — active medicines annotated with live unexpired
  stock (two separate queries, deliberately avoiding Django's
  aggregate-fan-out bug from combining two reverse-relation `Sum`/`Count`
  in one `annotate()` call).
- `_frequent_medicines(limit=8)` — top prescribed medicines, for quick-add
  chips.
- `_medicine_catalog_json()` — plain-dict list for the JS picker, embedded
  via `{{ medicine_catalog|json_script:"rxMedicineCatalog" }}`.

### 1.5 New constant — `app/models.py`

`COMMON_ILLNESSES` — flat list of ~35 common campus-clinic illnesses, used
purely as a `<datalist>` autocomplete (never enforced server-side).

### 1.6 Template — `app/templates/app/admin_panel.html`

The `#addHistoryModal` (Danger-Zone-adjacent "Todays Appointments" tab) was
rebuilt into a full prescription builder:
- Illness field with datalist.
- Quick-add chips for the clinic's most-frequently-prescribed medicines.
- Type-to-filter medicine search with a live stock badge (ok/low/out).
- Per-medicine editable "prescription line": dosage text, route select,
  4 timing toggle chips (Morning/Afternoon/Evening/Night), 4 food-timing
  chips, duration presets (3/5/7/10d) + custom input, and an
  **auto-calculated quantity** (`doses_per_day × duration_days`) that stops
  auto-syncing the moment the doctor manually edits it.
- All vanilla JS, wrapped in a single IIFE (`Digital Prescription Builder`
  block, search for that comment) to avoid polluting global scope. Only
  `window.showMedicalHistory` is exported, since the "Add History" button
  in the Today's Appointments list calls it via inline `onclick`.

`app/templates/app/doctor_portal.html` record cards were updated to show
`pm.frequency_pattern` next to each medicine name (guarded so legacy rows
with no timing set don't show a meaningless `0-0-0-0` badge).

### 1.7 Tests

`app/tests_prescription.py` — covers: the modal renders with the new JSON
catalog present; a full structured prescription saves every field correctly
and deducts stock; out-of-range/invalid values get clamped, not rejected;
unknown medicine IDs are skipped without error.

### 1.8 Action items for whoever picks this up

- [ ] Port these exact changes into the live repo (they exist today only in
      a working copy from a prior session) — diff against the current
      `AUdoc-main` and apply.
- [ ] Run `python manage.py test app.tests_prescription` and confirm green
      before starting Feature C, since Feature C reads this same data.
- [ ] No further design work needed here unless product feedback changes.

---

## 2. Feature B — Medicine Stock: Packs & Strips

**Status: backend done, UI not yet updated.** The real risk this closes:
today, `MedicineStock.quantity` has no defined atomic unit — a staff member
could type "5" meaning 5 strips-of-10 while the prescribing flow (§1)
always deducts in individual dispensable units. That mismatch would
silently overdraw a batch by 10× with no error. The fix is to make
`quantity` **always** mean individual units, and let staff optionally enter
stock as *packs* on the way in, auto-multiplied.

### 2.1 Model — `app/models.py` (done)

```python
class Medicine(models.Model):
    ...
    pack_size = models.PositiveIntegerField(
        default=1, verbose_name="Units per Pack/Strip",
        help_text="e.g. 10 for a strip of 10 tablets. Leave as 1 if this "
                   "medicine isn't received in packs/strips — stock always "
                   "tracks individual units regardless.",
    )

    @property
    def packs_and_loose(self):
        """(full_packs, loose_units), derived from total_available_quantity — never stored."""
        total = self.total_available_quantity
        if self.pack_size and self.pack_size > 1:
            return divmod(total, self.pack_size)
        return (0, total)

    @property
    def stock_display(self):
        """'54 Tablets (5 packs + 4 loose)' — or '54 Tablets' when pack_size == 1."""
        ...
```

Same `packs_and_loose` / `stock_display` pair added to `MedicineStock` (per
batch, using `self.medicine.pack_size`).

**Design rule — do not deviate:** `quantity` is the single source of truth
and is always in atomic units. Packs are a *display and data-entry*
convenience only, computed via `divmod()`, never stored as a separate
field. This is deliberate — a dual-count model (packs_remaining +
loose_units stored separately) was considered and rejected because it
requires "break open a pack" logic on every deduction and gives two numbers
that can drift out of sync for no real benefit here.

Migration: `app/migrations/0043_medicine_pack_size.py` (single `AddField`,
`default=1`, safe on all existing rows and existing prescriptions).

### 2.2 Views — `app/views.py` (done)

- `admin_medicine_save` — now reads `pack_size` from POST (clamped 1–1000,
  falls back to 1 on bad input), saved on both the create and update path.
- `admin_medicine_stock_save` — new optional `entry_mode` POST field
  (`'units'` default, or `'packs'`). When `'packs'`, reads `packs` from POST
  and computes `quantity = packs * medicine.pack_size` before saving —
  works on both the "new batch" and "edit batch" path (looks up the
  medicine via the existing stock when editing, since `medicine_id` isn't
  posted on edit).
- `admin_medicine_transaction_save` — same `entry_mode`/`packs` handling
  for manual ADD/SUBTRACT adjustments against an existing batch.

None of the *dispensing* logic (§1.2) changed — it was already correct
under the "quantity = atomic units" rule; this phase only fixes the
*receiving* side.

### 2.3 Remaining work — templates (`app/templates/app/admin_panel.html`)

All open. Locate via the existing anchors already in the file:

**(a) Add Medicine modal (`#medicineModal`, ~line 5950)**
Add a `pack_size` number input (default `1`, min `1`), with helper text
"Leave as 1 if not sold in strips/packs." Wire into the existing form (it
already POSTs to `admin_medicine_save`, which now reads this field — no
view change needed here, purely a template addition).

**(b) Catalog table (`#med-catalog`, ~line 2619)**
Replace the bare `{{ med.total_available_quantity }}` badge with
`{{ med.stock_display }}` (e.g. `"54 Tablets (5 packs + 4 loose)"`).

**(c) Stocks & Batches table (`#med-stocks`, ~line 2659)**
Replace `{{ stock.quantity }}` with `{{ stock.stock_display }}` in the
Quantity column.

**(d) Overview sub-tab expiring/expired lists (~lines 2567–2596)**
Same swap: `{{ stock.quantity }} units` → `{{ stock.stock_display }} {{ stock.medicine.unit }}`.

**(e) Add Stock modal (`#stockModal`, ~line 5967)**
Add an entry-mode toggle (two radio buttons or a segmented control:
"Enter as packs" / "Enter as loose units"). When "packs" is selected, show
a `packs` number input and a **live-calculated** read-only "= N units"
line (JS: `packs × selectedMedicine.pack_size`); when "units", show the
existing raw `quantity` input as today. The medicine `<select>` needs
`data-pack-size="{{ med.pack_size }}"` and `data-unit="{{ med.unit }}"` on
each `<option>` so the JS can look up the right multiplier on selection.
Submit whichever input is visible under its existing `name` (`quantity` or
`packs`) plus a hidden `entry_mode` field reflecting the toggle state.

**(f) Transaction modal (`#transactionModal`, ~line 5996)**
Same toggle as (e). The trigger button already calls
`openTransactionModal(stockId, medName, batchNo)` — extend this call (in
the Stocks & Batches table row, ~line 2671) to also pass `pack_size` and
`unit`:
```html
onclick="openTransactionModal('{{ stock.id }}', '{{ stock.medicine.name|escapejs }}', '{{ stock.batch_number|escapejs }}', {{ stock.medicine.pack_size }}, '{{ stock.medicine.unit|escapejs }}')"
```
and update the JS function signature accordingly to populate the toggle's
multiplier for that stock's medicine.

### 2.4 Gap found during design review — Edit Medicine

There is currently **no way to edit an existing `Medicine`** — the catalog
table only has Delete, not Edit, even though `admin_medicine_save` already
branches on `medicine_id` and fully supports updates. Without this:
- Every medicine already in the catalog is permanently stuck at
  `pack_size = 1` (today's default), since there's no path to ever set it
  after creation.
- The tempting workaround — delete and re-add — is **destructive**:
  `admin_medicine_delete` cascades onto `MedicineStock` *and*
  `PrescribedMedicine`, meaning real prescription history would be lost
  just to fix a pack size.

**Required for Feature B to actually be usable on existing data.** Add:
- An "Edit" button per row in the catalog table (~line 2619), next to the
  existing Delete link, e.g. `data-bs-toggle="modal"
  data-bs-target="#medicineModal"` plus an `onclick="editMedicine({...})"`
  that populates the same `#medicineModal` fields (including the new
  `pack_size` input) and sets a hidden `medicine_id` field so the existing
  create/update branch in `admin_medicine_save` is hit correctly. Modal
  title should read "Edit Medicine" vs "Add Medicine" based on state (see
  existing pattern in the "Add/Edit Stock" modal handling if one exists,
  otherwise a simple `document.getElementById('medModalTitle').textContent = ...`
  toggle is sufficient).
- No new view or URL needed — `admin_medicine_save` already handles both
  paths; this is a template/JS-only change plus the `pack_size` field
  addition from §2.3(a).

### 2.5 Non-breaking checklist for Feature B

- [ ] `pack_size` defaults to `1` everywhere — confirm the derived
      `stock_display` on a `pack_size=1` medicine renders identically to
      today's plain `"{{ quantity }}"` (i.e., no behavior change for any
      medicine nobody has touched yet).
- [ ] Existing `admin_medicine_stock_save` / `admin_medicine_transaction_save`
      callers that still POST a raw `quantity` (no `entry_mode`) must keep
      working exactly as before — `entry_mode` defaults to `'units'`.
- [ ] Run `python manage.py check` after each template edit.

---

## 3. Feature C — Digital Prescription: Email + Downloadable PNG

**Status: designed and prototyped as a standalone HTML artifact (visual
reference only — [see the design preview](https://claude.ai/artifact/2N4YLQTCpwNN7AVNSJuS9r)).
Nothing here exists in the real app yet.** This section is the actual
build spec.

### 3.1 Data flow

```
doctor saves Add-History form (§1)
        ↓
save_medical_history() creates MedicalHistory + PrescribedMedicine rows
        ↓  (new, added in this phase)
if prescription_lines and appointment.email:
    render_prescription_png(history)   →  PNG bytes  (Pillow, server-side)
    send_prescription_email(history, appointment, png_bytes)
        ↓
student receives email with the PNG attached
        ↓ (optional, for re-download later)
student can also visit /prescription/<id>/  →  view page with a Download button
        →  GET /prescription/<id>/download/  →  same PNG, streamed
```

Both the emailed PNG and the on-demand download use the **same** render
function, so they're guaranteed to always look identical — one image, two
delivery paths.

### 3.2 New module — `app/prescription_render.py`

New file. Renders a `MedicalHistory` instance to PNG bytes using Pillow.

```python
import io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings

FONT_DIR = Path(settings.BASE_DIR) / "app" / "static" / "fonts"

def _font(weight: str, size: int) -> ImageFont.FreeTypeFont:
    """weight: 'regular' | 'semibold' | 'bold'"""
    path = FONT_DIR / f"Inter-{weight.capitalize()}.ttf"
    return ImageFont.truetype(str(path), size)

# Layout constants — 2x scale for a crisp, print-quality PNG.
CARD_W = 1600
MARGIN = 60
COLOR_PRIMARY = (74, 124, 89)      # #4a7c59
COLOR_PRIMARY_DARK = (46, 92, 58)  # #2e5c3a
COLOR_PAPER = (255, 254, 251)      # #fffefb
COLOR_BORDER = (221, 214, 196)     # #ddd6c4
COLOR_TEXT = (43, 43, 38)
COLOR_MUTED = (136, 136, 136)

def render_prescription_png(history) -> bytes:
    """
    Draws the prescription card (header band, patient/doctor info,
    diagnosis, one row per PrescribedMedicine with its schedule tags,
    advice footer, signature line) and returns PNG bytes.

    Height is computed dynamically from the number of medicine lines so
    the card never clips or leaves excess whitespace.
    """
    lines = list(history.prescribedmedicine_set.select_related("medicine").all())
    row_h = 140  # approx height per medicine row at this scale
    card_h = 520 + len(lines) * row_h  # header+info+diagnosis+footer + rows
    img = Image.new("RGB", (CARD_W, card_h), COLOR_PAPER)
    draw = ImageDraw.Draw(img)

    # 1. Header band (solid color — no gradient, keeps Pillow code simple
    #    and reliable; visually close enough to the HTML artifact's gradient).
    draw.rectangle([0, 0, CARD_W, 130], fill=COLOR_PRIMARY_DARK)
    draw.text((MARGIN, 35), "AUdoc", font=_font("bold", 44), fill="white")
    draw.text((MARGIN, 85), "Assam University Silchar · Student Health Center",
               font=_font("regular", 20), fill=(230, 240, 233))

    # 2. Prescription ID / date strip
    rx_id = f"RX-{history.id:06d}"
    y = 150
    draw.text((MARGIN, y), rx_id, font=_font("semibold", 20), fill=COLOR_MUTED)
    issued = history.created_at.strftime("%d %b %Y")
    draw.text((CARD_W - MARGIN - 260, y), f"Issued {issued}",
               font=_font("regular", 20), fill=COLOR_MUTED)

    # 3. Patient / doctor two-column block, diagnosis block — see the
    #    artifact for exact copy/labels to match; omit doctor reg. no.
    #    (not a stored field — see §0 table) and doctor specialization
    #    unless a best-effort Doctor lookup by name succeeds.
    # ... (label/value pairs drawn with _font("regular", 18) labels,
    #      _font("semibold", 24) values, same layout as the artifact)

    # 4. One row per PrescribedMedicine:
    #    name (semibold 26) + dosage (regular 20, muted)
    #    then a line of pill-style tags: schedule slots, food_timing,
    #    "{duration_days} days", "Qty {quantity}" — draw each as a
    #    rounded_rectangle (Pillow ≥8.2 supports draw.rounded_rectangle)
    #    filled COLOR_PRIMARY-tinted background with white/dark text.
    #    If pm.instructions is set, draw it below in italic-styled muted text
    #    (Pillow has no italic synthesis — use a slightly smaller regular
    #    weight in COLOR_MUTED with a "Note: " prefix instead).

    # 5. Advice footer band + doctor name signature line + small
    #    "Digitally generated — valid without a physical signature" caption.

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
```

This is a structural skeleton, not final pixel-pushed code — implementer
should match the visual layout already approved in the artifact (link
above) rather than re-litigate the design. Keep the header **solid color**,
not a gradient — Pillow gradients are extra code for a difference nobody
will notice in a downloaded PNG.

### 3.2.1 Font asset — action required before this can ship

No fonts are bundled in the repo today (§0). Download the **Inter** family
(SIL Open Font License — free to redistribute) and commit exactly these
three files:

```
app/static/fonts/Inter-Regular.ttf
app/static/fonts/Inter-SemiBold.ttf
app/static/fonts/Inter-Bold.ttf
```

If `Inter-*.ttf` is missing at render time, `ImageFont.truetype()` raises
`OSError` — wrap the render call (see §3.4) so this fails safe rather than
breaking the doctor's save action.

### 3.3 New URL + view — on-demand / re-download

`app/urls.py`:
```python
path("prescription/<int:history_id>/", views.view_prescription, name="view_prescription"),
path("prescription/<int:history_id>/download/", views.download_prescription_png, name="download_prescription_png"),
```

`app/views.py`:
```python
from django.http import Http404, HttpResponse
from .prescription_render import render_prescription_png

def _can_view_prescription(request, history):
    if not request.user.is_authenticated:
        return False
    if request.user.is_staff or request.user.is_superuser:
        return True
    profile = getattr(request.user, "student_profile", None)
    return bool(profile and profile.student_id == history.student_id)

@login_required
def view_prescription(request, history_id):
    history = get_object_or_404(MedicalHistory, pk=history_id)
    if not _can_view_prescription(request, history):
        raise Http404()   # 404, not 403 — don't confirm the record exists
    return render(request, "app/prescription_view.html", {
        "history": history,
        "rx_id": f"RX-{history.id:06d}",
        "lines": history.prescribedmedicine_set.select_related("medicine").all(),
    })

@login_required
def download_prescription_png(request, history_id):
    history = get_object_or_404(MedicalHistory, pk=history_id)
    if not _can_view_prescription(request, history):
        raise Http404()
    try:
        png_bytes = render_prescription_png(history)
    except Exception as e:
        logger.error(f"Prescription PNG render failed for history {history_id}: {e}")
        raise Http404()
    response = HttpResponse(png_bytes, content_type="image/png")
    response["Content-Disposition"] = f'attachment; filename="Prescription_RX-{history.id:06d}.png"'
    return response
```

**Security note — deliberate design choice:** both views return `Http404`
(not `HttpResponseForbidden`) for an unauthorized viewer, so a student
cannot distinguish "this prescription ID doesn't exist" from "it exists but
isn't yours" — standard practice for PHI-adjacent records to avoid
existence-leaking via probing sequential IDs.

`app/templates/app/prescription_view.html` — new template: the same visual
card as the artifact (can reuse its CSS almost verbatim), with a
"Download as PNG" button pointing at `{% url 'download_prescription_png' history.id %}`
as a plain link (no JS needed in production — the server already generates
the exact PNG; the `html2canvas` approach used in the **preview artifact**
was a client-side convenience for testing only and should not be carried
into the production page).

### 3.4 Email sending — hook into `save_medical_history`

Add at the end of `save_medical_history`, after the `PrescribedMedicine`
loop and appointment-status update, guarded so a rendering/email failure
**never** blocks the doctor's save (matches this codebase's existing
`try/except` + `logger.error(...)` convention used everywhere else):

```python
if prescription_lines and appointment.email:
    try:
        send_prescription_email(history, appointment)
    except Exception as e:
        logger.error(f"Failed to send prescription email for history {history.id}: {e}")
        # Deliberately not re-raised — the prescription is already saved;
        # a failed email must not undo or block that.
```

New function, alongside the other `send_*_email` functions in `app/views.py`
(same file/section as `send_staff_welcome_email` etc., to match existing
organization):

```python
def send_prescription_email(history, appointment):
    from .prescription_render import render_prescription_png
    png_bytes = render_prescription_png(history)
    rx_id = f"RX-{history.id:06d}"

    plain_text = (
        f"Hi {appointment.student_name},\n\n"
        f"Your prescription from your visit with {history.doctor_name} is ready.\n"
        f"Diagnosis: {history.illness}\n\n"
        f"Your prescription is attached as {rx_id}.png — save it, print it, "
        f"or show it at any pharmacy.\n\n— AUdoc Health Center"
    )
    html_body = """<!-- same green-branded layout/footer convention as the
    other emails in this file (§0) — header band, one-line diagnosis
    summary, a 'View Full Prescription' button linking to
    view_prescription, and the standard footer block. See the approved
    design: https://claude.ai/artifact/2N4YLQTCpwNN7AVNSJuS9r for exact
    copy and layout to match. """

    msg = EmailMultiAlternatives(
        subject=f"Your Prescription is Ready — {history.doctor_name}",
        body=plain_text,
        from_email=None,
        to=[appointment.email],
    )
    msg.attach_alternative(html_body, "text/html")
    msg.attach(f"{rx_id}.png", png_bytes, "image/png")
    send_email_async(msg)
```

The "View Full Prescription" button in the HTML body should link to
`{settings-derived site base URL}` + `reverse('view_prescription', args=[history.id])`
— confirm how other emails in this codebase build absolute URLs (search
existing `donor_respond`/token-link emails for the pattern already in use,
e.g. a `SITE_BASE_URL` setting or `request.build_absolute_uri`) and reuse
that exact mechanism rather than introducing a new one.

### 3.5 What changes vs. what doesn't

| | |
|---|---|
| **Changes** | New file `prescription_render.py`; two new URLs/views; new template `prescription_view.html`; new fonts under `app/static/fonts/`; one new function + one new call site (guarded, non-blocking) inside `save_medical_history`. |
| **Does not change** | `PrescribedMedicine`/`MedicalHistory` models (§1, already correct and sufficient); stock deduction logic (§1.2, unaffected); anything in Feature B. |

### 3.6 Non-breaking checklist for Feature C

- [ ] Wrap `render_prescription_png` and `send_prescription_email` calls in
      `try/except` at the call site — a bug here must never prevent a
      medical history from saving.
- [ ] Confirm `Inter-*.ttf` files are actually committed before deploying —
      a missing font file is a silent, easy-to-miss failure mode caught
      only by the try/except above (logged, not surfaced to the doctor).
- [ ] `download_prescription_png` / `view_prescription` must 404 (not 403,
      not 500) for any unauthorized request — write a test asserting this
      explicitly (see §4).
- [ ] Verify `EmailMultiAlternatives.attach()` (binary PNG attachment)
      works through both `app/resend_backend.py` and
      `app/sendgrid_backend.py` — inspect both files before assuming
      attachments pass through; if either backend strips attachments,
      that must be fixed there rather than worked around here.

---

## 4. Suggested implementation order

```
1. Feature A  — verify/port already-built code into the live repo (§1.8)
2. Feature B  — template/JS work + Edit Medicine (§2.3, §2.4); independent
                of A and C, can happen in parallel
3. Feature C  — depends on Feature A's data model; do last
```

## 5. Testing plan

- **Feature A:** `app/tests_prescription.py` already exists — run it, keep
  it green.
- **Feature B (new):** add `app/tests_stock.py` covering: creating a
  medicine with `pack_size=10` and adding stock via `entry_mode='packs'`
  results in the correct raw `quantity`; `entry_mode='units'` still works
  unmodified; `stock_display`/`packs_and_loose` produce correct output for
  both `pack_size=1` and `pack_size>1`; editing an existing medicine
  updates `pack_size` without touching its stock batches.
- **Feature C (new):** add `app/tests_digital_prescription.py` covering:
  `render_prescription_png` returns valid PNG bytes (assert via
  `PIL.Image.open(io.BytesIO(result)).verify()`) for a history with 1 and
  with 3 medicine lines; `download_prescription_png` returns 404 for an
  unauthenticated request, 404 for a different student's session, 200 for
  the owning student, 200 for staff; `save_medical_history` still succeeds
  and still returns its normal redirect even when
  `render_prescription_png` is mocked to raise (regression test for the
  "must not block the save" requirement in §3.6).
- Run `python manage.py check` after every phase, not just at the end.

---

## 6. Appendix — issues found during this design review (not in original scope)

- **`MedicalHistory.__str__` is broken.** It references
  `self.appointment.student_name`, but `MedicalHistory` has no
  `appointment` field/relation — this will raise `AttributeError` the
  moment anything calls `str(history)` (e.g. Django's default admin list
  display, or debug logging). Low effort, high value fix while a
  contributor is already in this model:
  ```python
  def __str__(self):
      return f"History for {self.student_id} — {self.illness} ({self.appointment_date})"
  ```
- **No "Edit Medicine" UI** — covered in full as a required part of §2.4;
  listed here too since it was discovered, not requested, and is easy to
  lose track of in a long plan.
