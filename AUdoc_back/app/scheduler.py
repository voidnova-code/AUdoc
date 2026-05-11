"""
Scheduler for running appointment confirmation emails.
Runs daily at 8:00 AM.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

scheduler = None


def start_scheduler():
    global scheduler
    if scheduler is None:
        scheduler = BackgroundScheduler()

        # Schedule the send_appointment_confirmations command to run daily at 8 AM
        scheduler.add_job(
            func=run_send_confirmations,
            trigger="cron",
            hour=8,
            minute=0,
            id='send_appointment_confirmations',
            name='Send Appointment Confirmations',
            replace_existing=True,
            max_instances=1,
        )

        if not scheduler.running:
            scheduler.start()
            logger.info("Scheduler started - appointment confirmations will be sent daily at 8:00 AM")


def stop_scheduler():
    global scheduler
    if scheduler and scheduler.running:
        scheduler.shutdown()
        scheduler = None
        logger.info("Scheduler stopped")


def run_send_confirmations():
    """Execute the send_appointment_confirmations management command"""
    try:
        logger.info("Running send_appointment_confirmations...")
        call_command('send_appointment_confirmations')
        logger.info("send_appointment_confirmations completed successfully")
    except Exception as e:
        logger.error(f"Error running send_appointment_confirmations: {str(e)}")
