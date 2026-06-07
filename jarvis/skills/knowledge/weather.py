"""Current weather via OpenWeather (requires OPENWEATHER_API_KEY)."""

from __future__ import annotations

from ...config.settings import Settings
from ...services.http import get_json
from ..base import Context, Skill, Tool


class WeatherSkill(Skill):
    name = "weather"
    required_secrets = ("OPENWEATHER_API_KEY",)

    def tools(self) -> list[Tool]:
        return [
            Tool(
                name="get_weather",
                description="Get the current weather for a city.",
                parameters={
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City name, e.g. 'Mumbai' or 'London,GB'.",
                        },
                        "units": {
                            "type": "string",
                            "enum": ["metric", "imperial"],
                            "default": "metric",
                        },
                    },
                    "required": ["location"],
                },
                handler=self._weather,
            )
        ]

    def _weather(self, args: dict, ctx: Context) -> str:
        key = Settings.secret("OPENWEATHER_API_KEY")
        if not key:
            return "Weather is not configured (missing OPENWEATHER_API_KEY)."
        location = args.get("location", "").strip()
        units = args.get("units", "metric")
        try:
            data = get_json(
                "https://api.openweathermap.org/data/2.5/weather",
                params={"q": location, "units": units, "appid": key},
            )
        except Exception as exc:
            return f"Could not fetch weather: {exc}"
        if str(data.get("cod")) != "200":
            return f"Weather lookup failed: {data.get('message', 'unknown error')}."
        desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        unit = "°C" if units == "metric" else "°F"
        return f"{location.title()}: {desc}, {temp}{unit}."
