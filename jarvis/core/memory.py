"""Conversation memory with a simple sliding window.

Stores the running list of turns and trims old ones so the context handed to
the model stays bounded. Only user/assistant text turns are kept here; the
within-turn tool-call exchange lives transiently inside the router loop.
"""

from __future__ import annotations

from ..llm.base import Message


class Memory:
    def __init__(self, max_messages: int = 40) -> None:
        self.max_messages = max_messages
        self._messages: list[Message] = []

    def add_user(self, text: str) -> None:
        self._messages.append(Message(role="user", content=text))
        self._trim()

    def add_assistant(self, text: str) -> None:
        self._messages.append(Message(role="assistant", content=text))
        self._trim()

    def history(self) -> list[Message]:
        return list(self._messages)

    def clear(self) -> None:
        self._messages.clear()

    def _trim(self) -> None:
        if len(self._messages) > self.max_messages:
            self._messages = self._messages[-self.max_messages :]
