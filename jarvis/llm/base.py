"""Provider-agnostic LLM interface.

The rest of the system speaks only in these neutral types. Concrete providers
(LiteLLM, native SDKs, the offline fake) translate to and from their own wire
formats, so swapping the brain never touches core or skill code.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCall:
    """A request from the model to invoke a tool with arguments."""

    id: str
    name: str
    arguments: dict[str, Any] = field(default_factory=dict)


@dataclass
class Message:
    """A single conversation message in neutral form."""

    role: str  # "system" | "user" | "assistant" | "tool"
    content: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_call_id: str | None = None  # set on role == "tool"
    name: str | None = None  # tool name, on role == "tool"


@dataclass
class ToolSpec:
    """The provider-neutral schema for a tool the model may call."""

    name: str
    description: str
    parameters: dict[str, Any]  # JSON Schema for the arguments object


@dataclass
class LLMResult:
    """The model's reply: either final text, tool calls, or both."""

    text: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)

    @property
    def wants_tools(self) -> bool:
        return bool(self.tool_calls)


class LLMProvider(ABC):
    """Abstract brain. Implementations turn messages + tools into a reply."""

    @abstractmethod
    def complete(
        self, messages: list[Message], tools: list[ToolSpec] | None = None
    ) -> LLMResult:
        """Run one completion step and return the model's result."""
        raise NotImplementedError
