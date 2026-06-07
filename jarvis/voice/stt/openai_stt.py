"""Cloud Whisper STT via the OpenAI API (accuracy without local compute)."""

from __future__ import annotations

from ...config.settings import Settings
from .base import STTProvider


class OpenAISTT(STTProvider):
    def __init__(self, model: str = "whisper-1") -> None:
        self.model = model

    def transcribe_file(self, wav_path: str) -> str:
        key = Settings.secret("OPENAI_API_KEY")
        if not key:
            return ""
        from openai import OpenAI

        client = OpenAI(api_key=key)
        with open(wav_path, "rb") as fh:
            result = client.audio.transcriptions.create(model=self.model, file=fh)
        return (result.text or "").strip()
