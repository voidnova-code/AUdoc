"""
Management command to clean up old TodaysAppointment records.

Run this with a cron job at midnight daily to remove yesterday's data:
    python manage.py cleanup_todays_appointments
"""
from django.core.management.base import BaseCommand
from datetime import date
from app.models import TodaysAppointment


class Command(BaseCommand):
    help = 'Clean up old TodaysAppointment records (keeps only today\'s data)'

    def handle(self, *args, **options):
        today = date.today()
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"Cleaning up TodaysAppointment records older than {today}")
        self.stdout.write(f"{'='*60}\n")

        # Delete all records where appointment_date is not today
        deleted = TodaysAppointment.objects.exclude(
            appointment__appointment_date=today
        ).delete()

        deleted_count = deleted[0]

        if deleted_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f"[SUCCESS] Deleted {deleted_count} old appointment records")
            )
        else:
            self.stdout.write(
                self.style.WARNING("No old records to delete")
            )

        # Show current count
        current_count = TodaysAppointment.objects.count()
        self.stdout.write(
            self.style.SUCCESS(f"\n[SUCCESS] Current TodaysAppointment records: {current_count}")
        )

        self.stdout.write(f"{'='*60}\n")
