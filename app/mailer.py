"""Gmail SMTP email sender for report attachments."""

from __future__ import annotations

import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()


def send_report(
    recipients: list[str],
    subject: str,
    body: str,
    attachments: list[str] | None = None,
) -> dict:
    """
    Send an email with report attachments via Gmail SMTP.

    Loads from .env:
      SENDER_EMAIL   → Gmail address to send from
      APP_PASSWORD   → Gmail App Password (NOT your Gmail login password)

    Args:
      recipients:  list of email addresses to send to
      subject:     email subject line
      body:        plain text email body
      attachments: list of file paths to attach (PDF and/or Excel)

    Returns:
      {"success": True, "message": "Sent to N recipients"}
      or {"success": False, "error": ""}
    """
    if attachments is None:
        attachments = []

    sender = os.environ.get("SENDER_EMAIL", "").strip()
    password = os.environ.get("APP_PASSWORD", "").strip()

    if not sender or not password:
        return {
            "success": False,
            "error": "Missing SENDER_EMAIL or APP_PASSWORD in environment (.env).",
        }

    if not recipients:
        return {"success": False, "error": "No recipients provided."}

    try:
        message = MIMEMultipart("mixed")
        message["From"] = sender
        message["To"] = ", ".join(recipients)
        message["Subject"] = subject

        message.attach(MIMEText(body, "plain"))

        for file_path in attachments:
            if not file_path or not os.path.isfile(file_path):
                continue
            with open(file_path, "rb") as attachment_file:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment_file.read())
            encoders.encode_base64(part)
            filename = os.path.basename(file_path)
            part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
            message.attach(part)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, recipients, message.as_string())

        for addr in recipients:
            print(f"✓ Email sent to: {addr}")

        return {"success": True, "message": f"Sent to {len(recipients)} recipients"}

    except Exception as exc:  # noqa: BLE001 — return structured error to caller
        return {"success": False, "error": str(exc)}
