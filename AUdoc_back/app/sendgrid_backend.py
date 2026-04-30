"""Django email backend for SendGrid"""
import os
import logging
from django.core.mail.backends.base import BaseEmailBackend


logger = logging.getLogger(__name__)


class SendGridBackend(BaseEmailBackend):
    """Send emails via SendGrid API"""

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = os.environ.get("SENDGRID_API_KEY", "")

        if not self.api_key:
            logger.error("❌ SENDGRID_API_KEY is not set in environment variables")

    def send_messages(self, email_messages):
        """Send one or more EmailMessage objects and return the number sent."""
        if not self.api_key:
            logger.error("❌ SendGrid API key not configured - missing SENDGRID_API_KEY")
            if not self.fail_silently:
                raise ValueError("SENDGRID_API_KEY is not set")
            return 0

        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail, Email, To, Content

        sg = SendGridAPIClient(self.api_key)
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

                # Build email using SendGrid Mail class
                from_email = Email(message.from_email)
                to_emails = [To(email) for email in message.to]

                if html_content:
                    content = Content("text/html", html_content)
                else:
                    content = Content("text/plain", text_content)

                mail = Mail(
                    from_email=from_email,
                    to_emails=to_emails,
                    subject=message.subject,
                    plain_text_content=text_content if not html_content else None,
                    html_content=html_content,
                )

                # Send via SendGrid
                response = sg.send(mail)
                logger.info(f"✅ Email sent successfully: Status {response.status_code}")
                sent_count += 1
            except Exception as e:
                logger.error(f"❌ Failed to send email: {str(e)}", exc_info=True)
                if not self.fail_silently:
                    raise

        return sent_count
