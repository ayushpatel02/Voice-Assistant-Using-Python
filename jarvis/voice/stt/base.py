"""Speech-to-text provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod


class STTProvider(ABC):
    @abstractmethod
    def transcribe_file(self, wav_path: str) -> str:
        """Transcribe a WAV file to text."""
        raise NotImplementedError


class FakeSTT(STTProvider):
    """Returns canned text; used for mic-free tests."""

    def __init__(self, text: str = "what time is it") -> None:
        self.text = text
        self.calls: list[str] = []

    def transcribe_file(self, wav_path: str) -> str:
        self.calls.append(wav_path)
        return self.text
