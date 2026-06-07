"""The skill-plugin contract.

A *skill* groups one or more *tools*. Each tool couples three things:
  - a JSON-Schema parameter definition (OpenAI tool format),
  - a precise natural-language description (this IS the prompt the model sees),
  - a Python handler that performs the action.

Adding a capability is a one-file drop-in: subclass ``Skill`` anywhere under
``jarvis.skills`` and the registry discovers it automatically.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:  # avoid import cycles at runtime
    from ..config.settings import Settings
    from ..core.session import Session
    from ..platform.base import PlatformController
    from ..services import Services


@dataclass
class Context:
    """Everything a tool handler may need, injected at call time."""

    settings: "Settings"
    session: "Session"
    services: "Services"
    platform: "PlatformController"


# A handler takes the parsed argument dict plus the context and returns a
# string result that is fed back to the model as the tool's output.
Handler = Callable[[dict[str, Any], Context], str]


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict[str, Any]
    handler: Handler


def no_params() -> dict[str, Any]:
    """Convenience: a JSON schema for a tool that takes no arguments."""
    return {"type": "object", "properties": {}, "additionalProperties": False}


class Skill(ABC):
    """Base class for all skills. Subclass and implement :meth:`tools`."""

    #: Unique, stable identifier used for enable/disable config.
    name: str = ""

    #: Optional list of secret env-var names this skill needs to function.
    #: The registry uses these to skip skills that can't work yet.
    required_secrets: tuple[str, ...] = ()

    @abstractmethod
    def tools(self) -> list[Tool]:
        """Return the tools this skill exposes to the model."""
        raise NotImplementedError
