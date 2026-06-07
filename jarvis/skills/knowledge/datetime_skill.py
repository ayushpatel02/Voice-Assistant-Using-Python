"""Date and time."""

from __future__ import annotations

from datetime import datetime

from ..base import Context, Skill, Tool, no_params


class DateTimeSkill(Skill):
    name = "datetime"

    def tools(self) -> list[Tool]:
        return [
            Tool(
                name="get_time",
                description="Get the current local time.",
                parameters=no_params(),
                handler=self._time,
            ),
            Tool(
                name="get_date",
                description="Get today's date.",
                parameters=no_params(),
                handler=self._date,
            ),
        ]

    def _time(self, args: dict, ctx: Context) -> str:
        return datetime.now().strftime("It's %I:%M %p.")

    def _date(self, args: dict, ctx: Context) -> str:
        return datetime.now().strftime("Today is %A, %d %B %Y.")
