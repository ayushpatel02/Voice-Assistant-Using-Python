from jarvis.config.settings import Settings, load_settings


def test_defaults_load():
    settings = load_settings()
    assert settings.assistant.name == "Jarvis"
    assert settings.llm.provider in {"litellm", "fake"}
    assert settings.voice.wake_word == "jarvis"


def test_env_override(monkeypatch):
    monkeypatch.setenv("JARVIS_LLM_MODEL", "gpt-4o")
    monkeypatch.setenv("JARVIS_LLM_PROVIDER", "fake")
    settings = load_settings()
    assert settings.llm.model == "gpt-4o"
    assert settings.llm.provider == "fake"


def test_secret_reads_from_env(monkeypatch):
    monkeypatch.setenv("SOME_SECRET", "abc123")
    assert Settings.secret("SOME_SECRET") == "abc123"
    monkeypatch.delenv("SOME_SECRET", raising=False)
    assert Settings.secret("SOME_SECRET") is None
