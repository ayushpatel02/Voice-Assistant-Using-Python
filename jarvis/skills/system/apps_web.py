"""Launch applications and open websites via the platform layer."""

from __future__ import annotations

from ..base import Context, Skill, Tool


class AppsWebSkill(Skill):
    name = "apps_web"

    def tools(self) -> list[Tool]:
        return [
            Tool(
                name="open_app",
                description="Open a desktop application by name (e.g. 'spotify', 'code').",
                parameters={
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                    "required": ["name"],
                },
                handler=self._open_app,
            ),
            Tool(
                name="open_website",
                description="Open a website/URL in the default browser.",
                parameters={
                    "type": "object",
                    "properties": {"url": {"type": "string"}},
                    "required": ["url"],
                },
                handler=self._open_url,
            ),
        ]

    def _open_app(self, args: dict, ctx: Context) -> str:
        name = args.get("name", "").strip()
        if not name:
            return "Which application?"
        return ctx.platform.open_app(name)

    def _open_url(self, args: dict, ctx: Context) -> str:
        url = args.get("url", "").strip()
        if not url:
            return "Which website?"
        return ctx.platform.open_url(url)
