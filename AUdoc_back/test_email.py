#!/usr/bin/env python
"""
Test script to verify email configuration and send a test email.
Run from the project root: python test_email.py
"""
import os
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AUdoc_back.settings')
django.setup()

from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings

print("=" * 70)
print("EMAIL CONFIGURATION TEST")
print("=" * 70)

print(f"\n📧 Email Backend: {settings.EMAIL_BACKEND}")
print(f"📧 Email Host: {settings.EMAIL_HOST}")
print(f"📧 Email Port: {settings.EMAIL_PORT}")
print(f"📧 Email Use TLS: {settings.EMAIL_USE_TLS}")
print(f"📧 Email Host User: {settings.EMAIL_HOST_USER}")
print(f"📧 Email Host Password: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
print(f"📧 Default From Email: {settings.DEFAULT_FROM_EMAIL}")

if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
    print("\n❌ ERROR: Email credentials not configured!")
    print("   Please set EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in .env file")
    exit(1)

print("\n" + "=" * 70)
print("SENDING TEST EMAIL...")
print("=" * 70)

try:
    # Create a test email
    subject = "🧪 AUdoc Test Email - Configuration Verified"
    text_content = """
Dear User,

This is a test email to verify that AUdoc email system is configured correctly.

If you received this email, the email setup is working!

Test Details:
- Email Backend: Django SMTP
- Host: smtp.gmail.com
- Port: 587
- TLS: Enabled

Best regards,
AUdoc Campus Health Center
    """

    html_content = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #f4f8f5; }
        .container { max-width: 600px; margin: 0 auto; background: #fff; border-radius: 12px; padding: 30px; }
        .header { background: linear-gradient(135deg, #4a7c59, #2e5c3a); color: #fff; padding: 20px; border-radius: 8px; text-align: center; }
        .content { padding: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 Test Email</h1>
            <p>AUdoc Email Configuration Test</p>
        </div>
        <div class="content">
            <h2>Success! ✅</h2>
            <p>If you're reading this, your email system is working correctly.</p>
            <p><strong>Email Configuration Status:</strong></p>
            <ul>
                <li>✓ SMTP Connection: OK</li>
                <li>✓ Authentication: OK</li>
                <li>✓ Email Delivery: OK</li>
            </ul>
        </div>
    </div>
</body>
</html>
    """

    # Send email using EmailMultiAlternatives for HTML support
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.EMAIL_HOST_USER]  # Send to the configured email for testing
    )
    email.attach_alternative(html_content, "text/html")
    
    print(f"\n📧 Sending test email to: {settings.EMAIL_HOST_USER}")
    result = email.send()
    
    if result == 1:
        print("✅ SUCCESS: Test email sent successfully!")
        print("\n" + "=" * 70)
        print("EMAIL CONFIGURATION: ✅ VERIFIED")
        print("=" * 70)
        print("\n📌 Next Steps:")
        print("1. Check your inbox for the test email")
        print("2. If not received, check spam folder")
        print("3. Verify Gmail App Password is correct")
        print("4. Run management commands to send appointment emails:")
        print("   - python manage.py send_appointment_confirmations")
        print("   - python manage.py send_appointment_reminders")
        exit(0)
    else:
        print("❌ FAILED: Email sending returned unexpected result")
        exit(1)
        
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}")
    print(f"   {str(e)}")
    print("\n" + "=" * 70)
    print("TROUBLESHOOTING:")
    print("=" * 70)
    print("\n1. Check .env file exists and has EMAIL_HOST_USER and EMAIL_HOST_PASSWORD")
    print("2. Verify Gmail App Password (not regular password)")
    print("3. Ensure 'Less secure app access' is enabled (if using Gmail)")
    print("4. Check Gmail two-factor authentication is set up correctly")
    print("5. Verify .env file is in the correct location:")
    print(f"   Expected: {Path(__file__).parent / '.env'}")
    exit(1)
