"""faster-whisper STT (default). Accurate, int8-friendly on CPU."""

from __future__ import annotations

from .base import STTProvider


class FasterWhisperSTT(STTProvider):
    def __init__(self, model_size: str = "base", compute_type: str = "int8") -> None:
        self.model_size = model_size
        self.compute_type = compute_type
        self._model = None

    def _load(self):
        if self._model is None:
            from faster_whisper import WhisperModel

            self._model = WhisperModel(self.model_size, compute_type=self.compute_type)
        return self._model

    def transcribe_file(self, wav_path: str) -> str:
        model = self._load()
        segments, _info = model.transcribe(wav_path)
        return " ".join(seg.text for seg in segments).strip()
