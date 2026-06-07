"""Cross-platform autostart dispatch.

Picks the right OS backend and launches ``python -m jarvis voice`` at login so
Jarvis is always listening for the wake word after boot.
"""

from __future__ import annotations

import shlex
import sys


def launch_command() -> str:
    """The command the OS should run at login."""
    return f"{shlex.quote(sys.executable)} -m jarvis voice"


def _backend():
    if sys.platform.startswith("win"):
        from . import windows_task as backend
    elif sys.platform == "darwin":
        from . import launchd as backend
    else:
        from . import systemd_user as backend
    return backend


def install() -> str:
    return _backend().install(launch_command())


def uninstall() -> str:
    return _backend().uninstall()


def status() -> str:
    return _backend().status()


def run(action: str) -> str:
    actions = {"install": install, "uninstall": uninstall, "status": status}
    if action not in actions:
        return f"Unknown autostart action {action!r}. Use install|uninstall|status."
    return actions[action]()
