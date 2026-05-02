# Email Setup & Troubleshooting Guide for AUdoc

## ✅ Current Status

Your email system **IS properly configured**:
- ✅ Django SMTP Backend: Enabled
- ✅ Host: smtp.gmail.com
- ✅ Port: 587 (TLS)
- ✅ Credentials: Configured in `.env` file
- ✅ Email: `sayankumarr02@gmail.com`

---

## 🔧 Why You're Not Receiving Emails

The email system is configured, but **management commands need to be run manually or scheduled** with cron/task scheduler.

### Two Ways Emails Are Sent

#### 1. **Appointment Confirmation Emails** (Today's Appointments)
- Sent daily at **8 AM**
- For appointments scheduled for today
- Students get 2 hours to confirm

**Manual Test:**
```bash
python manage.py send_appointment_confirmations
```

#### 2. **Appointment Reminder Emails** (24-hour advance)
- Sent daily at **8 PM**
- For appointments scheduled for tomorrow
- Courtesy reminder

**Manual Test:**
```bash
python manage.py send_appointment_reminders --type 24h
```

#### 3. **SMS Reminders** (2-hour before)
- Sent hourly
- 2 hours before appointment time
- Uses SMS (currently free tier)

---

## 📋 Setup Steps

### Step 1: Verify Gmail App Password

Your email uses **Gmail with App Passwords** (not your regular Gmail password).

**Check if already set up:**
1. Go to: https://myaccount.google.com/security
2. Look for "App passwords" section
3. If you see the app password, it's working ✅
4. If not, create one:
   - Enable 2-factor authentication first
   - Go to App passwords
   - Select "Mail" and "Windows Computer"
   - Use the generated 16-character password

**Current password in `.env`:**
```
EMAIL_HOST_PASSWORD=grpf upuj gsjh mwcx
```

---

### Step 2: Test Email Configuration

Run the test script:

```bash
python test_email.py
```

Expected output:
```
EMAIL CONFIGURATION TEST
================================
✅ Email credentials are configured!
✅ SMTP connection successful!
✅ Test email sent to: sayankumarr02@gmail.com
```

Check your Gmail inbox for the test email (check spam folder too).

---

### Step 3: Run Management Commands

#### Test Send Confirmation Emails:
```bash
python manage.py send_appointment_confirmations
```

#### Test Send Reminder Emails:
```bash
python manage.py send_appointment_reminders --type 24h
```

---

## ⏰ Schedule Automated Emails

### Option 1: Windows Task Scheduler

#### Create a batch file (e.g., `send_emails.bat`):
```batch
@echo off
cd C:\Users\sayan\Desktop\New folder (4)\AUdoc_back
call myenv\Scripts\activate.bat
python manage.py send_appointment_confirmations
python manage.py send_appointment_reminders --type 24h
```

#### Schedule it:
1. Open **Task Scheduler** (Windows key + "Task Scheduler")
2. Click **Create Basic Task**
3. Name: "AUdoc Send Appointment Emails"
4. Trigger: Daily at 8:00 AM
5. Action: Run `send_emails.bat`
6. Click Finish

---

### Option 2: Python Schedule (Development)

Create `run_email_scheduler.py` in your project:

```python
import schedule
import subprocess
import time
from datetime import datetime

def send_confirmations():
    print(f"[{datetime.now()}] Sending appointment confirmations...")
    subprocess.run(["python", "manage.py", "send_appointment_confirmations"])

def send_reminders():
    print(f"[{datetime.now()}] Sending appointment reminders...")
    subprocess.run(["python", "manage.py", "send_appointment_reminders", "--type", "24h"])

# Schedule tasks
schedule.every().day.at("08:00").do(send_confirmations)
schedule.every().day.at("20:00").do(send_reminders)

print("Email scheduler running. Press Ctrl+C to stop.")
while True:
    schedule.run_pending()
    time.sleep(60)
```

Run it:
```bash
python run_email_scheduler.py
```

---

### Option 3: Django Cron Job (Production)

Install Django Crontab:
```bash
pip install django-crontab
```

Add to `settings.py`:
```python
CRONJOBS = [
    ('0 8 * * *', 'django.core.management.call_command', ['send_appointment_confirmations']),
    ('0 20 * * *', 'django.core.management.call_command', ['send_appointment_reminders', '--type=24h']),
]
```

Install cron jobs:
```bash
python manage.py crontab add
```

---

## 🧪 Test Email Sending

### Scenario 1: Test Confirmation Email
1. Create a new appointment for **today**
2. Mark status as `PENDING`
3. Run: `python manage.py send_appointment_confirmations`
4. Check email inbox

### Scenario 2: Test Reminder Email
1. Create a new appointment for **tomorrow**
2. Mark status as `CONFIRMED` or `PENDING`
3. Run: `python manage.py send_appointment_reminders --type 24h`
4. Check email inbox

---

## ❌ Troubleshooting

### Problem: "No emails being sent"

**Check:**
1. Is `.env` file present?
   ```bash
   dir .env
   ```

2. Are credentials correct?
   ```bash
   python test_email.py
   ```

3. Are management commands being run?
   ```bash
   python manage.py send_appointment_confirmations
   ```

### Problem: "Gmail authentication error"

**Solutions:**
1. Verify app password (16 characters, spaces don't matter in `.env`)
2. Check 2-factor authentication is enabled
3. Try regenerating app password
4. Whitelist IP in Gmail security settings

### Problem: "TLS connection failed"

**Solutions:**
1. Check internet connection
2. Verify firewall isn't blocking port 587
3. Try different email provider (see below)

### Problem: "Email appears in Django but not in inbox"

**Check:**
1. Gmail spam folder
2. Gmail filters/labels
3. Gmail blocking suspicious apps (check security notifications)

---

## 🔄 Alternative Email Providers (Free Tier)

If Gmail doesn't work, try these free alternatives:

### SendGrid (100 emails/day free)
```python
EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
SENDGRID_API_KEY = "your-api-key"
DEFAULT_FROM_EMAIL = "noreply@yourdomain.com"
```

### Mailgun (100 emails/day free)
```python
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.mailgun.org"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "postmaster@sandbox.mailgun.org"
EMAIL_HOST_PASSWORD = "your-password"
```

### MailerSend (100 emails/month free)
```python
EMAIL_HOST = "smtp.mailersend.net"
EMAIL_PORT = 587
EMAIL_HOST_USER = "your@email.com"
EMAIL_HOST_PASSWORD = "your-password"
```

---

## 📞 Support

**For student email sending issues:**
1. Use free tier email service (recommended)
2. Enable less secure app access in Gmail
3. Use App Passwords instead of Gmail password
4. Test with `python test_email.py`
5. Schedule management commands with cron

**Key Files:**
- Email settings: `AUdoc_back/settings.py` (lines with EMAIL_)
- Credentials: `.env` file
- Confirmation emails: `app/management/commands/send_appointment_confirmations.py`
- Reminder emails: `app/management/commands/send_appointment_reminders.py`
- Test script: `test_email.py`

---

## ✨ Email Templates

All email templates are in the management commands and include:
- ✅ Appointment confirmations (2-hour deadline)
- ✅ Appointment reminders (24-hour advance)
- ✅ SMS reminders (2-hour before)
- ✅ Beautiful HTML formatting
- ✅ Student-friendly language

---

**Status:** Email system is configured and ready. Just needs manual or scheduled execution.
**Next Step:** Run `python manage.py send_appointment_confirmations` to test!

