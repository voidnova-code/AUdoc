"""
SMS Service for sending appointment reminders.
Supports multiple SMS providers: Twilio, Nexmo/Vonage, or DISABLED for free setup

SMS is OPTIONAL - you can use just email reminders for free!
"""
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class SMSService:
    """Base SMS service class"""

    def send_sms(self, phone_number: str, message: str) -> bool:
        """Send SMS message. Returns True if successful."""
        raise NotImplementedError


class NoSMSService(SMSService):
    """Dummy SMS service for students using free email-only setup"""

    def __init__(self):
        logger.info("SMS disabled - using email-only reminders (free setup)")

    def send_sms(self, phone_number: str, message: str) -> bool:
        """SMS disabled - returns True but doesn't send"""
        logger.info(f"SMS disabled: Would send to {phone_number}: {message[:50]}...")
        return True  # Don't fail, just log


class SMSService:
    """Base SMS service class"""

    def send_sms(self, phone_number: str, message: str) -> bool:
        """Send SMS message. Returns True if successful."""
        raise NotImplementedError


class TwilioSMSService(SMSService):
    """Twilio SMS service implementation"""

    def __init__(self):
        try:
            import twilio
            from twilio.rest import Client
            self.twilio = twilio
            self.Client = Client

            self.account_sid = settings.TWILIO_ACCOUNT_SID
            self.auth_token = settings.TWILIO_AUTH_TOKEN
            self.phone_number = settings.TWILIO_PHONE_NUMBER

            if not all([self.account_sid, self.auth_token, self.phone_number]):
                raise ValueError("Twilio credentials not configured in settings")

            self.client = self.Client(self.account_sid, self.auth_token)
        except ImportError:
            logger.error("Twilio library not installed. Install with: pip install twilio")
            self.client = None

    def send_sms(self, phone_number: str, message: str) -> bool:
        """Send SMS via Twilio"""
        if not self.client:
            logger.error("Twilio client not initialized")
            return False

        try:
            # Ensure phone number is in E.164 format (+country code)
            if not phone_number.startswith("+"):
                phone_number = f"+91{phone_number}" if len(phone_number) == 10 else f"+{phone_number}"

            response = self.client.messages.create(
                body=message,
                from_=self.phone_number,
                to=phone_number,
            )
            logger.info(f"SMS sent successfully to {phone_number} (SID: {response.sid})")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS to {phone_number}: {str(e)}")
            return False


class NexmoSMSService(SMSService):
    """Nexmo/Vonage SMS service implementation"""

    def __init__(self):
        try:
            from vonage import Client
            from vonage.sms import MessageStatus

            self.Client = Client
            self.MessageStatus = MessageStatus

            api_key = settings.NEXMO_API_KEY
            api_secret = settings.NEXMO_API_SECRET
            self.phone_number = settings.NEXMO_PHONE_NUMBER

            if not all([api_key, api_secret, self.phone_number]):
                raise ValueError("Nexmo credentials not configured in settings")

            self.client = self.Client(key=api_key, secret=api_secret)
        except ImportError:
            logger.error("Vonage (Nexmo) library not installed. Install with: pip install vonage")
            self.client = None

    def send_sms(self, phone_number: str, message: str) -> bool:
        """Send SMS via Nexmo/Vonage"""
        if not self.client:
            logger.error("Nexmo client not initialized")
            return False

        try:
            # Ensure phone number is in international format
            if not phone_number.startswith("+"):
                phone_number = f"+91{phone_number}" if len(phone_number) == 10 else f"+{phone_number}"

            response = self.client.sms.send_message(
                {
                    "to": phone_number,
                    "from": self.phone_number,
                    "text": message,
                }
            )

            if response["messages"][0]["status"] == self.MessageStatus.OK:
                logger.info(f"SMS sent successfully to {phone_number}")
                return True
            else:
                logger.error(f"Failed to send SMS to {phone_number}: {response['messages'][0]['error-text']}")
                return False
        except Exception as e:
            logger.error(f"Error sending SMS to {phone_number}: {str(e)}")
            return False


def get_sms_service() -> SMSService:
    """Factory function to get appropriate SMS service
    
    Options:
    - "twilio": Use Twilio (paid)
    - "nexmo": Use Nexmo/Vonage (paid)
    - "disabled" or "none": Use email-only (FREE - recommended for students!)
    """
    provider = getattr(settings, "SMS_PROVIDER", "disabled").lower()

    if provider == "nexmo":
        return NexmoSMSService()
    elif provider == "twilio":
        return TwilioSMSService()
    else:  # default to disabled (FREE)
        return NoSMSService()


def send_appointment_reminder(phone_number: str, student_name: str, appointment_date: str, appointment_time: str, hours_remaining: int) -> bool:
    """
    Send appointment reminder SMS.

    Args:
        phone_number: Patient's phone number
        student_name: Patient's name
        appointment_date: Appointment date (formatted string)
        appointment_time: Appointment time (formatted string)
        hours_remaining: Hours until appointment (24 or 2)

    Returns:
        bool: True if SMS sent successfully
    """
    if hours_remaining == 24:
        message = f"Hi {student_name}, Reminder: Your appointment is scheduled for {appointment_date} at {appointment_time}. Please confirm or decline when you receive the confirmation email. - AUdoc Health Center"
    elif hours_remaining == 2:
        message = f"⏰ URGENT: {student_name}, Your appointment is in 2 hours at {appointment_time}. Please arrive on time. - AUdoc Health Center"
    else:
        message = f"Reminder: Your appointment is scheduled for {appointment_date} at {appointment_time}. - AUdoc Health Center"

    service = get_sms_service()
    return service.send_sms(phone_number, message)
