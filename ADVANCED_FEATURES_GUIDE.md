# Advanced Appointment System Features - Implementation Guide

This document describes the three advanced features implemented for the AUdoc appointment system.

## Features Implemented

### 1. 📱 SMS + Email Appointment Reminders

**What it does:**
- Sends 24-hour email reminders to patients before their appointment
- Sends 2-hour SMS reminders (urgent) 2 hours before appointment

**How it works:**
```
Day before appointment (8 PM):
  ├─ Email reminder sent with appointment details
  └─ Appointment.reminder_24h_sent = True

Appointment day (2 hours before):
  ├─ SMS reminder sent to patient phone
  └─ Appointment.reminder_2h_sent = True
```

**Files:**
- `app/sms_service.py` - SMS service providers (Twilio, Nexmo)
- `app/management/commands/send_appointment_reminders.py` - Scheduler command

**Usage:**
```bash
# Send 24-hour reminders
python manage.py send_appointment_reminders --type 24h

# Send 2-hour reminders
python manage.py send_appointment_reminders --type 2h

# Send all reminders
python manage.py send_appointment_reminders --type all
```

**Configuration:**
```python
# settings.py
SMS_PROVIDER = "twilio"  # or "nexmo"
APPOINTMENT_REMINDER_24H = True
APPOINTMENT_REMINDER_2H = True
```

---

### 2. 🗓️ Doctor Availability Calendar

**What it does:**
- Manages doctor working hours, lunch breaks, and leaves
- Filters available appointment slots based on doctor availability
- Prevents booking when doctor is unavailable

**How it works:**
```
Doctor Profile:
  ├─ Available Days: "Monday, Tuesday, Wednesday, Thursday, Friday"
  ├─ Working Hours: 9:00 AM - 5:00 PM
  ├─ Lunch Break: 1:00 PM - 2:00 PM
  └─ Leaves: DoctorLeave records for vacation/sick leave

When booking appointment:
  ├─ Check if date falls on doctor's available days
  ├─ Check if doctor is on leave (DoctorLeave table)
  ├─ Filter time slots within working hours
  ├─ Exclude lunch break times
  └─ Show only available slots
```

**Models:**
- `Doctor` - Added fields: `working_hours_start`, `working_hours_end`, `lunch_break_start`, `lunch_break_end`
- `DoctorLeave` - New model for tracking doctor leaves/unavailable periods

**Files:**
- `app/doctor_availability.py` - Availability checking utilities

**Key Functions:**
```python
from app.doctor_availability import (
    is_doctor_available_on_date,
    get_available_time_slots,
    get_available_doctors,
    get_doctor_next_available_date,
)

# Check if doctor is available
is_available = is_doctor_available_on_date(doctor_id=1, appointment_date=date(2024, 12, 15))

# Get available slots for a doctor
slots = get_available_time_slots(doctor_id=1, appointment_date=date(2024, 12, 15))
# Returns: [("09:00 AM", "09:00 AM"), ("09:30 AM", "09:30 AM"), ...]

# Get available doctors for a department
doctors = get_available_doctors(medical_department="General", appointment_date=date(2024, 12, 15))

# Get next available date for a doctor
next_date = get_doctor_next_available_date(doctor_id=1, start_date=date(2024, 12, 15))
```

**Admin Interface:**
1. Doctor Management:
   - Go to Admin > Doctors
   - Edit a doctor
   - Scroll to "Working Hours (Optional)" section
   - Set working hours and lunch break times
   - Set available days (e.g., "Monday, Tuesday, Wednesday, Thursday, Friday")

2. Doctor Leaves:
   - Go to Admin > Doctor Leaves
   - Click "Add Doctor Leave"
   - Select doctor and date range
   - Choose leave type (Personal, Medical, Conference, Emergency, Other)
   - Mark as active

---

### 3. ❌ No-Show Tracking & Booking Restrictions

**What it does:**
- Tracks no-show appointments for each student
- Automatically restricts students with repeated no-shows from booking
- Allows admin to mark appointments as completed or no-show

**How it works:**
```
Appointment Flow:
  
  Case 1: Patient shows up
    Doctor/Admin marks as "COMPLETED"
    └─ No impact on StudentNoShowRecord

  Case 2: Patient doesn't show up
    Doctor/Admin marks as "NO_SHOW"
    ├─ Appointment.status = "NO_SHOW"
    ├─ Appointment.was_no_show = True
    ├─ StudentNoShowRecord.total_no_shows += 1
    ├─ StudentNoShowRecord.last_no_show_date = now()
    └─ If total_no_shows >= 3:
        ├─ StudentNoShowRecord.is_restricted = True
        ├─ StudentNoShowRecord.restriction_until = now() + 30 days
        └─ Student cannot book new appointments until restriction expires

  Restriction Expiry:
    └─ Auto-lifted when restriction_until date passes
```

**Models:**
- `Appointment` - Added fields: `was_no_show`, `actual_completion_date`
- `StudentNoShowRecord` - New model tracking no-show statistics

**Configuration:**
```python
# settings.py
NO_SHOW_THRESHOLD = 3  # Restrict after 3 no-shows
NO_SHOW_RESTRICTION_DAYS = 30  # Restrict for 30 days
```

**Files:**
- `app/no_show_helper.py` - No-show tracking utilities

**Key Functions:**
```python
from app.no_show_helper import (
    mark_appointment_as_no_show,
    mark_appointment_as_completed,
    is_student_restricted_from_booking,
    get_student_no_show_statistics,
)

# Mark appointment as no-show
success = mark_appointment_as_no_show(appointment_id=123)

# Mark appointment as completed
success = mark_appointment_as_completed(appointment_id=123)

# Check if student is restricted
restriction = is_student_restricted_from_booking("ST001")
# Returns:
# {
#     'is_restricted': False,
#     'reason': '',
#     'total_no_shows': 0,
#     'restriction_until': None
# }

# Get student statistics
stats = get_student_no_show_statistics("ST001")
# Returns:
# {
#     'total_no_shows': 1,
#     'recent_no_shows_90_days': 1,
#     'last_no_show_date': datetime(...),
#     'is_restricted': False,
#     'restriction_until': None
# }
```

**Admin Interface:**
1. Appointment Status:
   - Go to Admin > Appointments
   - Find appointment by date/student
   - Change status dropdown to "No-Show" to mark no-show
   - Change status dropdown to "Completed" for attended appointments
   - Save

2. View No-Show Records:
   - Go to Admin > Student No-Show Records
   - See all students and their no-show counts
   - View restriction status and dates
   - Manually lift restrictions if needed

3. Booking Page:
   - Students with active restrictions see error message:
     "You have 3 no-show appointments. You are restricted until December 30, 2024"
   - Cannot proceed with booking

---

## Database Migrations

After implementing these features, run:

```bash
python manage.py makemigrations
python manage.py migrate
```

This creates:
- `DoctorLeave` table
- `StudentNoShowRecord` table
- New columns in `Appointment` table (reminder fields, no-show fields)
- New columns in `Doctor` table (working hours fields)

---

## Integration Points

### Views Updated

**app/views.py - appointment() view:**
```python
# Now includes:
# 1. Check student's no-show restriction before allowing booking
# 2. Display restriction warning if applicable
# 3. Show total no-shows in context
```

**app/views.py - admin_appointment_status() view:**
```python
# Now handles:
# 1. NO_SHOW status - automatically updates StudentNoShowRecord
# 2. COMPLETED status - marks no-show as False
```

### Admin Interface Updates

**app/admin.py:**
- `DoctorAdmin` - Added working hours fields
- `AppointmentAdmin` - Shows no-show status and reminder tracking
- `DoctorLeaveAdmin` - New admin for managing doctor leaves
- `StudentNoShowRecordAdmin` - New admin for viewing no-show records

---

## Cron Job Setup Examples

### Linux/Mac
```bash
# Edit crontab
crontab -e

# Add these lines:
# Send 24-hour email reminders at 8 PM daily
0 20 * * * cd /path/to/AUdoc_back && python manage.py send_appointment_reminders --type 24h

# Send 2-hour SMS reminders every hour
0 * * * * cd /path/to/AUdoc_back && python manage.py send_appointment_reminders --type 2h
```

### Windows (Task Scheduler)
```
Task Name: AUdoc-24h-Reminders
Program: C:\path\to\AUdoc_back\myenv\Scripts\python.exe
Arguments: manage.py send_appointment_reminders --type 24h
Working Directory: C:\path\to\AUdoc_back
Schedule: Daily at 8:00 PM

Task Name: AUdoc-2h-Reminders
Program: C:\path\to\AUdoc_back\myenv\Scripts\python.exe
Arguments: manage.py send_appointment_reminders --type 2h
Working Directory: C:\path\to\AUdoc_back
Schedule: Every 1 hour, starting from 00:00
```

---

## SMS Provider Setup

### Twilio
1. Sign up at https://www.twilio.com
2. Get Account SID and Auth Token from dashboard
3. Get a phone number or use Twilio's provided number
4. Add to .env:
   ```
   SMS_PROVIDER=twilio
   TWILIO_ACCOUNT_SID=AC...
   TWILIO_AUTH_TOKEN=...
   TWILIO_PHONE_NUMBER=+1234567890
   ```
5. Install: `pip install twilio`

### Nexmo/Vonage
1. Sign up at https://dashboard.nexmo.com
2. Get API Key and Secret from dashboard
3. Configure sender ID (11 characters max)
4. Add to .env:
   ```
   SMS_PROVIDER=nexmo
   NEXMO_API_KEY=...
   NEXMO_API_SECRET=...
   NEXMO_PHONE_NUMBER=YourSenderID
   ```
5. Install: `pip install vonage`

---

## Testing

### Test SMS Service
```python
python manage.py shell

>>> from app.sms_service import send_appointment_reminder
>>> success = send_appointment_reminder(
...     phone_number="+919999999999",
...     student_name="John Doe",
...     appointment_date="December 15",
...     appointment_time="2:00 PM",
...     hours_remaining=24
... )
>>> print(success)  # True if SMS sent
```

### Test Doctor Availability
```python
python manage.py shell

>>> from app.doctor_availability import get_available_time_slots
>>> from datetime import date
>>> slots = get_available_time_slots(doctor_id=1, appointment_date=date(2024, 12, 15))
>>> print(slots)  # List of available time slots
```

### Test No-Show Restriction
```python
python manage.py shell

>>> from app.no_show_helper import is_student_restricted_from_booking
>>> restriction = is_student_restricted_from_booking("ST001")
>>> print(restriction)
# {
#     'is_restricted': False,
#     'reason': '',
#     'total_no_shows': 0,
#     'restriction_until': None
# }
```

---

## Troubleshooting

### SMS Not Sending
- **Check credentials**: Verify TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER in .env
- **Phone number format**: Must be +country_code format (e.g., +91 for India)
- **Balance**: Check SMS provider account has sufficient balance
- **Test manually**: `python manage.py send_appointment_reminders --type 24h --debug`

### Reminders Not Sending
- **Check cron jobs**: `crontab -l` or check Task Scheduler on Windows
- **Test command**: `python manage.py send_appointment_reminders --type 24h`
- **Check logs**: `tail -f logs/security.log`
- **Verify appointments**: Ensure there are appointments scheduled for tomorrow/today

### Doctor Availability Not Working
- **Check DoctorLeave records**: Go to Admin > Doctor Leaves
- **Verify available_days format**: Should be "Monday, Tuesday, Wednesday, ..." (comma-separated)
- **Check working hours**: Ensure TimeField values are set correctly (e.g., 09:00, 17:00)

### No-Show Restriction Not Applying
- **Check threshold**: Verify NO_SHOW_THRESHOLD = 3 in settings
- **Manual test**: `python manage.py shell` and run the helper functions
- **Check database**: Verify StudentNoShowRecord is created after marking NO_SHOW

---

## Future Enhancements

1. **Dynamic Slot Filtering on Frontend**
   - Auto-update time slots when doctor is selected
   - Show doctor availability calendar

2. **Email Templates**
   - Customizable reminder email templates
   - Multilingual support

3. **SMS Templates**
   - Customizable SMS message templates
   - Support for different message types (confirmation, reminder, cancellation)

4. **Admin Dashboard Widgets**
   - No-show statistics chart
   - Appointment reminders status
   - Doctor availability overview

5. **Waitlist Feature**
   - Auto-notify when slots open up
   - Priority based on signup time

6. **API Endpoints**
   - `/api/doctor/{id}/availability/` - Get doctor availability
   - `/api/slots/` - Get available slots with filters
   - `/api/noshow-record/` - Get student's no-show record

---

## API Reference

### SMS Service API

```python
from app.sms_service import get_sms_service, send_appointment_reminder

# Get SMS service instance
service = get_sms_service()
success = service.send_sms("+919999999999", "Your message here")

# Or use the reminder helper directly
send_appointment_reminder(
    phone_number="+919999999999",
    student_name="John Doe",
    appointment_date="December 15",
    appointment_time="2:00 PM",
    hours_remaining=24  # or 2
)
```

### Doctor Availability API

```python
from app.doctor_availability import *
from datetime import date

# Check if doctor available on specific date
is_available_on_date(doctor_id, appointment_date)

# Get available time slots
get_available_time_slots(doctor_id, appointment_date)

# Get available doctors for department
get_available_doctors(medical_department, appointment_date)

# Find next available date
get_doctor_next_available_date(doctor_id, start_date=None)
```

### No-Show Helper API

```python
from app.no_show_helper import *

# Mark as no-show
mark_appointment_as_no_show(appointment_id, reason="")

# Mark as completed
mark_appointment_as_completed(appointment_id)

# Check restriction status
is_student_restricted_from_booking(student_id)

# Get statistics
get_student_no_show_statistics(student_id)
```

---

## Support & Questions

For issues or questions about these features, refer to:
1. This documentation
2. FEATURE_SETUP_GUIDE.txt
3. Code comments in respective files
4. Django admin interface for data verification
