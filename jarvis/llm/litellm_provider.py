"""LiteLLM-backed provider.

LiteLLM exposes a single OpenAI-format API across Claude, OpenAI, Ollama, and
local models, and translates one tool schema into each provider's native
function-calling format. ``litellm`` is imported lazily so the package (and the
test suite) work without it installed.
"""

from __future__ import annotations

import json
from typing import Any

from .base import LLMProvider, LLMResult, Message, ToolCall, ToolSpec


class LiteLLMProvider(LLMProvider):
    def __init__(self, model: str, temperature: float = 0.7) -> None:
        self.model = model
        self.temperature = temperature

    def complete(
        self, messages: list[Message], tools: list[ToolSpec] | None = None
    ) -> LLMResult:
        try:
            import litellm
        except ImportError as exc:  # pragma: no cover - depends on extras
            raise RuntimeError(
                "The 'litellm' package is required for the litellm provider. "
                "Install it with: pip install 'jarvis-assistant[llm]'"
            ) from exc

        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": [_to_wire(m) for m in messages],
            "temperature": self.temperature,
        }
        if tools:
            kwargs["tools"] = [_tool_to_wire(t) for t in tools]
            kwargs["tool_choice"] = "auto"

        response = litellm.completion(**kwargs)
        return _from_wire(response)


def _to_wire(message: Message) -> dict[str, Any]:
    wire: dict[str, Any] = {"role": message.role}
    if message.content is not None:
        wire["content"] = message.content
    if message.role == "tool":
        wire["tool_call_id"] = message.tool_call_id
        wire["name"] = message.name
    if message.tool_calls:
        wire["content"] = message.content or ""
        wire["tool_calls"] = [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.name,
                    "arguments": json.dumps(tc.arguments),
                },
            }
            for tc in message.tool_calls
        ]
    return wire


def _tool_to_wire(tool: ToolSpec) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters,
        },
    }


def _from_wire(response: Any) -> LLMResult:
    choice = response.choices[0]
    msg = choice.message
    tool_calls: list[ToolCall] = []
    for tc in getattr(msg, "tool_calls", None) or []:
        raw_args = tc.function.arguments or "{}"
        try:
            args = json.loads(raw_args)
        except (json.JSONDecodeError, TypeError):
            args = {}
        tool_calls.append(ToolCall(id=tc.id, name=tc.function.name, arguments=args))
    return LLMResult(text=msg.content, tool_calls=tool_calls)
