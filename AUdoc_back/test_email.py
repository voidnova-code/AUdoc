import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AUdoc_back.settings")
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("="*60)
print("EMAIL CONFIGURATION TEST")
print("="*60)

# Check environment
resend_key = os.environ.get("RESEND_API_KEY", "NOT SET")
from_email = os.environ.get("DEFAULT_FROM_EMAIL", "NOT SET")

print("\n1. Configuration:")
print(f"   RESEND_API_KEY: {resend_key[:15]}..." if resend_key != "NOT SET" else "   RESEND_API_KEY: NOT SET")
print(f"   DEFAULT_FROM_EMAIL: {from_email}")
print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")

# Test Resend SDK
print("\n2. Testing Resend SDK directly:")
try:
    import resend
    resend.api_key = resend_key
    
    response = resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": "sayankumarr02@gmail.com",
        "subject": "Resend Test",
        "html": "<p>Test email from Resend SDK</p>"
    })
    print("   [OK] Resend client initialized")
    print(f"   Response: {response}")
except Exception as e:
    print(f"   [ERROR] {str(e)}")

# Test Django send_mail
print("\n3. Testing Django send_mail:")
try:
    result = send_mail(
        'AUdoc Test Email',
        'This is a test email from AUdoc',
        'sayankumarr02@gmail.com',
        ['sayankumarr02@gmail.com'],
        fail_silently=False
    )
    print(f"   [OK] Email sent successfully! Result: {result}")
except Exception as e:
    print(f"   [ERROR] {str(e)}")

print("\n" + "="*60)
