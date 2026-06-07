"""Play music by opening a Spotify search (no account/API key required)."""

from __future__ import annotations

import urllib.parse

from ..base import Context, Skill, Tool


class MusicSkill(Skill):
    name = "music"

    def tools(self) -> list[Tool]:
        return [
            Tool(
                name="play_music",
                description="Search and open a song, artist, or playlist on Spotify.",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "What to play, e.g. 'Bohemian Rhapsody'.",
                        }
                    },
                    "required": ["query"],
                },
                handler=self._play,
            )
        ]

    def _play(self, args: dict, ctx: Context) -> str:
        query = args.get("query", "").strip()
        if not query:
            return "What would you like to play?"
        encoded = urllib.parse.quote(query)
        ctx.platform.open_url(f"https://open.spotify.com/search/{encoded}")
        return f"Opening Spotify for {query!r}."
