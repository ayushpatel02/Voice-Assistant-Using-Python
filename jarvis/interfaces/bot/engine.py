"""Transport-agnostic chat-bot brain.

The engine turns an inbound chat message into a reply by delegating to the same
``Assistant.handle`` the CLI, voice, and web faces use. It owns nothing about
Telegram/Discord wire formats — a transport adapter feeds it ``(chat_id, text,
user)`` and renders whatever string it returns. Each chat keeps its own
``Session`` so conversations don't bleed into one another.
"""

from __future__ import annotations

import logging

from ...core.assistant import Assistant
from ...core.session import Session

log = logging.getLogger(__name__)

_HELP = (
    "🤖 *Jarvis* at your service, Boss.\n\n"
    "Just talk to me normally — I can tell the time, take notes, set reminders, "
    "search the web, and more.\n\n"
    "*Commands*\n"
    "/help — show this message\n"
    "/reset — forget this conversation\n"
    "/whoami — show your chat id"
)


class BotEngine:
    """Maps inbound messages to assistant replies, one session per chat."""

    def __init__(self, assistant: Assistant, *, owner_id: str | None = None) -> None:
        self.assistant = assistant
        #: When set, only this user id may talk to the bot (a private assistant).
        self.owner_id = str(owner_id) if owner_id else None
        self._sessions: dict[str, Session] = {}

    def session_for(self, chat_id: str) -> Session:
        key = str(chat_id)
        if key not in self._sessions:
            session = self.assistant.new_session("bot")
            session.session_id = key
            session.user_id = key
            self._sessions[key] = session
        return self._sessions[key]

    def reset(self, chat_id: str) -> None:
        self._sessions.pop(str(chat_id), None)

    def handle_message(
        self,
        chat_id: str,
        text: str,
        *,
        user_name: str | None = None,
        user_id: str | None = None,
    ) -> str:
        """Return the reply for one inbound message (a command or free text)."""
        if self.owner_id and str(user_id) != self.owner_id:
            log.info("Rejected message from non-owner user_id=%s", user_id)
            return "🔒 Sorry, this Jarvis is private."

        text = (text or "").strip()
        if not text:
            return ""
        if text.startswith("/"):
            return self._command(chat_id, text)

        session = self.session_for(chat_id)
        try:
            return self.assistant.handle(text, session).text
        except Exception:  # pragma: no cover - defensive: never crash the loop
            log.exception("Assistant failed handling a bot message")
            return "⚠️ Something went wrong on my end. Please try again."

    def _command(self, chat_id: str, text: str) -> str:
        # Telegram sends "/cmd@BotName args" in groups; strip the @mention.
        word = text.split()[0].lstrip("/")
        cmd = word.split("@", 1)[0].lower()

        if cmd in ("start", "help"):
            return _HELP
        if cmd == "reset":
            self.reset(chat_id)
            return "🧹 Done — I've cleared our conversation."
        if cmd == "whoami":
            return f"Your chat id is `{chat_id}`."
        return f"Unknown command /{cmd}. Try /help."
