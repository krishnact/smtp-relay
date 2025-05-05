# email_relay.py
import os
import ssl
import logging
import asyncio
import signal
import sys
from datetime import datetime, timedelta
from email import message_from_bytes
from email.message import EmailMessage
from email.policy import default
from aiosmtpd.controller import Controller
from aiosmtpd.smtp import SMTP, Envelope, Session

from providers.sendgrid_provider import SendGridProvider
from providers.brevo_provider import BrevoProvider

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class ProviderManager:
    def __init__(self, config):
        self.providers = []
        self.usage = {}
        self.limits = {}
        logger.info(f"config: {config}")
        if "sendgrid" in config:
            self.providers.append(SendGridProvider(config["sendgrid"]["api_key"]))
            self.usage["sendgrid"] = []
            self.limits["sendgrid"] = config["sendgrid"]["daily_limit"]

        if "brevo" in config:
            self.providers.append(BrevoProvider(config["brevo"]["api_key"]))
            self.usage["brevo"] = []
            self.limits["brevo"] = config["brevo"]["daily_limit"]

        self.index = 0

    def clean_usage(self):
        now = datetime.utcnow()
        for key in self.usage:
            self.usage[key] = [t for t in self.usage[key] if now - t < timedelta(hours=24)]

    def get_provider(self):
        self.clean_usage()
        for _ in range(len(self.providers)):
            provider = self.providers[self.index]
            name = provider.name()
            if len(self.usage[name]) < self.limits[name]:
                return provider
            self.index = (self.index + 1) % len(self.providers)
        return None

    def record_usage(self, name):
        self.usage[name].append(datetime.utcnow())

class RelayHandler:
    def __init__(self, manager: ProviderManager):
        self.manager = manager

    async def handle_DATA(self, server: SMTP, session: Session, envelope: Envelope) -> str:
        message = message_from_bytes(envelope.content, policy=default)
        if not isinstance(message, EmailMessage):
            message = EmailMessage()
            message.set_content(envelope.content.decode())
            message["From"] = envelope.mail_from
            message["To"] = ", ".join(envelope.rcpt_tos)

        provider = self.manager.get_provider()
        if not provider:
            logger.warning("No available providers with quota")
            return "452 No available providers with quota"

        success = provider.send(message)
        if success:
            self.manager.record_usage(provider.name())
            return "250 Message accepted"
        else:
            return "451 Provider send failed"

def main():
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))

    cert_path = "/etc/ssl/private/server.pem"
    if not os.path.exists(cert_path):
        os.makedirs(os.path.dirname(cert_path), exist_ok=True)
        os.system(f"openssl req -new -x509 -days 7350 -nodes -subj '/CN=localhost' -out {cert_path} -keyout {cert_path}")
        logger.info("Generated self-signed certificate.")
    config = {}
    if os.environ.get("SENDGRID_API_KEY") is not None:
        config['sendgrid'] = {
            "api_key": os.environ.get("SENDGRID_API_KEY"),
            "daily_limit": int(os.environ.get("SENDGRID_DAILY_LIMIT", "200"))
        }
    if os.environ.get("BREVO_API_KEY") is not None:
        config['brevo'] = {
            "api_key": os.environ.get("BREVO_API_KEY"),
            "daily_limit": int(os.environ.get("BREVO_DAILY_LIMIT", "300"))
        }

    manager = ProviderManager(config)
    handler = RelayHandler(manager)
    controller = Controller(handler, hostname="0.0.0.0", port=465, ssl_context=ssl.create_default_context(ssl.Purpose.CLIENT_AUTH))
    controller.ssl_context.load_cert_chain(cert_path)
    controller.start()
    logger.info("SMTP relay with TLS started on port 465")
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()
