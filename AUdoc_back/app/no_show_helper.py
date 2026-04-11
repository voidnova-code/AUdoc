"""
Helper utilities for managing no-show tracking and restrictions.
"""
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from app.models import Appointment, StudentNoShowRecord


def mark_appointment_as_no_show(appointment_id: int, reason: str = "") -> bool:
    """
    Mark an appointment as no-show and update student's no-show record.

    Args:
        appointment_id: Appointment ID
        reason: Optional reason for no-show

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        appointment = Appointment.objects.get(id=appointment_id)

        # Mark appointment as no-show
        appointment.status = "NO_SHOW"
        appointment.was_no_show = True
        appointment.actual_completion_date = timezone.now()
        appointment.save(update_fields=["status", "was_no_show", "actual_completion_date"])

        # Update student no-show record
        from app.models import StudentProfile

        try:
            student_profile = StudentProfile.objects.get(student_id=appointment.student_id)
            no_show_record, created = StudentNoShowRecord.objects.get_or_create(
                student=student_profile
            )

            no_show_record.total_no_shows += 1
            no_show_record.last_no_show_date = timezone.now()

            # Check if threshold reached for restriction
            threshold = getattr(settings, "NO_SHOW_THRESHOLD", 3)
            if no_show_record.total_no_shows >= threshold:
                no_show_record.is_restricted = True
                restriction_days = getattr(settings, "NO_SHOW_RESTRICTION_DAYS", 30)
                no_show_record.restriction_until = (
                    timezone.now().date() + timedelta(days=restriction_days)
                )

            no_show_record.save()
            return True
        except StudentProfile.DoesNotExist:
            return False

    except Appointment.DoesNotExist:
        return False


def mark_appointment_as_completed(appointment_id: int) -> bool:
    """
    Mark an appointment as completed (patient showed up).

    Args:
        appointment_id: Appointment ID

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        appointment = Appointment.objects.get(id=appointment_id)

        appointment.status = "COMPLETED"
        appointment.was_no_show = False
        appointment.actual_completion_date = timezone.now()
        appointment.save(update_fields=["status", "was_no_show", "actual_completion_date"])

        return True
    except Appointment.DoesNotExist:
        return False


def is_student_restricted_from_booking(student_id: str) -> dict:
    """
    Check if student is restricted from booking appointments.

    Args:
        student_id: Student ID

    Returns:
        dict: {
            'is_restricted': bool,
            'reason': str,
            'total_no_shows': int,
            'restriction_until': date or None
        }
    """
    from app.models import StudentProfile
    from django.utils import timezone

    try:
        student = StudentProfile.objects.get(student_id=student_id)
        no_show_record = StudentNoShowRecord.objects.get(student=student)

        if no_show_record.is_restricted:
            # Check if restriction period has expired
            if (
                no_show_record.restriction_until
                and no_show_record.restriction_until <= timezone.now().date()
            ):
                # Auto-lift restriction
                no_show_record.is_restricted = False
                no_show_record.restriction_until = None
                no_show_record.save()

                return {
                    "is_restricted": False,
                    "reason": "",
                    "total_no_shows": no_show_record.total_no_shows,
                    "restriction_until": None,
                }

            return {
                "is_restricted": True,
                "reason": f"You have {no_show_record.total_no_shows} no-show appointments. "
                f"You are restricted until {no_show_record.restriction_until.strftime('%B %d, %Y')}",
                "total_no_shows": no_show_record.total_no_shows,
                "restriction_until": no_show_record.restriction_until,
            }

        return {
            "is_restricted": False,
            "reason": "",
            "total_no_shows": no_show_record.total_no_shows,
            "restriction_until": None,
        }

    except (StudentProfile.DoesNotExist, StudentNoShowRecord.DoesNotExist):
        return {
            "is_restricted": False,
            "reason": "",
            "total_no_shows": 0,
            "restriction_until": None,
        }


def get_student_no_show_statistics(student_id: str) -> dict:
    """
    Get no-show statistics for a student.

    Args:
        student_id: Student ID

    Returns:
        dict: No-show statistics
    """
    from app.models import StudentProfile

    try:
        student = StudentProfile.objects.get(student_id=student_id)
        no_show_record = StudentNoShowRecord.objects.get(student=student)

        # Get recent no-shows
        recent_no_shows = Appointment.objects.filter(
            student_id=student_id,
            was_no_show=True,
            actual_completion_date__gte=timezone.now() - timedelta(days=90),
        ).count()

        return {
            "total_no_shows": no_show_record.total_no_shows,
            "recent_no_shows_90_days": recent_no_shows,
            "last_no_show_date": no_show_record.last_no_show_date,
            "is_restricted": no_show_record.is_restricted,
            "restriction_until": no_show_record.restriction_until,
        }

    except (StudentProfile.DoesNotExist, StudentNoShowRecord.DoesNotExist):
        return {
            "total_no_shows": 0,
            "recent_no_shows_90_days": 0,
            "last_no_show_date": None,
            "is_restricted": False,
            "restriction_until": None,
        }
