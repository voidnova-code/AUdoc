from django.core.management.base import BaseCommand
from app.models import Appointment, TodaysAppointment
from datetime import date, timedelta


class Command(BaseCommand):
    help = (
        "Mark all unvisited (CONFIRMED) appointments in a specific shift "
        "as NO_SHOW. Run at shift end or automatically by the scheduler."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--shift",
            type=str,
            choices=["MORNING", "EVENING", "NIGHT", "ALL"],
            default="ALL",
            help="Which shift to clean up. Use ALL to clear every shift for yesterday.",
        )

    def handle(self, *args, **options):
        shift = options["shift"]
        today = date.today()

        if shift == "ALL":
            # Called by the nightly scheduler at 8 AM — clean the full previous day
            target_date = today - timedelta(days=1)
            shifts_to_clear = ["MORNING", "EVENING", "NIGHT"]
        elif shift == "NIGHT":
            # Night shift ends at 8 AM the following day, so target yesterday
            target_date = today - timedelta(days=1)
            shifts_to_clear = ["NIGHT"]
        else:
            target_date = today
            shifts_to_clear = [shift]

        total = 0
        for s in shifts_to_clear:
            qs = TodaysAppointment.objects.filter(
                appointment__shift=s,
                appointment__appointment_date=target_date,
                status="CONFIRMED",
            ).select_related("appointment")

            count = 0
            for ta in qs:
                ta.status = "NO_SHOW"
                ta.save(update_fields=["status"])
                ta.appointment.status = "NO_SHOW"
                ta.appointment.was_no_show = True
                ta.appointment.save(update_fields=["status", "was_no_show"])
                count += 1

            if count:
                self.stdout.write(self.style.SUCCESS(
                    "Marked {} unvisited student(s) from the {} shift on {} as NO_SHOW.".format(
                        count, s, target_date
                    )
                ))
            else:
                self.stdout.write("No unvisited students in {} shift on {}.".format(s, target_date))
            total += count

        self.stdout.write(self.style.SUCCESS(
            "Done. Total {} record(s) marked as NO_SHOW.".format(total)
        ))
