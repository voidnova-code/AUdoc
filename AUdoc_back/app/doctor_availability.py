"""
Helper utilities for doctor availability and time slot management.
"""
from datetime import datetime, time, timedelta
from app.models import Doctor, DoctorLeave, TIME_SLOT_CHOICES


def is_doctor_available_on_date(doctor_id: int, appointment_date) -> bool:
    """
    Check if doctor is available on a specific date.

    Args:
        doctor_id: Doctor's ID
        appointment_date: Date object to check

    Returns:
        bool: True if doctor is available, False otherwise
    """
    doctor = Doctor.objects.get(id=doctor_id)

    # Check if doctor is generally available
    if not doctor.is_available:
        return False

    # Check if doctor is on leave
    if DoctorLeave.objects.filter(
        doctor_id=doctor_id,
        leave_date_from__lte=appointment_date,
        leave_date_to__gte=appointment_date,
        is_active=True,
    ).exists():
        return False

    # Check if date falls on working days
    day_name = appointment_date.strftime("%A")
    if doctor.available_days:
        available_days = [d.strip() for d in doctor.available_days.split(",")]
        if day_name not in available_days:
            return False

    return True


def get_available_time_slots(doctor_id: int, appointment_date) -> list:
    """
    Get available time slots for a doctor on a specific date.

    Args:
        doctor_id: Doctor's ID
        appointment_date: Date object

    Returns:
        list: List of available time slot tuples (time_value, time_display)
    """
    doctor = Doctor.objects.get(id=doctor_id)

    # Check if doctor is available on this date
    if not is_doctor_available_on_date(doctor_id, appointment_date):
        return []

    available_slots = []

    # Get working hours from doctor profile
    working_start = doctor.working_hours_start
    working_end = doctor.working_hours_end
    lunch_start = doctor.lunch_break_start
    lunch_end = doctor.lunch_break_end

    # Use default working hours if not set (9 AM - 5 PM)
    if not working_start:
        working_start = time(9, 0)
    if not working_end:
        working_end = time(17, 0)

    # Check each predefined slot
    for slot_value, slot_display in TIME_SLOT_CHOICES:
        # Parse slot time
        try:
            slot_time = datetime.strptime(slot_value, "%I:%M %p").time()
        except ValueError:
            continue

        # Check if slot is within working hours
        if not (working_start <= slot_time < working_end):
            continue

        # Check if slot is during lunch break
        if lunch_start and lunch_end:
            if lunch_start <= slot_time < lunch_end:
                continue

        # Check if slot is already booked
        from app.models import Appointment

        slot_exists = Appointment.objects.filter(
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=slot_value,
            status__in=["CONFIRMED", "PENDING"],
        ).exists()

        if not slot_exists:
            available_slots.append((slot_value, slot_display))

    return available_slots


def get_available_doctors(medical_department: str, appointment_date) -> list:
    """
    Get available doctors for a specific department on a date.

    Args:
        medical_department: Medical department code
        appointment_date: Date object

    Returns:
        list: List of available Doctor objects
    """
    doctors = Doctor.objects.filter(
        specialized_in=medical_department,
        is_available=True,
    )

    available_doctors = []
    for doctor in doctors:
        if is_doctor_available_on_date(doctor.id, appointment_date):
            available_doctors.append(doctor)

    return available_doctors


def get_doctor_next_available_date(doctor_id: int, start_date=None) -> datetime or None:
    """
    Get the next available date for a doctor.

    Args:
        doctor_id: Doctor's ID
        start_date: Start date to check from (default: today)

    Returns:
        datetime or None: Next available date, or None if no availability found
    """
    from datetime import date

    if not start_date:
        start_date = date.today()

    # Check next 30 days
    for days_ahead in range(30):
        check_date = start_date + timedelta(days=days_ahead)
        if is_doctor_available_on_date(doctor_id, check_date):
            return check_date

    return None
