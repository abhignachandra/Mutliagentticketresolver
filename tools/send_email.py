"""SMTP email tool used by NotificationAgent to escalate unresolved tickets.

Hardened version:
- Uses shared sanitize helpers from utility.sanitize
- PII-redacts log lines (utility.redact)
- Structured logging (utility.logging_config.get_logger)
- File-log fallback if SMTP fails — escalations.jsonl
- Optional ticket_id parameter for traceability
"""

import json
import os
import smtplib
import time
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv

from utility.guardrails import (
    clean_addr,
    clean_text,
    redact_for_log,
    redact_for_email,
    get_logger,
)

load_dotenv()

logger = get_logger(__name__)

SMTP_SERVER = (os.getenv("SMTP_SERVER") or "smtp.gmail.com").strip()
SMTP_PORT = int((os.getenv("SMTP_PORT") or "587").strip())
SENDER_EMAIL = clean_addr(os.getenv("SENDER_EMAIL", ""))
# Gmail App Passwords display as "xxxx xxxx xxxx xxxx" — Google uses NON-breaking
# spaces in that display, which copy-paste as \xa0 (not regular spaces). Strip
# ALL whitespace so the 16-char password ends up clean regardless of paste source.
SENDER_PASSWORD = clean_addr(os.getenv("SENDER_PASSWORD", ""))
SUPPORT_EMAIL = clean_addr(os.getenv("SUPPORT_EMAIL", ""))

_FALLBACK_LOG = Path(__file__).resolve().parent.parent / "escalations.jsonl"


def _send_email(to_email: str, subject: str, body: str) -> tuple[bool, str]:
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        return False, "SENDER_EMAIL / SENDER_PASSWORD not configured in .env"

    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)

        return True, f"Email sent to {to_email}"
    except Exception as e:
        return False, f"SMTP error: {e}"


def _append_fallback(ticket_id: str, issue: str, reason: str) -> bool:
    """Append an escalation to a local JSONL queue when SMTP fails."""
    try:
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "ticket_id": ticket_id,
            "issue": redact_for_email(issue),
            "smtp_error": reason,
        }
        with _FALLBACK_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return True
    except Exception as e:
        logger.error("fallback_log_failed error=%s", e)
        return False


def escalate_ticket_with_email(issue: str, ticket_id: str = "") -> str:
    """Escalate an unresolved IT issue.

    Tries SMTP first; if that fails, appends to escalations.jsonl so the
    ticket is never silently lost. Returns a short status string for the
    NotificationAgent to surface back to the UI.
    """
    safe_issue = clean_text(issue)
    safe_body = redact_for_email(safe_issue)
    tid = clean_text(ticket_id) or "N/A"

    subject = f"Escalation: Unresolved IT Issue ({tid})"
    body = (
        "Hello IT Support Team,\n\n"
        f"Ticket ID: {tid}\n\n"
        "The following issue reported by a user could not be resolved by the AI Assistant:\n\n"
        f"\"{safe_body}\"\n\n"
        "Please investigate and take further action.\n\n"
        "Regards,\n"
        "AI Notification Agent\n"
    )

    start = time.time()
    success, detail = _send_email(to_email=SUPPORT_EMAIL, subject=subject, body=body)
    elapsed = round(time.time() - start, 2)

    # Log only redacted metadata — never the full issue body.
    logger.info(
        "escalation ticket_id=%s success=%s elapsed_s=%s detail_preview=%s",
        tid,
        success,
        elapsed,
        redact_for_log(detail)[:120],
    )

    if success:
        return f"Escalation email sent to {SUPPORT_EMAIL}. (ticket {tid})"

    # SMTP failed — file-log fallback so the ticket isn't lost.
    saved = _append_fallback(tid, safe_issue, detail)
    if saved:
        logger.warning("escalation_fallback_saved ticket_id=%s", tid)
        return (
            f"Email delivery failed ({detail}). "
            f"Ticket {tid} saved to local queue for manual processing."
        )
    return f"Escalation FAILED and fallback queue unavailable: {detail}"
