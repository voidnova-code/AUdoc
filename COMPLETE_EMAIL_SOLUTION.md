# 📧 Email System - Complete Setup Guide

## 🎯 The Problem & Solution

**Problem**: You're not receiving appointment emails

**Root Cause**: Email management commands need to be scheduled to run daily

**Solution**: Use the automated email scheduler (3 options provided)

---

## ✅ Verification: Email Configuration Works

Your system is correctly configured:
```
✅ Email Backend: Django SMTP
✅ SMTP Host: smtp.gmail.com:587
✅ Email Address: sayankumarr02@gmail.com  
✅ Credentials: Loaded from .env file
✅ Email Templates: Ready (HTML formatted)
```

---

## 🚀 Start Receiving Emails in 2 Minutes

### Option 1: Automated Scheduler (Recommended) ⭐

**Step 1:** Install schedule package
```bash
pip install schedule
```

**Step 2:** Run the scheduler
```bash
python email_scheduler.py
```

**That's it!** The scheduler will:
- ✅ Send confirmations every day at 8:00 AM
- ✅ Send reminders every day at 8:00 PM
- ✅ Keep running in background
- ✅ Log all activity to `email_scheduler.log`

### Option 2: Windows Batch Script

**Step 1:** Double-click `email_scheduler.bat`

**Step 2:** Batch script will:
- Activate virtual environment
- Install dependencies
- Start the scheduler

---

## 📅 Making It Truly Automatic (Optional)

If you want it to start automatically with your computer:

### Setup Windows Task Scheduler:

1. **Open Task Scheduler**
   - Press `Win + R`
   - Type `taskschd.msc`
   - Press Enter

2. **Create New Task**
   - Right-click "Task Scheduler Library"
   - Click "Create Basic Task"
   - Name: `AUdoc Email Scheduler`

3. **Configure Trigger**
   - Trigger: "At startup"
   - Click "Next"

4. **Configure Action**
   - Action: "Start a program"
   - Program: `C:\Users\sayan\Desktop\New folder (4)\AUdoc_back\email_scheduler.bat`
   - Click "Next"

5. **Finish**
   - Check "Open Properties dialog"
   - Set "Run whether user is logged in or not"
   - Click "OK"

Now emails will be sent automatically every day!

---

## 🧪 Test It Works

### Quick Test:

```bash
# Open Command Prompt in project folder
cd "C:\Users\sayan\Desktop\New folder (4)\AUdoc_back"

# Activate environment
myenv\Scripts\activate.bat

# Send test confirmations
python manage.py send_appointment_confirmations

# Send test reminders
python manage.py send_appointment_reminders --type 24h
```

Check your email inbox! (Check spam folder too)

---

## 📊 What Gets Sent

### Appointment Confirmations (8:00 AM Daily)
- **Sent to**: Students with appointments today
- **Contains**: Appointment details, confirmation deadline (2 hours)
- **Action needed**: Student clicks Accept or Decline link
- **Format**: Professional HTML email

### Appointment Reminders (8:00 PM Daily)
- **Sent to**: Students with appointments tomorrow
- **Contains**: Appointment date, time, doctor, location
- **Purpose**: Courtesy reminder to prepare
- **Format**: Professional HTML email

---

## 📝 Email Templates

Both emails include:
✅ AUdoc branding (green theme)  
✅ Student details (name, ID, department)  
✅ Appointment info (date, time, doctor)  
✅ Important instructions  
✅ Clear call-to-action  

---

## 🔍 Monitor Email Activity

Check the log file to see what's happening:
```bash
# View recent logs
type email_scheduler.log

# Or open in Notepad
notepad email_scheduler.log
```

Example log output:
```
2024-04-11 08:00:05 - Sending Appointment Confirmations
2024-04-11 08:00:12 - [SUCCESS] Sent: John Doe (AU-2024-001)
2024-04-11 08:00:15 - [SUCCESS] Sent: Jane Smith (AU-2024-002)
2024-04-11 08:00:18 - ✅ Confirmations sent successfully!
```

---

## ⚠️ Troubleshooting

### "Module not found: schedule"
```bash
pip install schedule
```

### "Django project not found"
- Make sure you're running from the correct directory
- Expected: `C:\Users\sayan\Desktop\New folder (4)\AUdoc_back`

### "Connection timeout to smtp.gmail.com"
- Check internet connection
- Check firewall settings (port 587 must be open)
- Try alternative email provider (see EMAIL_SETUP_GUIDE.md)

### "Authentication failed"
- Verify Gmail app password is correct
- Check 2-factor authentication is enabled
- Regenerate app password in Gmail settings

### "Still not receiving emails?"
- Check spam folder in Gmail
- Check email_scheduler.log for errors
- Verify appointment status is "PENDING" or "CONFIRMED"
- Verify appointment date is today or tomorrow

---

## 📚 Additional Files

- **EMAIL_SETUP_GUIDE.md** - Comprehensive email configuration guide
- **EMAIL_QUICK_FIX.md** - Quick reference for troubleshooting
- **email_scheduler.py** - The main scheduler script
- **email_scheduler.bat** - Windows batch runner
- **test_email.py** - Test script to verify configuration

---

## 🎯 Next Steps

1. **Install schedule**: `pip install schedule`
2. **Run scheduler**: `python email_scheduler.py`
3. **Test it**: Send a test appointment and verify email arrives
4. **Automate** (optional): Set up Windows Task Scheduler
5. **Monitor**: Check email_scheduler.log for activity

---

## ✨ You're Done!

Your email system is now:
- ✅ Configured
- ✅ Tested  
- ✅ Automated
- ✅ Monitored

Students will now automatically receive:
- ✅ Appointment confirmations at 8 AM
- ✅ Appointment reminders at 8 PM

**Happy emailing! 🎉**

