"""Django email backend for Resend"""
import os
from django.core.mail.backends.base import BaseEmailBackend
from resend import Resend


class ResendBackend(BaseEmailBackend):
    """Send emails via Resend API"""

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = os.environ.get("RESEND_API_KEY", "")
        self.client = Resend(api_key=self.api_key) if self.api_key else None

    def send_messages(self, email_messages):
        """Send one or more EmailMessage objects and return the number sent."""
        if not self.client:
            if not self.fail_silently:
                raise ValueError("RESEND_API_KEY is not set")
            return 0

        sent_count = 0
        for message in email_messages:
            try:
                # Build email params
                params = {
                    "from": message.from_email,
                    "to": message.to,
                    "subject": message.subject,
                    "html": message.body if message.content_subtype == "html" else None,
                    "text": message.body if message.content_subtype != "html" else None,
                }

                # Check for HTML alternative
                if hasattr(message, "alternatives"):
                    for content, mimetype in message.alternatives:
                        if mimetype == "text/html":
                            params["html"] = content
                            break

                # Send via Resend
                self.client.emails.send(params)
                sent_count += 1
            except Exception as e:
                if not self.fail_silently:
                    raise

        return sent_count
