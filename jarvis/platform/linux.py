"""Linux platform controller."""

from __future__ import annotations

import shutil
import subprocess

from .base import PlatformController


class LinuxController(PlatformController):
    def open_app(self, name: str) -> str:
        launcher = shutil.which(name) or shutil.which("gtk-launch")
        if not launcher:
            return f"Could not find a launcher for {name!r}."
        try:
            if launcher.endswith("gtk-launch"):
                subprocess.Popen([launcher, name])
            else:
                subprocess.Popen([launcher])
            return f"Opening {name}."
        except Exception as exc:
            return f"Could not open {name}: {exc}"

    def set_volume(self, percent: int) -> str:
        percent = max(0, min(100, percent))
        if shutil.which("pactl"):
            try:
                self._run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{percent}%"])
                return f"Volume set to {percent}%."
            except Exception as exc:
                return f"Could not set volume: {exc}"
        if shutil.which("amixer"):
            try:
                self._run(["amixer", "set", "Master", f"{percent}%"])
                return f"Volume set to {percent}%."
            except Exception as exc:
                return f"Could not set volume: {exc}"
        return "No supported volume control (pactl/amixer) found."

    def _power_command(self, action: str) -> list[str] | None:
        return {
            "shutdown": ["systemctl", "poweroff"],
            "restart": ["systemctl", "reboot"],
            "logout": ["loginctl", "terminate-user", ""],
        }.get(action)
