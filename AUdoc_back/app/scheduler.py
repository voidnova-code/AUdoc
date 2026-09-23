"""
Scheduler for appointment confirmation system.

Jobs (all times in IST = UTC+5:30):
  - 1:00 AM  → send_appointment_confirmations  (emails go out)
  - 10:00 AM → cancel_unconfirmed_appointments (auto-cancel PENDING)

APScheduler runs inside the Django process via AppConfig.ready(), so no
external cron or paid Render tier is required.

NOTE: Render free tier spins down after inactivity. When the app wakes up,
APScheduler will re-register jobs and run any that were missed within the
misfire_grace_time window (set to 2 hours below).
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management import call_command
import logging
import pytz

logger = logging.getLogger(__name__)

IST = pytz.timezone("Asia/Kolkata")

scheduler = None


def start_scheduler():
    global scheduler
    if scheduler is not None and scheduler.running:
        return  # Already running, don't double-start

    scheduler = BackgroundScheduler(timezone=IST)

    # ── Job 1: Send confirmation emails at 1:00 AM IST ──────────────
    scheduler.add_job(
        func=run_send_confirmations,
        trigger=CronTrigger(hour=1, minute=0, timezone=IST),
        id='send_appointment_confirmations',
        name='Send Appointment Confirmation Emails (1:00 AM IST)',
        replace_existing=True,
        max_instances=1,
        misfire_grace_time=2 * 60 * 60,  # 2-hour grace — handles Render wakeup delay
    )

    # ── Job 2: Auto-cancel unconfirmed at 10:00 AM IST ───────────────
    scheduler.add_job(
        func=run_cancel_unconfirmed,
        trigger=CronTrigger(hour=10, minute=0, timezone=IST),
        id='cancel_unconfirmed_appointments',
        name='Auto-Cancel Unconfirmed Appointments (10:00 AM IST)',
        replace_existing=True,
        max_instances=1,
        misfire_grace_time=2 * 60 * 60,  # 2-hour grace
    )

    scheduler.start()
    logger.info(
        "Scheduler started — "
        "emails at 1:00 AM IST, auto-cancel at 10:00 AM IST"
    )


def stop_scheduler():
    global scheduler
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)
        scheduler = None
        logger.info("Scheduler stopped")


def run_send_confirmations():
    """Execute the send_appointment_confirmations management command."""
    try:
        logger.info("Scheduler: running send_appointment_confirmations...")
        call_command('send_appointment_confirmations')
        logger.info("Scheduler: send_appointment_confirmations completed.")
    except Exception as e:
        logger.error(f"Scheduler: send_appointment_confirmations failed: {e}", exc_info=True)


def run_cancel_unconfirmed():
    """Execute the cancel_unconfirmed_appointments management command."""
    try:
        logger.info("Scheduler: running cancel_unconfirmed_appointments...")
        call_command('cancel_unconfirmed_appointments')
        logger.info("Scheduler: cancel_unconfirmed_appointments completed.")
    except Exception as e:
        logger.error(f"Scheduler: cancel_unconfirmed_appointments failed: {e}", exc_info=True)
