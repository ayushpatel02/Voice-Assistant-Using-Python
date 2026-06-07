"""Microphone capture and audio playback.

Wraps ``sounddevice`` (PortAudio) lazily so the package imports without the
voice extras. All audio-dependency pain lives in this one module. Recording
produces a temp WAV file so the rest of the pipeline is format-uniform.
"""

from __future__ import annotations

import logging
import tempfile
import wave
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)


class AudioIO:
    def __init__(self, sample_rate: int = 16000, channels: int = 1) -> None:
        self.sample_rate = sample_rate
        self.channels = channels

    def _sd(self) -> Any:
        try:
            import sounddevice as sd

            return sd
        except Exception as exc:  # pragma: no cover - needs audio libs
            raise RuntimeError(
                "Audio support requires the voice extras and PortAudio. "
                "Install with: pip install 'jarvis-assistant[voice]'"
            ) from exc

    def record_seconds(self, seconds: float) -> str:
        """Record a fixed duration to a temp WAV and return its path."""
        sd = self._sd()
        import numpy as np

        frames = sd.rec(
            int(seconds * self.sample_rate),
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="int16",
        )
        sd.wait()
        return self._write_wav(np.asarray(frames))

    def record_until_silence(
        self,
        max_seconds: float = 12.0,
        silence_rms: float = 500.0,
        silence_window: float = 1.2,
    ) -> str:
        """Record until ~``silence_window`` seconds of quiet, then stop."""
        sd = self._sd()
        import numpy as np

        block = int(self.sample_rate * 0.1)  # 100 ms blocks
        collected: list[Any] = []
        silent_for = 0.0
        with sd.InputStream(
            samplerate=self.sample_rate, channels=self.channels, dtype="int16"
        ) as stream:
            for _ in range(int(max_seconds / 0.1)):
                data, _overflow = stream.read(block)
                arr = np.asarray(data)
                collected.append(arr)
                rms = float(np.sqrt(np.mean(arr.astype("float64") ** 2)) or 0.0)
                silent_for = silent_for + 0.1 if rms < silence_rms else 0.0
                if silent_for >= silence_window and len(collected) > silence_window * 10:
                    break
        return self._write_wav(np.concatenate(collected))

    def stream_frames(self, frame_size: int):
        """Yield int16 audio frames of ``frame_size`` samples indefinitely.

        Used by wake-word detectors, which process fixed-size frames.
        """
        sd = self._sd()
        import numpy as np

        with sd.InputStream(
            samplerate=self.sample_rate, channels=self.channels, dtype="int16"
        ) as stream:
            while True:
                data, _overflow = stream.read(frame_size)
                yield np.asarray(data).reshape(-1)

    def play_file(self, path: str) -> None:
        """Play a WAV file through the default output device."""
        sd = self._sd()
        import numpy as np

        with wave.open(path, "rb") as wf:
            rate = wf.getframerate()
            frames = wf.readframes(wf.getnframes())
        audio = np.frombuffer(frames, dtype="int16")
        sd.play(audio, rate)
        sd.wait()

    def _write_wav(self, frames: Any) -> str:
        tmp = Path(tempfile.mkstemp(suffix=".wav", prefix="jarvis_")[1])
        with wave.open(str(tmp), "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # int16
            wf.setframerate(self.sample_rate)
            wf.writeframes(frames.tobytes())
        return str(tmp)
