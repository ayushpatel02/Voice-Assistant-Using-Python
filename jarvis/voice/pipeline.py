"""The voice loop: wake word -> record -> STT -> core -> TTS -> play.

The per-turn logic is split out as :meth:`respond_to_audio` so it can be
exercised from a WAV file with no microphone (see the tests).
"""

from __future__ import annotations

import logging
import tempfile
from dataclasses import dataclass
from pathlib import Path

from ..core.assistant import Assistant
from ..core.response import Response
from ..core.session import Session
from .audio_io import AudioIO
from .stt.base import STTProvider
from .tts.base import TTSProvider
from .wakeword.base import WakeWordDetector

log = logging.getLogger(__name__)


@dataclass
class Turn:
    heard: str
    response: Response | None
    audio_path: str | None


class VoicePipeline:
    def __init__(
        self,
        assistant: Assistant,
        session: Session,
        stt: STTProvider,
        tts: TTSProvider,
        audio: AudioIO,
        wakeword: WakeWordDetector,
    ) -> None:
        self.assistant = assistant
        self.session = session
        self.stt = stt
        self.tts = tts
        self.audio = audio
        self.wakeword = wakeword

    def respond_to_audio(self, wav_path: str) -> Turn:
        """Transcribe a clip, get the assistant's reply, and render it to audio."""
        heard = self.stt.transcribe_file(wav_path).strip()
        if not heard:
            return Turn(heard="", response=None, audio_path=None)
        response = self.assistant.handle(heard, self.session)
        out_path = str(
            Path(tempfile.mkstemp(suffix=self.tts.suffix, prefix="jarvis_say_")[1])
        )
        self.tts.synthesize_to_file(response.for_speech, out_path)
        return Turn(heard=heard, response=response, audio_path=out_path)

    def take_turn(self) -> Turn:
        """One live turn: record from the mic, respond, and play it back."""
        wav_path = self.audio.record_until_silence()
        turn = self.respond_to_audio(wav_path)
        if turn.audio_path:
            self.audio.play_file(turn.audio_path)
        return turn

    def speak(self, text: str) -> None:
        out = str(Path(tempfile.mkstemp(suffix=self.tts.suffix, prefix="jarvis_")[1]))
        self.tts.synthesize_to_file(text, out)
        self.audio.play_file(out)

    def run(self) -> None:
        """Block forever: wait for the wake word, then take a turn."""
        log.info("Listening for wake word '%s'...", self.assistant.settings.voice.wake_word)
        print(f"Listening for '{self.assistant.settings.voice.wake_word}'... (Ctrl+C to stop)")
        while True:
            self.wakeword.wait_for_wake(self.audio)
            log.info("Wake word detected.")
            turn = self.take_turn()
            if turn.heard:
                print(f"You said: {turn.heard}")
                if turn.response:
                    print(f"Jarvis: {turn.response.text}")
