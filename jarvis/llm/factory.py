"""Select and construct the configured LLM provider."""

from __future__ import annotations

from ..config.settings import Settings
from .base import LLMProvider


def build_llm(settings: Settings) -> LLMProvider:
    provider = settings.llm.provider.lower()

    if provider in {"fake", "echo", "offline"}:
        from .fake_provider import EchoLLMProvider

        return EchoLLMProvider()

    if provider == "litellm":
        from .litellm_provider import LiteLLMProvider

        return LiteLLMProvider(
            model=settings.llm.model,
            temperature=settings.llm.temperature,
        )

    raise ValueError(f"Unknown LLM provider: {settings.llm.provider!r}")
