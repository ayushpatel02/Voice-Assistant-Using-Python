"""Select the configured STT provider."""

from __future__ import annotations

from ...config.settings import Settings
from .base import STTProvider


def build_stt(settings: Settings) -> STTProvider:
    name = settings.voice.stt.lower()
    if name in {"fake", "test"}:
        from .base import FakeSTT

        return FakeSTT()
    if name in {"faster_whisper", "whisper"}:
        from .faster_whisper_stt import FasterWhisperSTT

        return FasterWhisperSTT()
    if name == "vosk":
        from .vosk_stt import VoskSTT

        return VoskSTT()
    if name in {"openai", "cloud_whisper"}:
        from .openai_stt import OpenAISTT

        return OpenAISTT()
    raise ValueError(f"Unknown STT provider: {settings.voice.stt!r}")
