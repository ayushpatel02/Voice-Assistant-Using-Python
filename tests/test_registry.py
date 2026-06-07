from jarvis.config.settings import Settings
from jarvis.skills.registry import build_registry


def test_registry_discovers_core_tools():
    registry = build_registry(Settings())
    names = {spec.name for spec in registry.tool_specs()}
    # No-secret skills should always be present.
    assert {"get_time", "get_date", "add_note", "open_app", "set_volume"} <= names


def test_disabled_skill_is_excluded():
    settings = Settings()
    settings.skills.disabled = ["datetime"]
    registry = build_registry(settings)
    names = {spec.name for spec in registry.tool_specs()}
    assert "get_time" not in names
    assert "add_note" in names


def test_enabled_allowlist_limits_skills():
    settings = Settings()
    settings.skills.enabled = ["notes"]
    registry = build_registry(settings)
    names = {spec.name for spec in registry.tool_specs()}
    assert "add_note" in names
    assert "get_time" not in names


def test_secret_gated_skill_absent_without_key(monkeypatch):
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
    registry = build_registry(Settings())
    assert "get_weather" not in {s.name for s in registry.tool_specs()}
