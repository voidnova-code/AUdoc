from django.core.management.base import BaseCommand
from app.models import Appointment, TodaysAppointment
from datetime import date
from django.utils import timezone


class Command(BaseCommand):
    help = (
        "Auto-cancel all PENDING appointments for today. "
        "Run this at 10:00 AM IST to clean up unconfirmed appointments "
        "so the today's list only shows confirmed patients."
    )

    def handle(self, *args, **options):
        today = date.today()

        pending_qs = TodaysAppointment.objects.filter(
            status="PENDING",
            appointment__appointment_date=today,
        ).select_related("appointment")

        count = 0
        for today_appt in pending_qs:
            today_appt.status = "DECLINED"
            today_appt.save(update_fields=["status"])

            today_appt.appointment.status = "DECLINED"
            today_appt.appointment.save(update_fields=["status"])
            count += 1

        if count:
            self.stdout.write(self.style.WARNING(
                f"Auto-cancelled {count} unconfirmed appointment(s) for {today}."
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"No pending appointments to cancel for {today}."
            ))
