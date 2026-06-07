"""ElevenLabs TTS — the cinematic upgrade. Requires ELEVENLABS_API_KEY."""

from __future__ import annotations

from ...config.settings import Settings
from .base import TTSProvider


class ElevenLabsTTS(TTSProvider):
    suffix = ".mp3"

    def __init__(self, voice_id: str = "Rachel", model: str = "eleven_turbo_v2_5") -> None:
        self.voice_id = voice_id
        self.model = model

    def synthesize_to_file(self, text: str, out_path: str) -> str:
        key = Settings.secret("ELEVENLABS_API_KEY")
        if not key:
            raise RuntimeError("ElevenLabs needs ELEVENLABS_API_KEY.")
        from elevenlabs.client import ElevenLabs

        client = ElevenLabs(api_key=key)
        audio = client.text_to_speech.convert(
            voice_id=self.voice_id, model_id=self.model, text=text
        )
        with open(out_path, "wb") as fh:
            for chunk in audio:
                fh.write(chunk)
        return out_path
