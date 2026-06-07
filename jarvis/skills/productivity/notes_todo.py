"""Notes and to-do list, persisted in the local store."""

from __future__ import annotations

from ..base import Context, Skill, Tool, no_params


class NotesSkill(Skill):
    name = "notes"

    def tools(self) -> list[Tool]:
        return [
            Tool(
                name="add_note",
                description="Save a note or to-do item for later.",
                parameters={
                    "type": "object",
                    "properties": {"text": {"type": "string"}},
                    "required": ["text"],
                },
                handler=self._add,
            ),
            Tool(
                name="list_notes",
                description="List all saved notes and to-do items.",
                parameters=no_params(),
                handler=self._list,
            ),
            Tool(
                name="clear_notes",
                description="Delete all saved notes.",
                parameters=no_params(),
                handler=self._clear,
            ),
        ]

    def _add(self, args: dict, ctx: Context) -> str:
        text = args.get("text", "").strip()
        if not text:
            return "Nothing to save."
        ctx.services.store.add_note(text)
        return f"Saved: {text}"

    def _list(self, args: dict, ctx: Context) -> str:
        notes = ctx.services.store.list_notes()
        if not notes:
            return "You have no notes."
        return "\n".join(f"{i}. {n}" for i, n in enumerate(notes, 1))

    def _clear(self, args: dict, ctx: Context) -> str:
        count = ctx.services.store.clear_notes()
        return f"Cleared {count} note(s)."
