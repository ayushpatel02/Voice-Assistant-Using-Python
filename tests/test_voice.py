from pathlib import Path

from jarvis.config.settings import Settings
from jarvis.core.assistant import Assistant
from jarvis.voice.pipeline import VoicePipeline
from jarvis.voice.stt.base import FakeSTT
from jarvis.voice.stt.factory import build_stt
from jarvis.voice.tts.base import FakeTTS
from jarvis.voice.tts.factory import build_tts
from jarvis.voice.wakeword.base import FakeWakeWord
from jarvis.voice.wakeword.factory import build_wakeword


def _assistant(tmp_path) -> Assistant:
    settings = Settings()
    settings.data_dir = tmp_path
    settings.llm.provider = "fake"
    return Assistant.create(settings=settings)


def test_pipeline_transcribes_responds_and_renders_audio(tmp_path):
    assistant = _assistant(tmp_path)
    pipeline = VoicePipeline(
        assistant,
        assistant.new_session("voice"),
        stt=FakeSTT("what time is it"),
        tts=FakeTTS(),
        audio=None,  # respond_to_audio never touches the mic
        wakeword=FakeWakeWord(),
    )
    turn = pipeline.respond_to_audio("dummy.wav")
    assert turn.heard == "what time is it"
    assert turn.response is not None
    assert turn.audio_path and Path(turn.audio_path).exists()


def test_pipeline_ignores_empty_transcription(tmp_path):
    assistant = _assistant(tmp_path)
    pipeline = VoicePipeline(
        assistant,
        assistant.new_session("voice"),
        stt=FakeSTT(""),
        tts=FakeTTS(),
        audio=None,
        wakeword=FakeWakeWord(),
    )
    turn = pipeline.respond_to_audio("dummy.wav")
    assert turn.heard == ""
    assert turn.response is None
    assert turn.audio_path is None


def test_wakeword_waits_then_fires():
    class FakeAudio:
        def stream_frames(self, n):
            while True:
                yield [0] * n

    detector = FakeWakeWord(fire_after=3)
    detector.wait_for_wake(FakeAudio())
    assert detector.seen == 3


def test_voice_factories_select_fakes():
    settings = Settings()
    settings.voice.stt = "fake"
    settings.voice.tts = "fake"
    settings.voice.wakeword = "fake"
    assert isinstance(build_stt(settings), FakeSTT)
    assert isinstance(build_tts(settings), FakeTTS)
    assert isinstance(build_wakeword(settings), FakeWakeWord)
