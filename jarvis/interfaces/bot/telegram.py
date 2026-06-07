"""Telegram adapter for the bot engine.

Uses Telegram's HTTP Bot API with long polling and only the standard library —
no third-party dependency, just a bot token from @BotFather. Network access is
isolated to :meth:`_call`, so :meth:`process_update` (message in -> reply out)
is unit-testable without touching the network.
"""

from __future__ import annotations

import json
import logging
import urllib.request

from .engine import BotEngine

log = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, token: str, engine: BotEngine, *, poll_timeout: int = 30) -> None:
        self._base = f"https://api.telegram.org/bot{token}"
        self.engine = engine
        self.poll_timeout = poll_timeout

    # --- the only place that touches the network -------------------------
    def _call(self, method: str, payload: dict, timeout: float | None = None) -> dict:
        url = f"{self._base}/{method}"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"}
        )
        wait = timeout if timeout is not None else self.poll_timeout + 10
        with urllib.request.urlopen(req, timeout=wait) as resp:  # noqa: S310
            return json.loads(resp.read().decode("utf-8"))

    # --- outbound --------------------------------------------------------
    def send_message(self, chat_id: str, text: str) -> None:
        # Telegram caps messages at 4096 chars; chunk longer replies.
        for chunk in _chunks(text, 4096):
            self._call(
                "sendMessage",
                {"chat_id": chat_id, "text": chunk, "parse_mode": "Markdown"},
            )

    def send_typing(self, chat_id: str) -> None:
        try:
            self._call("sendChatAction", {"chat_id": chat_id, "action": "typing"})
        except Exception:  # pragma: no cover - cosmetic only
            pass

    # --- inbound ---------------------------------------------------------
    def process_update(self, update: dict) -> str | None:
        """Turn one Telegram update into a reply (and send it). Returns the text."""
        message = update.get("message") or update.get("edited_message")
        if not message:
            return None
        text = message.get("text")
        if not text:
            return None
        chat_id = str(message["chat"]["id"])
        sender = message.get("from", {})

        self.send_typing(chat_id)
        reply = self.engine.handle_message(
            chat_id,
            text,
            user_name=sender.get("first_name"),
            user_id=sender.get("id"),
        )
        if reply:
            self.send_message(chat_id, reply)
        return reply

    def run(self) -> None:
        offset = 0
        log.info("Telegram long-polling started")
        while True:
            try:
                result = self._call(
                    "getUpdates", {"offset": offset, "timeout": self.poll_timeout}
                )
            except Exception:
                log.exception("getUpdates failed; retrying shortly")
                _sleep(3)
                continue
            for update in result.get("result", []):
                offset = update["update_id"] + 1
                try:
                    self.process_update(update)
                except Exception:  # pragma: no cover - keep the loop alive
                    log.exception("Failed to process an update")


def _chunks(text: str, size: int):
    if not text:
        return
    for i in range(0, len(text), size):
        yield text[i : i + size]


def _sleep(seconds: float) -> None:  # pragma: no cover - thin wrapper, for tests
    import time

    time.sleep(seconds)
