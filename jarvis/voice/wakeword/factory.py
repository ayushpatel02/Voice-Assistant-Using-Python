"""Select the configured wake-word detector."""

from __future__ import annotations

from ...config.settings import Settings
from .base import WakeWordDetector


def build_wakeword(settings: Settings) -> WakeWordDetector:
    name = getattr(settings.voice, "wakeword", "openwakeword").lower()
    if name in {"fake", "test"}:
        from .base import FakeWakeWord

        return FakeWakeWord()
    if name in {"openwakeword", "oww"}:
        from .openwakeword_det import OpenWakeWordDetector

        model = "hey_jarvis" if "jarvis" in settings.voice.wake_word.lower() else "alexa"
        return OpenWakeWordDetector(model_name=model)
    if name == "porcupine":
        from .porcupine_det import PorcupineDetector

        return PorcupineDetector(keyword=settings.voice.wake_word.lower())
    raise ValueError(f"Unknown wake-word provider: {name!r}")
