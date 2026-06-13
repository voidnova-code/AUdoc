from django.core.management.base import BaseCommand
from app.models import Appointment, TodaysAppointment
from datetime import date
from django.core.mail import EmailMultiAlternatives
from app.views import send_email_async
from django.urls import reverse
from django.conf import settings

class Command(BaseCommand):
    help = 'Send email confirmations for PENDING appointments scheduled for today.'

    def handle(self, *args, **options):
        today = date.today()
        # Find all PENDING appointments for today AND any missed past days
        # This catches appointments that were missed if the scheduler didn't fire
        appointments = Appointment.objects.filter(appointment_date__lte=today, status="PENDING")
        
        count = 0
        from django.utils import timezone
        for appt in appointments:
            # Create TodaysAppointment to generate confirmation token
            defaults = {
                "status": "PENDING",
                "email_sent_at": timezone.now(),
                "response_deadline": timezone.now() + timezone.timedelta(hours=4)
            }
            today_appt, created = TodaysAppointment.objects.get_or_create(
                appointment=appt,
                defaults=defaults
            )
            
            if not created and today_appt.status != "PENDING":
                continue # Already responded or expired
                
            # Send Email
            self.send_confirmation_email(appt, today_appt.confirmation_token)
            count += 1
            
        self.stdout.write(self.style.SUCCESS(f"Successfully sent {count} confirmation emails."))

    def send_confirmation_email(self, appt, token):
        # We need a domain. In commands, request is not available.
        # Fallback to localhost for demo purposes if SITE_URL is not set.
        domain = getattr(settings, "SITE_URL", "http://127.0.0.1:8000")
        
        accept_url = f"{domain}{reverse('appointment_confirm', args=[str(token), 'accept'])}"
        decline_url = f"{domain}{reverse('appointment_confirm', args=[str(token), 'decline'])}"
        
        doctor_str = f" with Dr. {appt.doctor.name}" if appt.doctor else ""
        
        plain_text = (
            f"Dear {appt.student_name},\n\n"
            f"You have an appointment booked for today{doctor_str}.\n"
            f"Please confirm if you will be attending.\n\n"
            f"To ACCEPT : {accept_url}\n"
            f"To DECLINE : {decline_url}\n\n"
            "If you do not accept, your appointment will be cancelled.\n\n"
            "-- AUdoc Campus Health"
        )
        
        msg = EmailMultiAlternatives(
            subject="[AUdoc] Today's Appointment Confirmation Required",
            body=plain_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[appt.email],
        )
        # Using send() directly instead of send_email_async in a cron context to avoid thread issues,
        # but since we import send_email_async we can just use it or msg.send().
        msg.send()
