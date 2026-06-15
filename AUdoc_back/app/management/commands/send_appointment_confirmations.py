from django.core.management.base import BaseCommand
from app.models import Appointment, TodaysAppointment
from datetime import date, timedelta
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.conf import settings
from django.utils import timezone


def expire_pending_confirmations():
    """
    Auto-expire any TodaysAppointment records whose response_deadline has passed
    and the student hasn't responded. Marks them as EXPIRED and cancels the
    underlying appointment so they are NOT added to the FCFS queue.

    Returns the number of expired confirmations.
    """
    now = timezone.now()
    expired_qs = TodaysAppointment.objects.filter(
        status="PENDING",
        response_deadline__lt=now,
    ).select_related("appointment")

    count = 0
    for today_appt in expired_qs:
        today_appt.status = "EXPIRED"
        today_appt.save(update_fields=["status"])

        # Cancel the main appointment — student did not confirm in time
        today_appt.appointment.status = "CANCELLED"
        today_appt.appointment.save(update_fields=["status"])
        count += 1

    return count


class Command(BaseCommand):
    help = (
        "Send email confirmations for PENDING appointments scheduled for today "
        "and auto-expire unresponsive ones."
    )

    def handle(self, *args, **options):
        # ── Step 1: Auto-expire past-deadline confirmations ──────────────
        expired_count = expire_pending_confirmations()
        if expired_count:
            self.stdout.write(self.style.WARNING(
                f"Auto-expired {expired_count} unconfirmed appointment(s)."
            ))

        # ── Step 2: Send confirmations for today's pending appointments ──
        today = date.today()
        appointments = Appointment.objects.filter(
            appointment_date__lte=today,
            status="PENDING",
        )

        count = 0
        for appt in appointments:
            defaults = {
                "status": "PENDING",
                "email_sent_at": timezone.now(),
                "response_deadline": timezone.now() + timedelta(hours=4),
            }
            today_appt, created = TodaysAppointment.objects.get_or_create(
                appointment=appt,
                defaults=defaults,
            )

            if not created and today_appt.status != "PENDING":
                continue  # Already responded or expired

            self.send_confirmation_email(appt, today_appt.confirmation_token)
            count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Successfully sent {count} confirmation email(s)."
        ))

    def send_confirmation_email(self, appt, token):
        """Send a beautifully styled confirmation email for a single appointment."""
        domain = getattr(settings, "SITE_URL", "http://127.0.0.1:8000")

        accept_url = f"{domain}{reverse('appointment_confirm', args=[str(token), 'accept'])}"
        decline_url = f"{domain}{reverse('appointment_confirm', args=[str(token), 'decline'])}"

        doctor_name = appt.doctor.name if appt.doctor else "Any Available Doctor"
        doctor_str = f" with Dr. {appt.doctor.name}" if appt.doctor else ""
        doctor_str_html = (
            f' with <strong style="color:#1a5c96;">Dr. {appt.doctor.name}</strong>'
            if appt.doctor else ""
        )
        department_display = appt.get_medical_department_display()
        date_display = (
            appt.appointment_date.strftime("%A, %B %d, %Y")
            if appt.appointment_date else "Today"
        )
        time_display = appt.appointment_time or "To be assigned"

        # Use verified domain sender — never fall back to resend.dev
        from_email = settings.DEFAULT_FROM_EMAIL
        if not from_email or "resend.dev" in str(from_email):
            from_email = "AUdoc Campus Health <noreply@voiddoc.me>"

        self.stdout.write(
            f"  → Sending to {appt.email} | from: {from_email} | domain: {domain}"
        )

        # ── Plain-text fallback ──────────────────────────────────────────
        plain_text = (
            f"Dear {appt.student_name},\n\n"
            f"You have an appointment booked for {date_display}{doctor_str}.\n"
            f"Department: {department_display}\n"
            f"Time Slot: {time_display}\n\n"
            f"Please confirm if you will be attending within the next 4 hours.\n\n"
            f"To ACCEPT  : {accept_url}\n"
            f"To DECLINE : {decline_url}\n\n"
            f"⚠️ IMPORTANT: If you do not respond within 4 hours, your appointment\n"
            f"will be automatically cancelled and you will NOT be added to today's\n"
            f"queue.\n\n"
            f"How FCFS Works: Once you confirm, you'll be assigned a queue position\n"
            f"based on when you responded. The earlier you confirm, the earlier\n"
            f"you'll be seen!\n\n"
            "-- AUdoc Campus Health\n"
            "Academic Block C, Room 101 | health@au.edu"
        )

        # ── Rich HTML email ──────────────────────────────────────────────
        html_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
</head>
<body style="margin:0;padding:0;background:#e8f0fe;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#e8f0fe;padding:40px 0;">
    <tr><td align="center">
      <table width="560" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:20px;overflow:hidden;box-shadow:0 8px 32px rgba(26,92,150,.18);">

        <!-- ═══ Header ═══ -->
        <tr>
          <td style="background:linear-gradient(135deg,#1a5c96 0%,#134a7a 100%);padding:36px 40px;text-align:center;">
            <div style="display:inline-block;background:rgba(255,255,255,.15);border-radius:14px;padding:12px 18px;margin-bottom:14px;">
              <span style="font-size:2rem;">&#128197;</span>
            </div>
            <h1 style="margin:0;color:#ffffff;font-size:1.6rem;font-weight:700;letter-spacing:-.5px;">Appointment Confirmation</h1>
            <p style="margin:6px 0 0;color:#c0d8f0;font-size:.9rem;">AUdoc Campus Health &mdash; Assam University</p>
          </td>
        </tr>

        <!-- ═══ Body ═══ -->
        <tr>
          <td style="padding:40px 40px 32px;">
            <p style="margin:0 0 8px;font-size:1.5rem;">&#128075; Dear {appt.student_name},</p>
            <p style="margin:0 0 24px;color:#555;font-size:.97rem;line-height:1.6;">
              You have an appointment scheduled for
              <strong style="color:#1a5c96;">today</strong>{doctor_str_html}.
              Please confirm whether you&rsquo;ll be attending so we can assign your
              queue position.
            </p>

            <!-- ─── Appointment Details Card ─── -->
            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;background:#eef4ff;border-radius:12px;overflow:hidden;border:1px solid #ccdcf0;">
              <tr><td style="padding:20px 24px;">
                <p style="margin:0 0 14px;font-size:.78rem;text-transform:uppercase;letter-spacing:2px;color:#1a5c96;font-weight:700;">Your Appointment Details</p>
                <table width="100%" cellpadding="5" cellspacing="0">
                  <tr>
                    <td style="font-size:.85rem;color:#888;width:38%;">&#128197; Date</td>
                    <td style="font-size:.92rem;color:#333;font-weight:600;">{date_display}</td>
                  </tr>
                  <tr>
                    <td style="font-size:.85rem;color:#888;">&#128336; Time Slot</td>
                    <td style="font-size:.92rem;color:#333;font-weight:600;">{time_display}</td>
                  </tr>
                  <tr>
                    <td style="font-size:.85rem;color:#888;">&#129658; Doctor</td>
                    <td style="font-size:.92rem;color:#333;font-weight:600;">{doctor_name}</td>
                  </tr>
                  <tr>
                    <td style="font-size:.85rem;color:#888;">&#127973; Department</td>
                    <td><span style="background:#1a5c96;color:#fff;padding:3px 12px;border-radius:20px;font-size:.85rem;font-weight:700;">{department_display}</span></td>
                  </tr>
                </table>
              </td></tr>
            </table>

            <!-- ─── Accept / Decline Buttons ─── -->
            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
              <tr>
                <td align="center" style="padding-right:8px;">
                  <a href="{accept_url}"
                     style="display:inline-block;background:linear-gradient(135deg,#27ae60,#1e8449);color:#fff;text-decoration:none;padding:14px 32px;border-radius:50px;font-size:1rem;font-weight:700;letter-spacing:.3px;">
                    &#10003;&nbsp; I'll Be There
                  </a>
                </td>
                <td align="center" style="padding-left:8px;">
                  <a href="{decline_url}"
                     style="display:inline-block;background:#f8f9fa;color:#555;text-decoration:none;padding:14px 32px;border-radius:50px;font-size:1rem;font-weight:700;border:2px solid #dee2e6;">
                    &#10007;&nbsp; Can't Make It
                  </a>
                </td>
              </tr>
            </table>

            <!-- ─── 4-Hour Deadline Warning ─── -->
            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:20px;">
              <tr>
                <td style="background:#fff3cd;border-left:4px solid #f9a825;border-radius:0 10px 10px 0;padding:14px 16px;">
                  <p style="margin:0;font-size:.88rem;color:#7a5800;line-height:1.5;">
                    &#9200; <strong>You have 4 hours to respond.</strong>
                    If you don&rsquo;t confirm within this window, your appointment
                    will be <strong>automatically cancelled</strong> and you will
                    not be added to today&rsquo;s queue. Better click fast! &#127939;
                  </p>
                </td>
              </tr>
            </table>

            <!-- ─── FCFS Info Note ─── -->
            <table width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="background:#e8f5e9;border-left:4px solid #27ae60;border-radius:0 10px 10px 0;padding:14px 16px;">
                  <p style="margin:0;font-size:.85rem;color:#1b5e20;line-height:1.5;">
                    &#128161; <strong>How it works:</strong> Once you confirm,
                    you&rsquo;ll be assigned a queue position based on when you
                    respond (first-come, first-served). The earlier you confirm,
                    the earlier you&rsquo;ll be seen!
                  </p>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- ═══ Footer ═══ -->
        <tr>
          <td style="background:#f4f8fc;padding:20px 40px;text-align:center;border-top:1px solid #e5edf5;">
            <p style="margin:0;font-size:.8rem;color:#999;">
              &#169; 2026 <strong style="color:#1a5c96;">AUdoc</strong> &mdash;
              Assam University Silchar Campus Health<br/>
              Academic Block C, Room 101 &nbsp;|&nbsp; health@au.edu
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""

        msg = EmailMultiAlternatives(
            subject="[AUdoc] ✅ Confirm Your Appointment Today",
            body=plain_text,
            from_email=from_email,
            to=[appt.email],
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send()
