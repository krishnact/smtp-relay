# sendgrid_provider.py
import logging
from email.message import EmailMessage
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from .provider_base import EmailProvider
import os

logger = logging.getLogger(__name__)

class SendGridProvider(EmailProvider):
    def __init__(self, api_key):
        self.sg = SendGridAPIClient(api_key)

    def name(self):
        return "sendgrid"

    def send(self, message: EmailMessage) -> bool:
        body_plain = message.get_body(preferencelist=('plain'))
        body_html = message.get_body(preferencelist=('html'))
        text = body_plain.get_content() if body_plain else ""
        html = body_html.get_content() if body_html else ""

        mail = Mail(
                from_email=(os.getenv("RELAY_FROM_EMAIL", message["From"]), os.getenv("RELAY_FROM_NAME", "")),
                to_emails=message["To"],
                subject=message["Subject"],
                plain_text_content=body_plain,
                html_content=html)
        try:
            response = self.sg.send(mail)
            logger.info(f"SendGrid: status {response.status_code}")
            return 200 <= response.status_code < 300
        except Exception as e:
            logger.error(f"SendGrid send error: {e}")
            return False
