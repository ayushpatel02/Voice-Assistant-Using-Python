"""Lightweight web search via the DuckDuckGo Instant Answer API (no key)."""

from __future__ import annotations

from ...services.http import get_json
from ..base import Context, Skill, Tool


class WebSearchSkill(Skill):
    name = "web_search"

    def tools(self) -> list[Tool]:
        return [
            Tool(
                name="web_search",
                description=(
                    "Search the web for a quick factual answer or summary. "
                    "Best for definitions, people, places, and 'what is' questions."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The search query."}
                    },
                    "required": ["query"],
                },
                handler=self._search,
            )
        ]

    def _search(self, args: dict, ctx: Context) -> str:
        query = args.get("query", "").strip()
        if not query:
            return "No query provided."
        try:
            data = get_json(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_html": 1},
            )
        except Exception as exc:
            return f"Search failed: {exc}"

        if data.get("AbstractText"):
            return data["AbstractText"]
        if data.get("Answer"):
            return str(data["Answer"])
        topics = data.get("RelatedTopics") or []
        for t in topics:
            if isinstance(t, dict) and t.get("Text"):
                return t["Text"]
        return f"No quick answer found for {query!r}."
