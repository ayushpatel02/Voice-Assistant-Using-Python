"""edge-tts (default): free, natural Microsoft neural voices. Online, outputs MP3."""

from __future__ import annotations

import asyncio

from .base import TTSProvider


class EdgeTTS(TTSProvider):
    suffix = ".mp3"

    def __init__(self, voice: str = "en-GB-RyanNeural") -> None:
        self.voice = voice

    def synthesize_to_file(self, text: str, out_path: str) -> str:
        import edge_tts

        async def _run() -> None:
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(out_path)

        asyncio.run(_run())
        return out_path
