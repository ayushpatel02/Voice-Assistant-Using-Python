"""Auto-discovers skills and exposes their tools to the brain.

On startup the registry imports every module under ``jarvis.skills``, finds all
``Skill`` subclasses, instantiates the ones enabled by config (and whose
required secrets are present), and builds:
  - a list of provider-neutral ``ToolSpec`` for the LLM, and
  - a ``name -> Tool`` dispatch table the router uses to execute calls.
"""

from __future__ import annotations

import importlib
import logging
import pkgutil

from ..config.settings import Settings
from ..llm.base import ToolSpec
from .base import Context, Skill, Tool

log = logging.getLogger(__name__)


class Registry:
    def __init__(self, tools: dict[str, Tool], skills: list[str]) -> None:
        self._tools = tools
        self.skills = skills

    def tool_specs(self) -> list[ToolSpec]:
        return [
            ToolSpec(name=t.name, description=t.description, parameters=t.parameters)
            for t in self._tools.values()
        ]

    def has(self, name: str) -> bool:
        return name in self._tools

    def dispatch(self, name: str, args: dict, context: Context) -> str:
        tool = self._tools.get(name)
        if tool is None:
            return f"Error: unknown tool {name!r}."
        try:
            return tool.handler(args, context)
        except Exception as exc:  # surface failures to the model, don't crash
            log.exception("Tool %s failed", name)
            return f"Error while running {name}: {exc}"

    def __len__(self) -> int:
        return len(self._tools)


def _iter_skill_modules() -> list[str]:
    package = importlib.import_module("jarvis.skills")
    names: list[str] = []
    for info in pkgutil.walk_packages(package.__path__, prefix="jarvis.skills."):
        # Skip the framework modules themselves.
        if info.name.rsplit(".", 1)[-1] in {"base", "registry"}:
            continue
        names.append(info.name)
    return names


def _discover_skill_classes() -> list[type[Skill]]:
    classes: list[type[Skill]] = []
    for module_name in _iter_skill_modules():
        try:
            module = importlib.import_module(module_name)
        except Exception:  # a skill's optional dep may be missing; skip it
            log.warning("Could not import skill module %s", module_name, exc_info=True)
            continue
        for attr in vars(module).values():
            if (
                isinstance(attr, type)
                and issubclass(attr, Skill)
                and attr is not Skill
                and attr.__module__ == module_name
            ):
                classes.append(attr)
    return classes


def build_registry(settings: Settings) -> Registry:
    tools: dict[str, Tool] = {}
    enabled_skills: list[str] = []

    for skill_cls in _discover_skill_classes():
        name = skill_cls.name or skill_cls.__name__
        if not settings.skills.is_enabled(name):
            continue

        missing = [s for s in skill_cls.required_secrets if not Settings.secret(s)]
        if missing:
            log.info("Skill %s disabled (missing secrets: %s)", name, ", ".join(missing))
            continue

        skill = skill_cls()
        for tool in skill.tools():
            if tool.name in tools:
                log.warning("Duplicate tool name %s; keeping first", tool.name)
                continue
            tools[tool.name] = tool
        enabled_skills.append(name)

    log.info("Loaded %d skills, %d tools", len(enabled_skills), len(tools))
    return Registry(tools, enabled_skills)
