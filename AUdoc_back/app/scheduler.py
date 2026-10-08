"""
Scheduler for appointment confirmation system.

Jobs (all times in IST = UTC+5:30):
  - Every 30 min from 1:00 AM to 9:00 AM → send_appointment_confirmations
    (The command is idempotent: uses get_or_create, never double-sends.)
  - 10:00 AM → cancel_unconfirmed_appointments (auto-cancel PENDING)

WHY every 30 minutes instead of once at 1:00 AM?
  A student who books at 1:30 AM (after the 1 AM run) would never receive
  a confirmation email under the old single-shot design. Running every
  30 minutes guarantees no student waits more than 30 min for their email,
  regardless of when they booked.
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

    # ── Job 1: Send confirmation emails every 30 min, 1:00 AM–9:00 AM IST ────
    # Safe to run multiple times — management command never re-sends to a
    # student who already received a confirmation email (get_or_create guard).
    scheduler.add_job(
        func=run_send_confirmations,
        trigger=CronTrigger(
            hour='1-9',      # 1:00 AM through 9:00 AM IST
            minute='0,30',   # on the hour and half-hour
            timezone=IST,
        ),
        id='send_appointment_confirmations',
        name='Send Appointment Confirmation Emails (every 30 min, 1-9 AM IST)',
        replace_existing=True,
        max_instances=1,
        misfire_grace_time=30 * 60,  # 30-min grace for missed fires
    )

    # ── Job 2: Auto-cancel unconfirmed at 10:00 AM IST ───────────────────────
    scheduler.add_job(
        func=run_cancel_unconfirmed,
        trigger=CronTrigger(hour=10, minute=0, timezone=IST),
        id='cancel_unconfirmed_appointments',
        name='Auto-Cancel Unconfirmed Appointments (10:00 AM IST)',
        replace_existing=True,
        max_instances=1,
        misfire_grace_time=2 * 60 * 60,  # 2-hour grace
    )

    # ── Job 3: Nightly full cleanup at 8:00 AM IST ───────────────────────────
    # The Night shift ends at 8:00 AM. At this point, mark ALL remaining
    # CONFIRMED (unvisited) appointments from the previous day as NO_SHOW.
    # This ensures the Today's Appointments panel starts fresh every morning.
    scheduler.add_job(
        func=run_nightly_cleanup,
        trigger=CronTrigger(hour=8, minute=5, timezone=IST),  # 8:05 AM — after confirmation emails start
        id='nightly_shift_cleanup',
        name='Nightly Shift Cleanup — Mark Unvisited as No-Show (8:05 AM IST)',
        replace_existing=True,
        max_instances=1,
        misfire_grace_time=2 * 60 * 60,
    )

    scheduler.start()
    logger.info(
        "Scheduler started — "
        "confirmation emails every 30 min (1:00–9:00 AM IST), "
        "auto-cancel at 10:00 AM IST"
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


def run_nightly_cleanup():
    """
    Mark ALL remaining CONFIRMED (unvisited) appointments from yesterday as NO_SHOW.
    Runs at 8:05 AM IST — just after the Night shift ends — to clear the
    full previous day's queue so the admin panel starts fresh every morning.
    """
    try:
        logger.info("Scheduler: running nightly shift cleanup (mark_shift_no_shows --shift ALL)...")
        call_command('mark_shift_no_shows', '--shift', 'ALL')
        logger.info("Scheduler: nightly shift cleanup completed.")
    except Exception as e:
        logger.error(f"Scheduler: nightly shift cleanup failed: {e}", exc_info=True)
