"""Windows platform controller."""

from __future__ import annotations

import os

from .base import PlatformController


class WindowsController(PlatformController):
    def open_app(self, name: str) -> str:
        try:
            os.startfile(name)  # type: ignore[attr-defined]  # Windows-only
            return f"Opening {name}."
        except Exception as exc:
            return f"Could not open {name}: {exc}"

    def set_volume(self, percent: int) -> str:
        percent = max(0, min(100, percent))
        try:
            from ctypes import cast, POINTER

            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(percent / 100.0, None)
            return f"Volume set to {percent}%."
        except Exception as exc:
            return f"Could not set volume (pycaw required): {exc}"

    def _power_command(self, action: str) -> list[str] | None:
        return {
            "shutdown": ["shutdown", "/s", "/t", "1"],
            "restart": ["shutdown", "/r", "/t", "1"],
            "logout": ["shutdown", "/l"],
        }.get(action)
