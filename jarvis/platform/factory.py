"""Detect the OS and build the right platform controller."""

from __future__ import annotations

import sys

from .base import PlatformController


def build_platform(allow_power: bool = False) -> PlatformController:
    if sys.platform.startswith("win"):
        from .windows import WindowsController

        return WindowsController(allow_power=allow_power)
    if sys.platform == "darwin":
        from .macos import MacOSController

        return MacOSController(allow_power=allow_power)
    from .linux import LinuxController

    return LinuxController(allow_power=allow_power)
