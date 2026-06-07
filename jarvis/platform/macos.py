"""macOS platform controller."""

from __future__ import annotations

import subprocess

from .base import PlatformController


class MacOSController(PlatformController):
    def open_app(self, name: str) -> str:
        try:
            subprocess.Popen(["open", "-a", name])
            return f"Opening {name}."
        except Exception as exc:
            return f"Could not open {name}: {exc}"

    def set_volume(self, percent: int) -> str:
        percent = max(0, min(100, percent))
        try:
            subprocess.run(
                ["osascript", "-e", f"set volume output volume {percent}"],
                check=True,
            )
            return f"Volume set to {percent}%."
        except Exception as exc:
            return f"Could not set volume: {exc}"

    def _power_command(self, action: str) -> list[str] | None:
        verbs = {
            "shutdown": "shut down",
            "restart": "restart",
            "logout": "log out",
        }
        verb = verbs.get(action)
        if not verb:
            return None
        return ["osascript", "-e", f'tell app "System Events" to {verb}']
