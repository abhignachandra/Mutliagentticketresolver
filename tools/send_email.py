"""SMTP email tool used by NotificationAgent to escalate unresolved tickets."""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()

# Read SMTP config from .env so nothing is hardcoded.
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")  # Gmail App Password
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "sandeshhase15@gmail.com")


def _send_email(to_email: str, subject: str, body: str) -> tuple[bool, str]:
    """Low-level send. Returns (success, message)."""
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        return False, "SENDER_EMAIL / SENDER_PASSWORD not configured in .env"

    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())

        return True, f"Email sent to {to_email}"
    except Exception as e:
        return False, f"SMTP error: {e}"


def escalate_ticket_with_email(issue: str) -> str:
    """Escalate an unresolved IT issue by emailing the support team.

    Args:
        issue: The full text of the IT issue that could not be resolved
            by the knowledge base.

    Returns:
        A short human-readable status string describing whether the email
        was sent (this is what the NotificationAgent will read back).
    """
    subject = "Escalation: Unresolved IT Issue"
    body = (
        "Hello IT Support Team,\n\n"
        "The following issue reported by a user could not be resolved by the AI Assistant:\n\n"
        f"\"{issue}\"\n\n"
        "Please investigate and take further action.\n\n"
        "Regards,\n"
        "AI Notification Agent\n"
    )

    success, detail = _send_email(to_email=SUPPORT_EMAIL, subject=subject, body=body)
    if success:
        return f"Escalation email sent to {SUPPORT_EMAIL}. ({detail})"
    return f"Escalation email FAILED: {detail}"