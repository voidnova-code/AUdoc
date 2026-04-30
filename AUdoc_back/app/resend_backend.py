"""Django email backend for Resend"""
import os
import logging
from django.core.mail.backends.base import BaseEmailBackend


logger = logging.getLogger(__name__)


class ResendBackend(BaseEmailBackend):
    """Send emails via Resend API"""

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = os.environ.get("RESEND_API_KEY", "")

        if not self.api_key:
            logger.error("❌ RESEND_API_KEY is not set in environment variables")

    def send_messages(self, email_messages):
        """Send one or more EmailMessage objects and return the number sent."""
        if not self.api_key:
            logger.error("❌ Resend API key not configured - missing RESEND_API_KEY")
            if not self.fail_silently:
                raise ValueError("RESEND_API_KEY is not set")
            return 0

        from resend.emails._emails import Emails as EmailsClass

        sent_count = 0
        for message in email_messages:
            try:
                logger.info(f"📧 Sending email to {message.to} - Subject: {message.subject}")

                # Determine if HTML or plain text
                html_content = None
                text_content = message.body

                # Check for HTML alternative
                if hasattr(message, "alternatives"):
                    for content, mimetype in message.alternatives:
                        if mimetype == "text/html":
                            html_content = content
                            break

                # Build email params as dict
                params = {
                    "from": message.from_email,
                    "to": message.to,
                    "subject": message.subject,
                }

                if html_content:
                    params["html"] = html_content
                else:
                    params["text"] = text_content

                # Send via Resend (API key read from RESEND_API_KEY env var)
                response = EmailsClass.send(params)
                logger.info(f"✅ Email sent successfully: {response}")
                sent_count += 1
            except Exception as e:
                logger.error(f"❌ Failed to send email: {str(e)}", exc_info=True)
                if not self.fail_silently:
                    raise

        return sent_count
