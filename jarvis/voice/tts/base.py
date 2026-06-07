"""Text-to-speech provider interface."""

from __future__ import annotations

import wave
from abc import ABC, abstractmethod


class TTSProvider(ABC):
    #: File suffix the provider writes (so the pipeline/player knows the format).
    suffix: str = ".wav"

    @abstractmethod
    def synthesize_to_file(self, text: str, out_path: str) -> str:
        """Render ``text`` to an audio file at ``out_path``; return the path written."""
        raise NotImplementedError


class FakeTTS(TTSProvider):
    """Writes a tiny silent WAV so mic-free tests can assert output exists."""

    suffix = ".wav"

    def __init__(self) -> None:
        self.spoken: list[str] = []

    def synthesize_to_file(self, text: str, out_path: str) -> str:
        self.spoken.append(text)
        with wave.open(out_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(b"\x00\x00" * 1600)  # 0.1s of silence
        return out_path
