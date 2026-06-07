"""Porcupine detector: higher accuracy, needs PORCUPINE_ACCESS_KEY.

"jarvis" is a Porcupine built-in keyword, so no custom model file is required.
"""

from __future__ import annotations

from typing import Any

from ...config.settings import Settings
from .base import WakeWordDetector


class PorcupineDetector(WakeWordDetector):
    def __init__(self, keyword: str = "jarvis") -> None:
        self.keyword = keyword
        self._handle = None
        self.frame_size = 512  # overwritten with porcupine.frame_length on load

    def _load(self):
        if self._handle is None:
            import pvporcupine

            key = Settings.secret("PORCUPINE_ACCESS_KEY")
            if not key:
                raise RuntimeError("Porcupine needs PORCUPINE_ACCESS_KEY.")
            self._handle = pvporcupine.create(access_key=key, keywords=[self.keyword])
            self.frame_size = self._handle.frame_length
        return self._handle

    def detect(self, frame: Any) -> bool:
        handle = self._load()
        return handle.process(frame) >= 0
