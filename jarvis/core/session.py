"""Per-conversation state."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from .memory import Memory


@dataclass
class Session:
    #: Which interface this conversation came from ("cli", "voice", "web", ...).
    channel: str = "cli"
    #: Stable identifier for the user, when an interface can supply one.
    user_id: str = "boss"
    locale: str = "en-IN"
    session_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    memory: Memory = field(default_factory=Memory)
