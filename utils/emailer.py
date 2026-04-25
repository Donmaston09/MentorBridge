"""SMTP email helpers for OTP and booking invites."""

from __future__ import annotations

import os
import smtplib
import uuid
from datetime import datetime, timedelta
from email.message import EmailMessage


SMTP_HOST = os.getenv("SMTP_HOST", "").strip()
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "").strip()
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "").strip()
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "").strip()
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "MentorBridge").strip()
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() in {"1", "true", "yes"}
APP_BASE_URL = os.getenv("APP_BASE_URL", "").strip()


def email_is_configured() -> bool:
    return all([SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM_EMAIL])


def send_otp_email(recipient_email: str, recipient_name: str, otp_code: str) -> tuple[bool, str]:
    subject = "Your MentorBridge verification code"
    body = (
        f"Hello {recipient_name},\n\n"
        f"Your MentorBridge verification code is: {otp_code}\n\n"
        "Enter this 6-digit code in the app to activate your mentor profile.\n\n"
        "If you did not request this, you can ignore this email.\n\n"
        "MentorBridge"
    )
    return _send_email(subject, body, [recipient_email])


def send_booking_invites(student: dict, mentor: dict, event: dict) -> tuple[bool, str]:
    recipients = [student.get("email", ""), mentor.get("email", "")]
    recipients = [email for email in recipients if email]
    if len(recipients) < 2:
        return False, "Missing student or mentor email address."

    subject = f"MentorBridge session invite: {event.get('date')} at {event.get('time')}"
    body = (
        f"Hello {student.get('name', 'student')} and {mentor.get('name', 'mentor')},\n\n"
        "Your MentorBridge session has been confirmed.\n\n"
        f"Date: {event.get('date')}\n"
        f"Time: {event.get('time')}\n"
        f"Duration: {event.get('duration')}\n"
        f"Platform: {event.get('platform')}\n"
        f"Meeting link: {event.get('link')}\n"
    )
    if event.get("note"):
        body += f"\nStudent note: {event.get('note')}\n"
    if APP_BASE_URL:
        body += f"\nOpen MentorBridge: {APP_BASE_URL}\n"
    body += "\nA calendar invite is attached.\n\nMentorBridge"

    invite_bytes = _build_ics_invite(student, mentor, event)
    return _send_email(
        subject,
        body,
        recipients,
        attachments=[
            (
                "mentorbridge-session.ics",
                invite_bytes,
                "text",
                "calendar",
            )
        ],
    )


def _send_email(
    subject: str,
    body: str,
    recipients: list[str],
    attachments: list[tuple[str, bytes, str, str]] | None = None,
) -> tuple[bool, str]:
    if not email_is_configured():
        return False, "SMTP is not configured."

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
    message["To"] = ", ".join(recipients)
    message.set_content(body)

    for filename, content, maintype, subtype in attachments or []:
        message.add_attachment(content, maintype=maintype, subtype=subtype, filename=filename)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            if SMTP_USE_TLS:
                server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(message)
    except Exception as exc:
        return False, str(exc)

    return True, "Email sent."


def _build_ics_invite(student: dict, mentor: dict, event: dict) -> bytes:
    start = datetime.strptime(f"{event['date']} {event['time']}", "%Y-%m-%d %H:%M")
    duration = timedelta(minutes=30 if event.get("duration") == "30 minutes" else 60)
    end = start + duration
    uid = f"{uuid.uuid4()}@mentorbridge.app"
    dtstamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//MentorBridge//Session Invite//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:REQUEST",
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{dtstamp}",
        f"DTSTART:{start.strftime('%Y%m%dT%H%M%S')}",
        f"DTEND:{end.strftime('%Y%m%dT%H%M%S')}",
        f"SUMMARY:{event.get('title', 'MentorBridge Session')}",
        (
            "DESCRIPTION:"
            f"MentorBridge session between {student.get('name', 'Student')} and "
            f"{mentor.get('name', 'Mentor')}. Join here: {event.get('link', '')}"
        ),
        f"LOCATION:{event.get('link', '')}",
        "STATUS:CONFIRMED",
        "END:VEVENT",
        "END:VCALENDAR",
    ]
    return "\r\n".join(lines).encode("utf-8")
