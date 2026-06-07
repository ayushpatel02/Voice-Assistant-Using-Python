"""Vosk STT — lightweight, offline, streaming-friendly (good for low-power)."""

from __future__ import annotations

import json
import wave

from .base import STTProvider


class VoskSTT(STTProvider):
    def __init__(self, model_path: str | None = None) -> None:
        self.model_path = model_path
        self._model = None

    def _load(self):
        if self._model is None:
            from vosk import Model

            self._model = Model(self.model_path) if self.model_path else Model(lang="en-us")
        return self._model

    def transcribe_file(self, wav_path: str) -> str:
        from vosk import KaldiRecognizer

        model = self._load()
        with wave.open(wav_path, "rb") as wf:
            rec = KaldiRecognizer(model, wf.getframerate())
            rec.SetWords(True)
            text_parts: list[str] = []
            while True:
                data = wf.readframes(4000)
                if not data:
                    break
                if rec.AcceptWaveform(data):
                    text_parts.append(json.loads(rec.Result()).get("text", ""))
            text_parts.append(json.loads(rec.FinalResult()).get("text", ""))
        return " ".join(p for p in text_parts if p).strip()
