"""Top headlines via NewsAPI (requires NEWS_API_KEY)."""

from __future__ import annotations

from ...config.settings import Settings
from ...services.http import get_json
from ..base import Context, Skill, Tool


class NewsSkill(Skill):
    name = "news"
    required_secrets = ("NEWS_API_KEY",)

    def tools(self) -> list[Tool]:
        return [
            Tool(
                name="get_news",
                description="Get current top news headlines, optionally about a topic.",
                parameters={
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "Optional topic/keyword to filter headlines.",
                        },
                        "count": {"type": "integer", "default": 5},
                    },
                },
                handler=self._news,
            )
        ]

    def _news(self, args: dict, ctx: Context) -> str:
        key = Settings.secret("NEWS_API_KEY")
        if not key:
            return "News is not configured (missing NEWS_API_KEY)."
        topic = (args.get("topic") or "").strip()
        count = int(args.get("count", 5) or 5)
        params = {"apiKey": key, "pageSize": count, "language": "en"}
        if topic:
            url = "https://newsapi.org/v2/everything"
            params["q"] = topic
            params["sortBy"] = "publishedAt"
        else:
            url = "https://newsapi.org/v2/top-headlines"
            params["country"] = "us"
        try:
            data = get_json(url, params=params)
        except Exception as exc:
            return f"Could not fetch news: {exc}"
        articles = data.get("articles", [])[:count]
        if not articles:
            return "No headlines found."
        return "\n".join(f"- {a['title']}" for a in articles)
