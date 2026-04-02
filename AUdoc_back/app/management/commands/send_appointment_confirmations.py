"""
Management command to send appointment confirmation emails at 8 AM.

Run this with a cron job or task scheduler at 8:00 AM daily:
    python manage.py send_appointment_confirmations
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from datetime import date, timedelta
from app.models import Appointment, TodaysAppointment


class Command(BaseCommand):
    help = 'Send appointment confirmation emails to patients with appointments today'

    def handle(self, *args, **options):
        today = date.today()
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"Sending appointment confirmations for {today}")
        self.stdout.write(f"{'='*60}\n")

        # Get all PENDING appointments scheduled for today
        appointments = Appointment.objects.filter(
            appointment_date=today,
            status='PENDING'
        ).select_related('doctor')

        if not appointments.exists():
            self.stdout.write(self.style.WARNING(f"No pending appointments found for {today}"))
            return

        sent_count = 0
        error_count = 0

        for appointment in appointments:
            # Check if TodaysAppointment already exists for this appointment
            if TodaysAppointment.objects.filter(appointment=appointment).exists():
                self.stdout.write(
                    self.style.WARNING(
                        f"  [WARNING] Already sent: {appointment.student_name} ({appointment.student_id})"
                    )
                )
                continue

            # Create TodaysAppointment record with 2-hour deadline
            response_deadline = timezone.now() + timedelta(hours=2)
            today_appt = TodaysAppointment.objects.create(
                appointment=appointment,
                email_sent_at=timezone.now(),
                response_deadline=response_deadline,
                status='PENDING'
            )

            # Send confirmation email
            try:
                self._send_confirmation_email(appointment, today_appt)
                sent_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  [SUCCESS] Sent: {appointment.student_name} ({appointment.student_id}) - "
                        f"Deadline: {response_deadline.strftime('%I:%M %p')}"
                    )
                )
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"  [FAILED] Failed: {appointment.student_name} ({appointment.student_id}) - {str(e)}"
                    )
                )

        # Cleanup expired pending confirmations
        self._cleanup_expired()

        # Summary
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(self.style.SUCCESS(f"[SUCCESS] Successfully sent: {sent_count}"))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f"[FAILED] Failed: {error_count}"))
        self.stdout.write(f"{'='*60}\n")

    def _send_confirmation_email(self, appointment, today_appt):
        """Send the confirmation email to the patient"""
        base_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        accept_url = f"{base_url}/appointment/confirm/{today_appt.confirmation_token}/accept/"
        decline_url = f"{base_url}/appointment/confirm/{today_appt.confirmation_token}/decline/"

        subject = f"[AUdoc] ⏰ Appointment Confirmation Required - {appointment.appointment_date}"

        # Plain text version
        text_content = f"""
Dear {appointment.student_name},

You have an appointment scheduled with AUdoc Campus Health Center:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Appointment Details
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Patient Name: {appointment.student_name}
Student ID: {appointment.student_id}
Department: {appointment.get_medical_department_display()}
{"Doctor: " + appointment.doctor.name if appointment.doctor else ""}
Date: {appointment.appointment_date.strftime('%A, %B %d, %Y')}
Time: {appointment.appointment_time}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ IMPORTANT: You must confirm or decline this appointment within 2 hours.

Deadline: {today_appt.response_deadline.strftime('%I:%M %p')}

Please click one of the links below:

✓ CONFIRM APPOINTMENT:
{accept_url}

✗ DECLINE APPOINTMENT:
{decline_url}

If you confirm, you will be assigned a queue position on a First Come, First Serve (FCFS) basis.

If you decline or do not respond within 2 hours, your appointment will be automatically cancelled.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Best regards,
AUdoc Campus Health Center
Assam University, Silchar
        """

        # HTML version
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
  <style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f4f8f5; margin: 0; padding: 20px; }}
    .container {{ max-width: 600px; margin: 0 auto; background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
    .header {{ background: linear-gradient(135deg, #4a7c59, #2e5c3a); color: #fff; padding: 30px 24px; text-align: center; }}
    .header h1 {{ margin: 0; font-size: 1.8rem; }}
    .header p {{ margin: 8px 0 0; opacity: 0.9; font-size: 0.95rem; }}
    .content {{ padding: 32px 24px; }}
    .alert {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 16px; margin-bottom: 24px; border-radius: 6px; }}
    .alert strong {{ color: #856404; }}
    .info-box {{ background: #f8f9fa; border-radius: 10px; padding: 20px; margin-bottom: 24px; }}
    .info-row {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #e8f5ec; }}
    .info-row:last-child {{ border-bottom: none; }}
    .info-label {{ color: #666; font-weight: 600; font-size: 0.9rem; }}
    .info-value {{ color: #1a3a25; font-weight: 700; text-align: right; }}
    .buttons {{ text-align: center; margin: 32px 0; }}
    .btn {{ display: inline-block; padding: 14px 32px; margin: 8px; text-decoration: none; border-radius: 8px; font-weight: 700; font-size: 1rem; }}
    .btn-accept {{ background: #4a7c59; color: #fff; }}
    .btn-decline {{ background: #c41e3a; color: #fff; }}
    .footer {{ background: #f8f9fa; padding: 20px 24px; text-align: center; font-size: 0.85rem; color: #666; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>⏰ Appointment Confirmation Required</h1>
      <p>Action needed within 2 hours</p>
    </div>
    <div class="content">
      <div class="alert">
        <strong>⚠️ IMPORTANT:</strong> You must confirm or decline within 2 hours.<br>
        <strong>Deadline:</strong> {today_appt.response_deadline.strftime('%I:%M %p')}
      </div>

      <p style="font-size:1rem;color:#333;margin-bottom:20px;">Dear <strong>{appointment.student_name}</strong>,</p>

      <p style="font-size:0.95rem;color:#555;">You have an appointment scheduled with AUdoc Campus Health Center today:</p>

      <div class="info-box">
        <div class="info-row">
          <span class="info-label">Patient Name</span>
          <span class="info-value">{appointment.student_name}</span>
        </div>
        <div class="info-row">
          <span class="info-label">Student ID</span>
          <span class="info-value">{appointment.student_id}</span>
        </div>
        <div class="info-row">
          <span class="info-label">Department</span>
          <span class="info-value">{appointment.get_medical_department_display()}</span>
        </div>
        {'<div class="info-row"><span class="info-label">Doctor</span><span class="info-value">' + appointment.doctor.name + '</span></div>' if appointment.doctor else ''}
        <div class="info-row">
          <span class="info-label">Date</span>
          <span class="info-value">{appointment.appointment_date.strftime('%A, %B %d, %Y')}</span>
        </div>
        <div class="info-row">
          <span class="info-label">Time</span>
          <span class="info-value">{appointment.appointment_time}</span>
        </div>
      </div>

      <div class="buttons">
        <a href="{accept_url}" class="btn btn-accept">✓ CONFIRM APPOINTMENT</a>
        <a href="{decline_url}" class="btn btn-decline">✗ DECLINE APPOINTMENT</a>
      </div>

      <div style="background:#e8f5ec;padding:16px;border-radius:8px;font-size:0.9rem;color:#2e5c3a;">
        <strong>📌 What happens next?</strong>
        <ul style="margin:8px 0 0;padding-left:20px;">
          <li>If you <strong>confirm</strong>, you'll be assigned a queue position (FCFS).</li>
          <li>If you <strong>decline</strong> or don't respond, your appointment will be cancelled.</li>
        </ul>
      </div>
    </div>
    <div class="footer">
      <p style="margin:0;"><strong>AUdoc Campus Health Center</strong></p>
      <p style="margin:4px 0 0;">Assam University, Silchar</p>
    </div>
  </div>
</body>
</html>
        """

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[appointment.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

    def _cleanup_expired(self):
        """Mark expired pending confirmations as EXPIRED and cancel appointments"""
        now = timezone.now()
        expired = TodaysAppointment.objects.filter(
            status='PENDING',
            response_deadline__lt=now
        ).select_related('appointment')

        expired_count = expired.count()
        if expired_count > 0:
            for ta in expired:
                ta.status = 'EXPIRED'
                ta.save(update_fields=['status'])

                # Cancel the appointment
                ta.appointment.status = 'CANCELLED'
                ta.appointment.save(update_fields=['status'])

            self.stdout.write(
                self.style.WARNING(f"\n[EXPIRED] Marked {expired_count} expired confirmations as CANCELLED")
            )
