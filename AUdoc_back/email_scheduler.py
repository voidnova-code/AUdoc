#!/usr/bin/env python
"""
Automated Email Scheduler for AUdoc

This script runs email sending tasks at scheduled times:
- 8:00 AM: Send appointment confirmations
- 8:00 PM: Send appointment reminders

Run this script in the background while your Django server is running.

Usage:
    python email_scheduler.py

To keep it running in the background on Windows:
    1. Create a batch file with: python email_scheduler.py
    2. Add to Windows Task Scheduler to run at startup
    3. Set to "Run whether user is logged in or not"
"""

import os
import sys
import django
import schedule
import time
import logging
from datetime import datetime
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AUdoc_back.settings')
django.setup()

from django.core.management import call_command
from django.conf import settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────

def send_confirmations():
    """Send appointment confirmation emails"""
    try:
        logger.info("=" * 70)
        logger.info("TASK: Sending Appointment Confirmations")
        logger.info("=" * 70)
        
        call_command('send_appointment_confirmations')
        
        logger.info("✅ Confirmations sent successfully!")
        logger.info("=" * 70 + "\n")
    except Exception as e:
        logger.error(f"❌ Error sending confirmations: {str(e)}")
        logger.error("=" * 70 + "\n")

def send_reminders():
    """Send appointment reminder emails"""
    try:
        logger.info("=" * 70)
        logger.info("TASK: Sending Appointment Reminders (24h)")
        logger.info("=" * 70)
        
        call_command('send_appointment_reminders', '--type', '24h')
        
        logger.info("✅ Reminders sent successfully!")
        logger.info("=" * 70 + "\n")
    except Exception as e:
        logger.error(f"❌ Error sending reminders: {str(e)}")
        logger.error("=" * 70 + "\n")

# ─────────────────────────────────────────────────────────────────────────

def main():
    """Main scheduler loop"""
    
    print("\n" + "=" * 70)
    print("🚀 AUdoc Email Scheduler Starting")
    print("=" * 70)
    print(f"\nEmail Service: {settings.EMAIL_BACKEND}")
    print(f"Email Host: {settings.EMAIL_HOST}")
    print(f"From Email: {settings.DEFAULT_FROM_EMAIL}")
    print("\nScheduled Tasks:")
    print("  • 08:00 AM - Send appointment confirmations")
    print("  • 08:00 PM - Send appointment reminders")
    print("\nPress Ctrl+C to stop the scheduler")
    print("=" * 70 + "\n")
    
    # Schedule jobs
    schedule.every().day.at("08:00").do(send_confirmations)
    schedule.every().day.at("20:00").do(send_reminders)
    
    logger.info("📅 Email scheduler initialized")
    logger.info(f"⏰ Next tasks:")
    logger.info(f"   - Confirmations: Daily at 08:00 AM")
    logger.info(f"   - Reminders: Daily at 08:00 PM")
    logger.info(f"\nScheduler running... (Press Ctrl+C to stop)\n")
    
    # Keep scheduler running
    try:
        while True:
            schedule.run_pending()
            
            # Check every minute
            time.sleep(60)
            
            # Print status every hour
            current_time = datetime.now()
            if current_time.minute == 0:
                logger.info(f"⏰ Scheduler still running at {current_time.strftime('%I:%M %p')}")
                
    except KeyboardInterrupt:
        logger.info("\n\n" + "=" * 70)
        logger.info("⛔ Scheduler stopped by user")
        logger.info("=" * 70)
        print("\n✋ Email scheduler stopped.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n❌ Scheduler error: {str(e)}")
        logger.error("=" * 70)
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
