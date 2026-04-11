"""
Management command to send appointment reminders.

This command sends two types of reminders:
1. 24-hour email reminder (morning before appointment day)
2. 2-hour SMS reminder (2 hours before appointment)

Run with cron jobs:
  # 24-hour reminders (runs daily at 8 PM)
  0 20 * * * python manage.py send_appointment_reminders --type 24h

  # 2-hour reminders (runs every day at 12 PM, 2 PM, 4 PM, etc.)
  0 */1 * * * python manage.py send_appointment_reminders --type 2h
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from datetime import date, timedelta, datetime, time
from app.models import Appointment
from app.sms_service import send_appointment_reminder
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Send appointment reminders (24-hour email and 2-hour SMS)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--type",
            type=str,
            choices=["24h", "2h", "all"],
            default="all",
            help="Type of reminder to send: 24h (email), 2h (SMS), or all",
        )

    def handle(self, *args, **options):
        reminder_type = options["type"]

        self.stdout.write(f"\n{'='*70}")
        self.stdout.write(f"Sending Appointment Reminders - Type: {reminder_type.upper()}")
        self.stdout.write(f"{'='*70}\n")

        if reminder_type in ["24h", "all"]:
            self._send_24h_reminders()

        if reminder_type in ["2h", "all"]:
            self._send_2h_reminders()

        self.stdout.write(f"\n{'='*70}")
        self.stdout.write(self.style.SUCCESS("Reminder sending completed"))
        self.stdout.write(f"{'='*70}\n")

    def _send_24h_reminders(self):
        """Send 24-hour email reminders"""
        self.stdout.write("\n🔔 Sending 24-hour reminders...\n")

        # Get appointments scheduled for tomorrow
        tomorrow = date.today() + timedelta(days=1)
        appointments = Appointment.objects.filter(
            appointment_date=tomorrow,
            status__in=["CONFIRMED", "PENDING"],
            reminder_24h_sent=False,
        ).select_related("doctor")

        if not appointments.exists():
            self.stdout.write(self.style.WARNING(f"No appointments found for {tomorrow}"))
            return

        sent_count = 0
        error_count = 0

        for appointment in appointments:
            try:
                self._send_24h_email(appointment)
                appointment.reminder_24h_sent = True
                appointment.reminder_24h_sent_at = timezone.now()
                appointment.save(update_fields=["reminder_24h_sent", "reminder_24h_sent_at"])

                sent_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✓ {appointment.student_name} ({appointment.student_id}) - 24h email sent"
                    )
                )
            except Exception as e:
                error_count += 1
                logger.error(f"Failed to send 24h reminder to {appointment.student_name}: {str(e)}")
                self.stdout.write(
                    self.style.ERROR(f"  ✗ {appointment.student_name} - Error: {str(e)}")
                )

        self.stdout.write(f"\n24h Reminders: {self.style.SUCCESS(f'{sent_count} sent')}, {self.style.ERROR(f'{error_count} failed')}")

    def _send_2h_reminders(self):
        """Send 2-hour SMS reminders"""
        self.stdout.write("\n📱 Sending 2-hour SMS reminders...\n")

        # Get appointments happening in the next 2-3 hours
        now = timezone.now()
        appointment_window_start = now + timedelta(hours=1, minutes=45)
        appointment_window_end = now + timedelta(hours=2, minutes=15)

        # Get appointments for today that fall in this time window
        today = date.today()
        appointments = Appointment.objects.filter(
            appointment_date=today,
            status__in=["CONFIRMED", "PENDING"],
            reminder_2h_sent=False,
        ).select_related("doctor")

        sent_count = 0
        error_count = 0

        for appointment in appointments:
            if appointment.appointment_time is None:
                continue

            # Parse appointment time and create datetime for today
            try:
                time_str = appointment.appointment_time
                # Parse time like "02:00 PM"
                appt_time = datetime.strptime(time_str, "%I:%M %p").time()
                appt_datetime = datetime.combine(today, appt_time)
                appt_datetime = timezone.make_aware(
                    appt_datetime,
                    timezone=settings.TZ if hasattr(settings, "TZ") else timezone.get_current_timezone(),
                )

                # Check if appointment is within 2-hour window
                if appointment_window_start <= appt_datetime <= appointment_window_end:
                    if send_appointment_reminder(
                        phone_number=appointment.phone,
                        student_name=appointment.student_name,
                        appointment_date=appointment.appointment_date.strftime("%B %d"),
                        appointment_time=appointment.appointment_time,
                        hours_remaining=2,
                    ):
                        appointment.reminder_2h_sent = True
                        appointment.reminder_2h_sent_at = timezone.now()
                        appointment.save(update_fields=["reminder_2h_sent", "reminder_2h_sent_at"])

                        sent_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"  ✓ {appointment.student_name} - 2h SMS sent to {appointment.phone}"
                            )
                        )
                    else:
                        error_count += 1
                        self.stdout.write(
                            self.style.ERROR(f"  ✗ {appointment.student_name} - SMS failed")
                        )

            except Exception as e:
                error_count += 1
                logger.error(f"Error processing 2h reminder for {appointment.student_name}: {str(e)}")
                self.stdout.write(
                    self.style.ERROR(f"  ✗ {appointment.student_name} - Error: {str(e)}")
                )

        self.stdout.write(f"\n2h Reminders: {self.style.SUCCESS(f'{sent_count} sent')}, {self.style.ERROR(f'{error_count} failed')}")

    def _send_24h_email(self, appointment):
        """Send 24-hour reminder email"""
        base_url = getattr(settings, "SITE_URL", "http://localhost:8000")

        subject = f"[AUdoc] 📅 Appointment Reminder - {appointment.appointment_date.strftime('%B %d, %Y')}"

        # Plain text version
        text_content = f"""
Dear {appointment.student_name},

This is a reminder about your upcoming appointment with AUdoc Campus Health Center:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Appointment Details
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Patient Name: {appointment.student_name}
Student ID: {appointment.student_id}
Department: {appointment.get_medical_department_display()}
{"Doctor: " + appointment.doctor.name if appointment.doctor else "Doctor: To be assigned"}
Date: {appointment.appointment_date.strftime('%A, %B %d, %Y')}
Time: {appointment.appointment_time}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 Please arrive 10 minutes early.

If you need to reschedule or cancel, please contact us as soon as possible.

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
    .content {{ padding: 32px 24px; }}
    .info-box {{ background: #f8f9fa; border-radius: 10px; padding: 20px; margin-bottom: 24px; }}
    .info-row {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #e8f5ec; }}
    .info-row:last-child {{ border-bottom: none; }}
    .info-label {{ color: #666; font-weight: 600; font-size: 0.9rem; }}
    .info-value {{ color: #1a3a25; font-weight: 700; text-align: right; }}
    .footer {{ background: #f8f9fa; padding: 20px 24px; text-align: center; font-size: 0.85rem; color: #666; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>📅 Appointment Reminder</h1>
      <p>Your appointment is coming up tomorrow</p>
    </div>
    <div class="content">
      <p style="font-size:1rem;color:#333;margin-bottom:20px;">Dear <strong>{appointment.student_name}</strong>,</p>

      <p style="font-size:0.95rem;color:#555;">This is a reminder about your upcoming appointment:</p>

      <div class="info-box">
        <div class="info-row">
          <span class="info-label">Date</span>
          <span class="info-value">{appointment.appointment_date.strftime('%A, %B %d, %Y')}</span>
        </div>
        <div class="info-row">
          <span class="info-label">Time</span>
          <span class="info-value">{appointment.appointment_time}</span>
        </div>
        <div class="info-row">
          <span class="info-label">Department</span>
          <span class="info-value">{appointment.get_medical_department_display()}</span>
        </div>
        <div class="info-row">
          <span class="info-label">Doctor</span>
          <span class="info-value">{"" + appointment.doctor.name if appointment.doctor else "To be assigned"}</span>
        </div>
      </div>

      <div style="background:#e8f5ec;padding:16px;border-radius:8px;font-size:0.9rem;color:#2e5c3a;">
        <strong>📍 Important:</strong>
        <ul style="margin:8px 0 0;padding-left:20px;">
          <li>Please arrive 10 minutes early</li>
          <li>Bring a valid ID and any medical documents</li>
          <li>If you need to cancel, please contact us immediately</li>
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
