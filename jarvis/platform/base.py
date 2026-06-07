"""OS abstraction for system-control actions.

The base class implements the genuinely cross-platform bits (open a URL,
adjust brightness via ``screen-brightness-control``) and a guard around
destructive power actions. Subclasses supply the OS-specific commands for
launching apps, setting volume, and power control.
"""

from __future__ import annotations

import logging
import subprocess
import webbrowser
from abc import ABC, abstractmethod

log = logging.getLogger(__name__)


class PlatformController(ABC):
    def __init__(self, allow_power: bool = False) -> None:
        # Power actions are destructive; off unless explicitly enabled in config.
        self.allow_power = allow_power

    # --- cross-platform ---
    def open_url(self, url: str) -> str:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        webbrowser.open(url)
        return f"Opening {url}"

    def set_brightness(self, percent: int) -> str:
        percent = max(0, min(100, percent))
        try:
            import screen_brightness_control as sbc

            sbc.set_brightness(percent)
            return f"Brightness set to {percent}%."
        except Exception as exc:
            return f"Could not set brightness: {exc}"

    # --- power (guarded) ---
    def shutdown(self) -> str:
        return self._guarded_power("shutdown")

    def restart(self) -> str:
        return self._guarded_power("restart")

    def logout(self) -> str:
        return self._guarded_power("logout")

    def _guarded_power(self, action: str) -> str:
        if not self.allow_power:
            return (
                f"Power action '{action}' is disabled for safety. "
                "Enable it in config to allow this."
            )
        cmd = self._power_command(action)
        if not cmd:
            return f"Power action '{action}' is not supported on this platform."
        try:
            subprocess.Popen(cmd)
            return f"{action.capitalize()} initiated."
        except Exception as exc:
            return f"Could not {action}: {exc}"

    @staticmethod
    def _run(cmd: list[str]) -> str:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return (result.stdout or result.stderr).strip()

    # --- OS-specific ---
    @abstractmethod
    def open_app(self, name: str) -> str: ...

    @abstractmethod
    def set_volume(self, percent: int) -> str: ...

    @abstractmethod
    def _power_command(self, action: str) -> list[str] | None: ...
