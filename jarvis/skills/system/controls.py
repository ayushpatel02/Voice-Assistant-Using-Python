"""Volume, brightness, and (guarded) power controls via the platform layer."""

from __future__ import annotations

from ..base import Context, Skill, Tool, no_params


def _percent_param(desc: str) -> dict:
    return {
        "type": "object",
        "properties": {
            "percent": {
                "type": "integer",
                "minimum": 0,
                "maximum": 100,
                "description": desc,
            }
        },
        "required": ["percent"],
    }


class ControlsSkill(Skill):
    name = "controls"

    def tools(self) -> list[Tool]:
        return [
            Tool(
                name="set_volume",
                description="Set the system output volume (0-100%).",
                parameters=_percent_param("Target volume percentage."),
                handler=lambda a, c: c.platform.set_volume(int(a.get("percent", 50))),
            ),
            Tool(
                name="set_brightness",
                description="Set the screen brightness (0-100%).",
                parameters=_percent_param("Target brightness percentage."),
                handler=lambda a, c: c.platform.set_brightness(int(a.get("percent", 50))),
            ),
            Tool(
                name="shutdown_computer",
                description="Shut down the computer. Confirm with the user first.",
                parameters=no_params(),
                handler=lambda a, c: c.platform.shutdown(),
            ),
            Tool(
                name="restart_computer",
                description="Restart the computer. Confirm with the user first.",
                parameters=no_params(),
                handler=lambda a, c: c.platform.restart(),
            ),
            Tool(
                name="logout",
                description="Log out the current user. Confirm with the user first.",
                parameters=no_params(),
                handler=lambda a, c: c.platform.logout(),
            ),
        ]
