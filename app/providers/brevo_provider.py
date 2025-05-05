# brevo_provider.py
import logging
import requests
from email.message import EmailMessage
from .provider_base import EmailProvider
import os

logger = logging.getLogger(__name__)

class BrevoProvider(EmailProvider):
    def __init__(self, api_key):
        self.api_key = api_key

    def name(self):
        return "brevo"

    def send(self, message: EmailMessage) -> bool:
        body_plain = message.get_body(preferencelist=('plain'))
        body_html = message.get_body(preferencelist=('html'))
        text = body_plain.get_content() if body_plain else None
        html = body_html.get_content() if body_html else None
        html = html if html else text
        logger.info(f"Sending email with message {message['to']}, subject {message['Subject']}")
        data = {
            "sender": {
                "email": os.getenv("RELAY_FROM_EMAIL", message["From"]),
                "name": os.getenv("RELAY_FROM_NAME", "")
            },
            "to": [{"email": message["to"]}],
            "subject": message["Subject"],
            "textContent": text,
            "htmlContent": html,
        }

        headers = {
            "accept": "application/json",
            "api-key": self.api_key,
            "content-type": "application/json"
        }
        logger.debug(f"Sending email with headers {headers}")
        logger.debug(f"Sending email with data {data}")
        try:
            response = requests.post("https://api.brevo.com/v3/smtp/email",
                                     headers=headers, json=data)
            logger.info(f"Brevo: status {response.status_code}: {response.json()}")
            return 200 <= response.status_code < 300
        except Exception as e:
            logger.error(f"Brevo send error: {e}")
            return False
