# Today's Appointment System - Setup Guide

## Overview

The Today's Appointment system automatically manages daily appointment confirmations with the following features:

1. **Email Confirmations**: Sends emails at 8 AM to patients with appointments scheduled for today
2. **2-Hour Response Window**: Patients have 2 hours to accept or decline
3. **FCFS Queue**: Confirmed patients are assigned positions in First Come, First Serve order
4. **Auto-Cleanup**: Past appointment data is automatically deleted daily

## Components Created

### 1. Database Model
- **TodaysAppointment**: Tracks daily appointments with confirmation status and queue positions

### 2. Management Commands
- `send_appointment_confirmations`: Sends confirmation emails at 8 AM
- `cleanup_todays_appointments`: Cleans up old records daily

### 3. Views & Templates
- Confirmation URLs with accept/decline actions
- Beautiful confirmation page with queue position display

### 4. Admin Panel Integration
- New "Today's Appointments" tab showing real-time status
- FCFS queue visualization
- Confirmation status tracking

## Setup Instructions

### Windows (Task Scheduler)

#### 1. Send Confirmation Emails at 8 AM Daily

1. Open Task Scheduler (search for "Task Scheduler" in Start menu)
2. Click "Create Basic Task"
3. Name: "AUdoc - Send Appointment Confirmations"
4. Trigger: Daily at 8:00 AM
5. Action: Start a program
   - Program: `python`
   - Arguments: `manage.py send_appointment_confirmations`
   - Start in: `c:\Users\sayan\Desktop\New folder (4)\AUdoc_back`

#### 2. Cleanup Old Records at Midnight Daily

1. Open Task Scheduler
2. Click "Create Basic Task"
3. Name: "AUdoc - Cleanup Old Appointments"
4. Trigger: Daily at 12:00 AM (midnight)
5. Action: Start a program
   - Program: `python`
   - Arguments: `manage.py cleanup_todays_appointments`
   - Start in: `c:\Users\sayan\Desktop\New folder (4)\AUdoc_back`

### Linux/MacOS (Cron Jobs)

Edit crontab:
```bash
crontab -e
```

Add these lines:
```bash
# Send appointment confirmations at 8 AM daily
0 8 * * * cd /path/to/AUdoc_back && python manage.py send_appointment_confirmations

# Cleanup old appointments at midnight daily
0 0 * * * cd /path/to/AUdoc_back && python manage.py cleanup_todays_appointments
```

## Manual Testing

### Test Email Sending
```bash
cd "c:\Users\sayan\Desktop\New folder (4)\AUdoc_back"
python manage.py send_appointment_confirmations
```

### Test Cleanup
```bash
cd "c:\Users\sayan\Desktop\New folder (4)\AUdoc_back"
python manage.py cleanup_todays_appointments
```

## Email Configuration

Make sure your `.env` file has the correct email settings:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=AUdoc Health Center <your-email@gmail.com>
SITE_URL=http://localhost:8000  # Change to your production URL
```

## How It Works

### 1. Morning (8:00 AM)
- System finds all appointments scheduled for today with status = "PENDING"
- Creates TodaysAppointment records for each
- Sends confirmation emails with accept/decline links
- Sets 2-hour deadline (10:00 AM)

### 2. Patient Response (within 2 hours)
- Patient clicks "Accept" → Status becomes "CONFIRMED" → Assigned queue position (FCFS)
- Patient clicks "Decline" → Status becomes "DECLINED" → Appointment cancelled
- No response → After 2 hours, status becomes "EXPIRED" → Appointment cancelled

### 3. Midnight (12:00 AM)
- Cleanup command runs
- Deletes all TodaysAppointment records from previous days
- Keeps database clean and efficient

## Admin Panel Features

Navigate to: `/manage/?tab=todays-appointments`

**What you can see:**
- Queue positions for confirmed patients
- Email sent timestamps
- Response deadlines
- Current status of each confirmation
- Color-coded rows (green = confirmed, red = expired)

**Legend:**
- ✓ CONFIRMED: Patient accepted, in queue
- ⏳ PENDING: Waiting for response
- ✗ DECLINED: Patient declined
- ⏰ EXPIRED: 2-hour window passed

## Troubleshooting

### Emails not sending?
1. Check `.env` email configuration
2. Test email settings: `python manage.py shell`
   ```python
   from django.core.mail import send_mail
   send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
   ```
3. Check Gmail App Password (if using Gmail)

### Task Scheduler not running?
1. Check task history in Task Scheduler
2. Ensure Python path is correct
3. Run command manually first to test

### Queue positions not updating?
1. Check that patients are clicking the confirmation link
2. Verify TodaysAppointment records exist in admin
3. Check Django logs for errors

## Database Schema

**TodaysAppointment Table:**
- `appointment` (ForeignKey → Appointment)
- `confirmation_token` (UUID)
- `email_sent_at` (DateTime)
- `response_deadline` (DateTime)
- `status` (PENDING/CONFIRMED/DECLINED/EXPIRED)
- `responded_at` (DateTime)
- `queue_position` (Integer, FCFS order)
- `created_at` (DateTime)

## Support

For issues or questions:
1. Check Django logs: `python manage.py runserver`
2. Test commands manually
3. Verify email configuration
4. Check Task Scheduler logs (Windows) or cron logs (Linux)
