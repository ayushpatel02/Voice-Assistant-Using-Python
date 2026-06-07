"""Countdown timers."""

from __future__ import annotations

from datetime import datetime, timedelta

from ..base import Context, Skill, Tool


class TimersSkill(Skill):
    name = "timers"

    def tools(self) -> list[Tool]:
        return [
            Tool(
                name="set_timer",
                description="Start a countdown timer for a number of seconds.",
                parameters={
                    "type": "object",
                    "properties": {
                        "seconds": {"type": "integer", "description": "Duration in seconds."},
                        "label": {"type": "string", "description": "Optional label."},
                    },
                    "required": ["seconds"],
                },
                handler=self._set,
            )
        ]

    def _set(self, args: dict, ctx: Context) -> str:
        seconds = int(args.get("seconds", 0) or 0)
        if seconds <= 0:
            return "Please give a positive number of seconds."
        label = (args.get("label") or "Timer").strip()
        when = datetime.now() + timedelta(seconds=seconds)
        armed = ctx.services.scheduler.schedule_at(when, f"{label} finished!")
        mins, secs = divmod(seconds, 60)
        human = f"{mins}m {secs}s" if mins else f"{secs}s"
        if armed:
            return f"{label} set for {human}."
        return f"{label} noted for {human}, but background timers aren't available here."
