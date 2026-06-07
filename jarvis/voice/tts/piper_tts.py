"""Piper TTS — fully offline neural voice, outputs WAV (ideal for local/edge)."""

from __future__ import annotations

import wave

from .base import TTSProvider


class PiperTTS(TTSProvider):
    suffix = ".wav"

    def __init__(self, model_path: str | None = None) -> None:
        self.model_path = model_path
        self._voice = None

    def _load(self):
        if self._voice is None:
            from piper.voice import PiperVoice

            if not self.model_path:
                raise RuntimeError("Piper requires a voice model path (set in config).")
            self._voice = PiperVoice.load(self.model_path)
        return self._voice

    def synthesize_to_file(self, text: str, out_path: str) -> str:
        voice = self._load()
        with wave.open(out_path, "wb") as wf:
            voice.synthesize(text, wf)
        return out_path
