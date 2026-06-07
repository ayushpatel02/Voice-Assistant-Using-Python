"""openWakeWord detector (default): open-source, no key, runs in real time."""

from __future__ import annotations

from typing import Any

from .base import WakeWordDetector


class OpenWakeWordDetector(WakeWordDetector):
    frame_size = 1280  # 80 ms at 16 kHz, as openWakeWord expects

    def __init__(self, model_name: str = "hey_jarvis", threshold: float = 0.5) -> None:
        self.model_name = model_name
        self.threshold = threshold
        self._model = None

    def _load(self):
        if self._model is None:
            from openwakeword.model import Model

            self._model = Model(wakeword_models=[self.model_name])
        return self._model

    def detect(self, frame: Any) -> bool:
        model = self._load()
        scores = model.predict(frame)
        for name, score in scores.items():
            if self.model_name in name and score >= self.threshold:
                return True
        return False
