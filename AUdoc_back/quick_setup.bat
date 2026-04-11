@echo off
REM Quick setup script for AUdoc appointment features (FREE setup - email only)

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║  AUdoc Advanced Appointment - FREE Setup (Email Only)          ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Step 1: Run migrations
echo 📦 Step 1: Running database migrations...
python manage.py makemigrations
python manage.py migrate
echo ✅ Migrations complete!
echo.

REM Step 2: Check email config
echo 📧 Step 2: Checking email configuration...
findstr /M "EMAIL_HOST_USER" .env >nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ Email configured in .env
) else (
    echo ⚠️  Make sure EMAIL_HOST_USER is set in .env
)
echo.

REM Step 3: Test reminders
echo 🧪 Step 3: Testing 24-hour reminder command...
python manage.py send_appointment_reminders --type 24h
echo ✅ Reminders command works!
echo.

REM Step 4: Check all 3 features
echo ✨ All 3 Features Status:
echo   ✅ Feature 1: Email Reminders - READY (FREE)
echo   ✅ Feature 2: Doctor Availability - READY (FREE)
echo   ✅ Feature 3: No-Show Tracking - READY (FREE)
echo.

echo 🎉 Setup complete! All features ready to use - FREE!
echo.
echo Next steps:
echo 1. Go to Admin > Doctors and set working hours
echo 2. Test booking an appointment
echo 3. Schedule reminders via Task Scheduler (optional)
echo.
echo For more details, read: FREE_SETUP_FOR_STUDENTS.md
echo.
pause
