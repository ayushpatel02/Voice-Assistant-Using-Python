"""Reminders: stored in the local DB and armed with the scheduler when possible."""

from __future__ import annotations

from datetime import datetime

from ..base import Context, Skill, Tool, no_params


class RemindersSkill(Skill):
    name = "reminders"

    def tools(self) -> list[Tool]:
        return [
            Tool(
                name="add_reminder",
                description=(
                    "Create a reminder for a specific date/time. Provide the time "
                    "as an ISO 8601 string (e.g. '2026-06-03T18:30:00')."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "What to be reminded of."},
                        "due_iso": {
                            "type": "string",
                            "description": "When, as ISO 8601 local time.",
                        },
                    },
                    "required": ["text", "due_iso"],
                },
                handler=self._add,
            ),
            Tool(
                name="list_reminders",
                description="List pending reminders.",
                parameters=no_params(),
                handler=self._list,
            ),
        ]

    def _add(self, args: dict, ctx: Context) -> str:
        text = args.get("text", "").strip()
        due_iso = args.get("due_iso", "").strip()
        if not text or not due_iso:
            return "I need both what to remind you of and when."
        try:
            when = datetime.fromisoformat(due_iso)
        except ValueError:
            return f"I couldn't understand the time {due_iso!r}. Use ISO 8601."
        ctx.services.store.add_reminder(text, due_iso)
        armed = ctx.services.scheduler.schedule_at(when, f"Reminder: {text}")
        note = "" if armed else " (it will be in your list, but won't pop up automatically here)"
        return f"Reminder set for {when:%A %d %B at %I:%M %p}: {text}.{note}"

    def _list(self, args: dict, ctx: Context) -> str:
        reminders = ctx.services.store.list_reminders()
        if not reminders:
            return "You have no pending reminders."
        lines = []
        for r in reminders:
            try:
                when = datetime.fromisoformat(r.due_iso)
                stamp = when.strftime("%a %d %b %I:%M %p")
            except ValueError:
                stamp = r.due_iso
            lines.append(f"- {stamp}: {r.text}")
        return "\n".join(lines)
