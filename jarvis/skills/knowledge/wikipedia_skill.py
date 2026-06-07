"""Wikipedia summaries."""

from __future__ import annotations

from ..base import Context, Skill, Tool


class WikipediaSkill(Skill):
    name = "wikipedia"

    def tools(self) -> list[Tool]:
        return [
            Tool(
                name="wikipedia_summary",
                description="Look up a topic on Wikipedia and return a short summary.",
                parameters={
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "The subject to look up."},
                        "sentences": {
                            "type": "integer",
                            "description": "How many sentences to return (1-5).",
                            "default": 3,
                        },
                    },
                    "required": ["topic"],
                },
                handler=self._summary,
            )
        ]

    def _summary(self, args: dict, ctx: Context) -> str:
        topic = args.get("topic", "").strip()
        if not topic:
            return "No topic provided."
        sentences = int(args.get("sentences", 3) or 3)
        try:
            import wikipedia
        except ImportError:
            return "The 'wikipedia' package is not installed."
        try:
            return wikipedia.summary(topic, sentences=max(1, min(5, sentences)))
        except Exception as exc:
            return f"Could not find a Wikipedia summary for {topic!r}: {exc}"
