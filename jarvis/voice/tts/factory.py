"""Select the configured TTS provider."""

from __future__ import annotations

from ...config.settings import Settings
from .base import TTSProvider


def build_tts(settings: Settings) -> TTSProvider:
    name = settings.voice.tts.lower()
    voice = settings.voice.voice_name
    if name in {"fake", "test"}:
        from .base import FakeTTS

        return FakeTTS()
    if name in {"edge", "edge_tts"}:
        from .edge_tts import EdgeTTS

        return EdgeTTS(voice=voice)
    if name == "piper":
        from .piper_tts import PiperTTS

        return PiperTTS()
    if name in {"elevenlabs", "eleven"}:
        from .elevenlabs_tts import ElevenLabsTTS

        return ElevenLabsTTS()
    raise ValueError(f"Unknown TTS provider: {settings.voice.tts!r}")
