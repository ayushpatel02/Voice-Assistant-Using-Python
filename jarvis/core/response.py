"""The assistant's reply, independent of how it will be rendered."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Response:
    text: str
    #: Optional alternate phrasing optimized for speech (falls back to ``text``).
    speech_text: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)

    @property
    def for_speech(self) -> str:
        return self.speech_text or self.text
