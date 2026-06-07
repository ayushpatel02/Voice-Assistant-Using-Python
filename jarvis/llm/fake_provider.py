"""Offline providers used for tests and key-less smoke runs.

``EchoLLMProvider`` needs no API key or network: it simply restates the last
user message. ``ScriptedLLMProvider`` returns a predefined sequence of results,
which makes the router and skills testable without any real model.
"""

from __future__ import annotations

from .base import LLMProvider, LLMResult, Message, ToolSpec


class EchoLLMProvider(LLMProvider):
    """A trivial brain for running the CLI without configuring a real model."""

    def complete(
        self, messages: list[Message], tools: list[ToolSpec] | None = None
    ) -> LLMResult:
        last_user = next(
            (m.content for m in reversed(messages) if m.role == "user" and m.content),
            "",
        )
        return LLMResult(
            text=(
                "(offline echo brain — set an API key and an LLM provider in "
                f"config to enable the real assistant) You said: {last_user}"
            )
        )


class ScriptedLLMProvider(LLMProvider):
    """Returns queued results in order; used by the test suite."""

    def __init__(self, results: list[LLMResult]) -> None:
        self._results = list(results)
        self.calls: list[list[Message]] = []

    def complete(
        self, messages: list[Message], tools: list[ToolSpec] | None = None
    ) -> LLMResult:
        self.calls.append(list(messages))
        if not self._results:
            return LLMResult(text="(no more scripted results)")
        return self._results.pop(0)
