"""Voice interface entry point: hands-free 'Jarvis' wake-word assistant."""

from __future__ import annotations

from ..config.settings import load_settings
from ..core.assistant import Assistant
from ..voice.audio_io import AudioIO
from ..voice.pipeline import VoicePipeline
from ..voice.stt.factory import build_stt
from ..voice.tts.factory import build_tts
from ..voice.wakeword.factory import build_wakeword


def run_voice(allow_power: bool = False) -> None:
    settings = load_settings()
    try:
        assistant = Assistant.create(settings=settings, allow_power=allow_power)
        stt = build_stt(settings)
        tts = build_tts(settings)
        wakeword = build_wakeword(settings)
        audio = AudioIO()
        session = assistant.new_session("voice")
        pipeline = VoicePipeline(assistant, session, stt, tts, audio, wakeword)
    except Exception as exc:
        print(f"Could not start voice mode: {exc}")
        print("Install the voice extras with: pip install 'jarvis-assistant[voice]'")
        return

    try:
        pipeline.speak(f"{settings.assistant.name} online.")
    except Exception:
        pass  # greeting is best-effort; don't block the loop on audio output

    try:
        pipeline.run()
    except KeyboardInterrupt:
        print("\nStopping.")
    except RuntimeError as exc:
        print(f"\nVoice mode stopped: {exc}")
        print("Install the voice extras with: pip install 'jarvis-assistant[voice]'")
    finally:
        assistant.shutdown()
