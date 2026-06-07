"""Skill plugins. Drop a new ``Skill`` subclass module here and it's discovered."""

from .base import Context, Skill, Tool
from .registry import Registry, build_registry

__all__ = ["Context", "Skill", "Tool", "Registry", "build_registry"]
