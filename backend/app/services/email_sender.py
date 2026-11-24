"""Send contact-form submissions by email.

Configuration comes from environment variables so no credentials live in the
repo: SMTP_HOST, SMTP_PORT (default 587), SMTP_USER, SMTP_PASSWORD, and
CONTACT_RECIPIENT (who receives the messages; defaults to SMTP_USER).
"""
import os
import smtplib
from email.message import EmailMessage


class EmailNotConfigured(RuntimeError):
    """Raised when the SMTP settings needed to send mail are missing."""


def send_contact_email(sender_email: str, message: str) -> None:
    """Email one contact-form message to the team, or raise on failure."""
    host = os.getenv("SMTP_HOST")
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    recipient = os.getenv("CONTACT_RECIPIENT") or user
    if not (host and user and password and recipient):
        raise EmailNotConfigured("SMTP settings are not configured")
    port = int(os.getenv("SMTP_PORT", "587"))

    msg = EmailMessage()
    msg["Subject"] = "New BoostSEO contact message"
    msg["From"] = user
    msg["To"] = recipient
    msg["Reply-To"] = sender_email          # replies go to the visitor
    msg.set_content(f"From: {sender_email}\n\n{message}")

    with smtplib.SMTP(host, port, timeout=10) as smtp:
        smtp.starttls()
        smtp.login(user, password)
        smtp.send_message(msg)
