"""Wake-word detector interface.

A detector consumes fixed-size int16 audio frames and fires when the wake word
("Jarvis") is heard. ``wait_for_wake`` blocks until that happens.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class WakeWordDetector(ABC):
    #: Samples per frame this detector expects (model-dependent).
    frame_size: int = 1280

    @abstractmethod
    def detect(self, frame: Any) -> bool:
        """Return True if the wake word is present in this frame."""
        raise NotImplementedError

    def wait_for_wake(self, audio_io: Any) -> None:
        for frame in audio_io.stream_frames(self.frame_size):
            if self.detect(frame):
                return


class FakeWakeWord(WakeWordDetector):
    """Fires after a fixed number of frames; used for mic-free tests."""

    frame_size = 4

    def __init__(self, fire_after: int = 1) -> None:
        self.fire_after = fire_after
        self.seen = 0

    def detect(self, frame: Any) -> bool:
        self.seen += 1
        return self.seen >= self.fire_after
