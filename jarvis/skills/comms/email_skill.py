"""Send email via SMTP. Credentials come from the environment only."""

from __future__ import annotations

import smtplib
from email.message import EmailMessage

from ...config.settings import Settings
from ..base import Context, Skill, Tool


class EmailSkill(Skill):
    name = "email"
    required_secrets = ("JARVIS_EMAIL", "JARVIS_EMAIL_PASSWORD")

    def tools(self) -> list[Tool]:
        return [
            Tool(
                name="send_email",
                description="Send an email. If recipient is omitted, sends to the owner.",
                parameters={
                    "type": "object",
                    "properties": {
                        "to": {"type": "string", "description": "Recipient email address."},
                        "subject": {"type": "string"},
                        "body": {"type": "string"},
                    },
                    "required": ["body"],
                },
                handler=self._send,
            )
        ]

    def _send(self, args: dict, ctx: Context) -> str:
        address = Settings.secret("JARVIS_EMAIL")
        password = Settings.secret("JARVIS_EMAIL_PASSWORD")
        if not address or not password:
            return "Email is not configured (set JARVIS_EMAIL and JARVIS_EMAIL_PASSWORD)."

        to = (args.get("to") or address).strip()
        subject = (args.get("subject") or "Message from Jarvis").strip()
        body = args.get("body", "").strip()
        if not body:
            return "There's no message body to send."

        message = EmailMessage()
        message["From"] = address
        message["To"] = to
        message["Subject"] = subject
        message.set_content(body)

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.ehlo()
                server.starttls()
                server.login(address, password)
                server.send_message(message)
        except Exception as exc:
            return f"Could not send the email: {exc}"
        return f"Email sent to {to}."
