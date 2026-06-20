import os
import django
from datetime import date
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AUdoc_back.settings")
django.setup()

from app.models import Appointment, TodaysAppointment, Doctor
from django.core import mail
from django.test import Client
from django.core.management import call_command
from django.conf import settings

def run_demo():
    print("="*50)
    print("   [Demo] AUdoc Appointment Workflow Demo Test")
    print("="*50)
    
    # 1. Clear previous test data
    Appointment.objects.filter(email="demo_test@example.com").delete()
    
    # 2. Setup Email backend to locmem to intercept emails without sending real ones
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
    mail.outbox = [] # Clear outbox
    
    # 3. Create a doctor if not exists
    doctor, _ = Doctor.objects.get_or_create(
        email="doctor_demo@example.com",
        defaults={
            "name": "Demo Doctor",
            "specialized_in": "GENERAL",
            "is_available": True
        }
    )
    
    # 4. Create a PENDING appointment for today
    today = date.today()
    print(f"\n[Step 1] Creating a PENDING appointment for {today}...")
    appointment = Appointment.objects.create(
        student_id="DEMO123",
        student_name="Demo User",
        phone="1234567890",
        email="demo_test@example.com",
        student_department="CSE",
        medical_department="GENERAL",
        doctor=doctor,
        appointment_date=today,
        status="PENDING",
        problem_description="Demo testing workflow"
    )
    print(f"OK: Appointment created with status: {appointment.status}")
    
    # 5. Run the cron job logic (simulating 8:00 AM)
    print("\n[Step 2] Running the daily confirmation cron job (8:00 AM)...")
    call_command('send_appointment_confirmations')
    
    # 6. Check emails
    if len(mail.outbox) == 0:
        print("ERROR: No email was sent!")
        return
        
    email = mail.outbox[0]
    print(f"OK: Email Sent to: {email.to[0]}")
    print(f"Subject: {email.subject}")
    
    # Extract the confirmation link from plain text body
    body = email.body
    
    accept_link = None
    for line in body.split('\n'):
        if "ACCEPT :" in line:
            accept_link = line.split("ACCEPT :")[1].strip()
            break
            
    if not accept_link:
        print("ERROR: Could not find ACCEPT link in email.")
        return
        
    print(f"\n[Step 3] Extracted Confirmation Link from Email:")
    print(f"Link: {accept_link}")
    
    # 7. Simulate clicking the accept link
    from urllib.parse import urlparse
    path = urlparse(accept_link).path
    print(f"\n[Step 4] Simulating user clicking the Accept link...")
    
    c = Client(SERVER_NAME='127.0.0.1')
    response = c.get(path)
    
    if response.status_code == 200:
        print(f"OK: Link clicked successfully (HTTP {response.status_code})")
    else:
        print(f"ERROR: Failed to click link (HTTP {response.status_code})")
        return
    
    # 8. Check TodaysAppointment queue position
    today_appt = TodaysAppointment.objects.get(appointment=appointment)
    print(f"\n[Step 5] Final Queue Status verification:")
    print(f"Status: {today_appt.status}")
    print(f"FCFS Queue Position: {today_appt.queue_position}")
    
    if today_appt.queue_position is not None:
        print("\nSUCCESS! The workflow works perfectly from end to end.")
    else:
        print("\nFAILED to assign queue position.")
        
    print("="*50)

if __name__ == "__main__":
    run_demo()
