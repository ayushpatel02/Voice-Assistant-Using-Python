"""Typed configuration for Jarvis.

Configuration is layered: built-in ``defaults.toml`` -> optional user config
file (``JARVIS_CONFIG``) -> ``JARVIS_*`` environment variables. Secrets/keys
are NOT part of this schema; they are read from the environment (loaded from
``.env`` via python-dotenv) at the point of use, so they never get logged or
serialized with the settings object.
"""

from __future__ import annotations

import os
import tomllib
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

_DEFAULTS_PATH = Path(__file__).with_name("defaults.toml")


class LLMSettings(BaseModel):
    provider: str = "litellm"
    model: str = "claude-sonnet-4-5"
    temperature: float = 0.7
    max_tool_iterations: int = 6


class SkillsSettings(BaseModel):
    enabled: list[str] = Field(default_factory=list)
    disabled: list[str] = Field(default_factory=list)

    def is_enabled(self, name: str) -> bool:
        if name in self.disabled:
            return False
        if self.enabled:
            return name in self.enabled
        return True


class VoiceSettings(BaseModel):
    wake_word: str = "jarvis"
    stt: str = "faster_whisper"
    tts: str = "edge_tts"
    voice_name: str = "en-GB-RyanNeural"


class WebSettings(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8765


class AssistantSettings(BaseModel):
    name: str = "Jarvis"
    persona: str = "You are Jarvis, a concise and capable assistant."


class Settings(BaseModel):
    llm: LLMSettings = Field(default_factory=LLMSettings)
    skills: SkillsSettings = Field(default_factory=SkillsSettings)
    voice: VoiceSettings = Field(default_factory=VoiceSettings)
    web: WebSettings = Field(default_factory=WebSettings)
    assistant: AssistantSettings = Field(default_factory=AssistantSettings)
    data_dir: Path = Field(default_factory=lambda: _default_data_dir())

    @staticmethod
    def secret(name: str) -> str | None:
        """Read a secret/key from the environment. Never stored on the model."""
        value = os.environ.get(name)
        return value or None


def _default_data_dir() -> Path:
    base = os.environ.get("JARVIS_DATA_DIR")
    if base:
        return Path(base)
    return Path.home() / ".local" / "share" / "jarvis"


def _deep_merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def _load_toml(path: Path) -> dict:
    with path.open("rb") as fh:
        return tomllib.load(fh)


def _env_overrides() -> dict:
    """Translate JARVIS_<SECTION>_<KEY> env vars into a nested override dict.

    Example: JARVIS_LLM_MODEL=gpt-4o -> {"llm": {"model": "gpt-4o"}}.
    Only known top-level sections are considered so unrelated JARVIS_* vars
    (like JARVIS_EMAIL, a secret) are ignored here.
    """
    sections = {"llm", "skills", "voice", "web", "assistant"}
    overrides: dict[str, dict] = {}
    for env_key, value in os.environ.items():
        if not env_key.startswith("JARVIS_"):
            continue
        remainder = env_key[len("JARVIS_") :].lower()
        section, _, field = remainder.partition("_")
        if not field or section not in sections:
            continue
        overrides.setdefault(section, {})[field] = value
    return overrides


def load_settings(config_path: str | os.PathLike[str] | None = None) -> Settings:
    """Build the Settings object from defaults, an optional user file, and env."""
    load_dotenv()  # populate os.environ from a local .env if present

    data = _load_toml(_DEFAULTS_PATH)

    user_path = config_path or os.environ.get("JARVIS_CONFIG")
    if user_path:
        p = Path(user_path)
        if p.exists():
            data = _deep_merge(data, _load_toml(p))

    data = _deep_merge(data, _env_overrides())
    return Settings.model_validate(data)
