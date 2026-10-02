"""
Helper utilities for doctor availability and time slot management.

Shift definitions (fixed):
  MORNING  08:00 AM – 02:00 PM
  EVENING  02:00 PM – 08:00 PM
  NIGHT    08:00 PM – 08:00 AM  (crosses midnight)
"""
from datetime import datetime, time, timedelta
from app.models import Doctor, DoctorLeave, TIME_SLOT_CHOICES


# ── Shift boundary helpers ────────────────────────────────────────────────────

def _slot_in_shift(slot_time: time, shift: str) -> bool:
    """
    Return True if *slot_time* falls inside the given shift window.

    MORNING  08:00 <= t < 14:00
    EVENING  14:00 <= t < 20:00
    NIGHT    t >= 20:00  OR  t < 08:00   (crosses midnight)
    """
    if shift == "MORNING":
        return time(8, 0) <= slot_time < time(14, 0)
    if shift == "EVENING":
        return time(14, 0) <= slot_time < time(20, 0)
    if shift == "NIGHT":
        return slot_time >= time(20, 0) or slot_time < time(8, 0)
    return False


# ── Public API ────────────────────────────────────────────────────────────────

def is_doctor_available_on_date(doctor_id: int, appointment_date) -> bool:
    """
    Check if a doctor is available on a specific date.

    Checks:
      1. Doctor's ``is_available`` flag.
      2. Active ``DoctorLeave`` records covering the date.
      3. The day name falls within ``available_days``.
    """
    doctor = Doctor.objects.get(id=doctor_id)

    if not doctor.is_available:
        return False

    if DoctorLeave.objects.filter(
        doctor_id=doctor_id,
        leave_date_from__lte=appointment_date,
        leave_date_to__gte=appointment_date,
        is_active=True,
    ).exists():
        return False

    day_name = appointment_date.strftime("%A")
    if doctor.available_days:
        available_days = [d.strip() for d in doctor.available_days.split(",")]
        if day_name not in available_days:
            return False

    return True


def get_available_time_slots(doctor_id: int, appointment_date) -> list:
    """
    Get available (unbooked) time slots for a doctor on a specific date.

    Slots are filtered to match the doctor's assigned shift only.
    Night shift slots are handled correctly (span crosses midnight).

    Returns:
        list[tuple]: [(time_value, time_display), ...]
    """
    doctor = Doctor.objects.get(id=doctor_id)

    if not is_doctor_available_on_date(doctor_id, appointment_date):
        return []

    shift = getattr(doctor, "shift", "MORNING")
    available_slots = []

    for slot_value, slot_display in TIME_SLOT_CHOICES:
        try:
            slot_time = datetime.strptime(slot_value, "%I:%M %p").time()
        except ValueError:
            continue

        # Only include slots that belong to this doctor's shift
        if not _slot_in_shift(slot_time, shift):
            continue

        # Check if slot is already booked
        from app.models import Appointment
        already_booked = Appointment.objects.filter(
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=slot_value,
            status__in=["CONFIRMED", "PENDING"],
        ).exists()

        if not already_booked:
            available_slots.append((slot_value, slot_display))

    return available_slots


def get_available_doctors(medical_department: str, appointment_date) -> list:
    """
    Return available Doctor objects for a department on a given date.
    """
    doctors = Doctor.objects.filter(
        specialized_in=medical_department,
        is_available=True,
    )
    return [d for d in doctors if is_doctor_available_on_date(d.id, appointment_date)]


def get_doctor_next_available_date(doctor_id: int, start_date=None):
    """
    Return the next calendar date (within 30 days) that the doctor is available,
    or None if none found.
    """
    from datetime import date
    if not start_date:
        start_date = date.today()

    for days_ahead in range(30):
        check_date = start_date + timedelta(days=days_ahead)
        if is_doctor_available_on_date(doctor_id, check_date):
            return check_date

    return None
