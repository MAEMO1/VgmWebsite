"""Utility functions for sending transactional emails."""

from __future__ import annotations

import logging
import os
import smtplib
from email.message import EmailMessage
from typing import Optional

logger = logging.getLogger(__name__)


def _smtp_config() -> Optional[dict[str, str]]:
    host = os.getenv('SMTP_HOST')
    sender = os.getenv('SMTP_SENDER') or os.getenv('SMTP_USERNAME')

    if not host or not sender:
        return None

    return {
        'host': host,
        'port': int(os.getenv('SMTP_PORT', '587')),
        'username': os.getenv('SMTP_USERNAME'),
        'password': os.getenv('SMTP_PASSWORD'),
        'sender': sender,
        'use_tls': os.getenv('SMTP_USE_TLS', 'true').lower() not in {'false', '0', 'no'},
    }


def send_email(subject: str, to_email: str, body: str) -> bool:
    """Send an email using the configured SMTP server."""
    config = _smtp_config()
    if not config:
        logger.warning("SMTP is not configured; skipping email to %s", to_email)
        return False

    message = EmailMessage()
    message['Subject'] = subject
    message['From'] = config['sender']
    message['To'] = to_email
    message.set_content(body)

    try:
        with smtplib.SMTP(config['host'], config['port']) as smtp:
            if config['use_tls']:
                smtp.starttls()
            if config['username'] and config['password']:
                smtp.login(config['username'], config['password'])
            smtp.send_message(message)
        logger.info("Password reset email delivered to %s", to_email)
        return True
    except Exception as exc:  # pragma: no cover - log unexpected failures
        logger.exception("Failed to send email to %s: %s", to_email, exc)
        return False


def send_password_reset_email(to_email: str, reset_url: str, locale: str = 'nl') -> bool:
    """Send a password reset email in the provided locale."""
    if locale.startswith('nl'):
        subject = 'Wachtwoord resetten voor VGM'
        body = (
            "Assalaam alaikum,\n\n"
            "We ontvingen een verzoek om uw wachtwoord te resetten."
            " Klik op onderstaande link om een nieuw wachtwoord in te stellen:\n\n"
            f"{reset_url}\n\n"
            "Als u dit verzoek niet heeft gedaan, kunt u deze e-mail negeren."
        )
    else:
        subject = 'Reset your VGM account password'
        body = (
            "Assalaam alaikum,\n\n"
            "We received a request to reset your password."
            " Click the link below to choose a new password:\n\n"
            f"{reset_url}\n\n"
            "If you did not request this, you can safely ignore this email."
        )

    return send_email(subject, to_email, body)


__all__ = ['send_email', 'send_password_reset_email']
