"""macOS autostart via a launchd LaunchAgent (RunAtLoad)."""

from __future__ import annotations

import shlex
import subprocess
from pathlib import Path

LABEL = "com.jarvis.assistant"
PLIST_PATH = Path.home() / "Library" / "LaunchAgents" / f"{LABEL}.plist"


def plist_text(exec_cmd: str) -> str:
    args = "".join(f"        <string>{part}</string>\n" for part in shlex.split(exec_cmd))
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{LABEL}</string>
    <key>ProgramArguments</key>
    <array>
{args}    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
"""


def install(exec_cmd: str) -> str:
    PLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    PLIST_PATH.write_text(plist_text(exec_cmd))
    subprocess.run(["launchctl", "unload", str(PLIST_PATH)], check=False)
    subprocess.run(["launchctl", "load", str(PLIST_PATH)], check=False)
    return f"Installed launchd agent at {PLIST_PATH}"


def uninstall() -> str:
    subprocess.run(["launchctl", "unload", str(PLIST_PATH)], check=False)
    if PLIST_PATH.exists():
        PLIST_PATH.unlink()
    return "Removed Jarvis launchd agent."


def status() -> str:
    result = subprocess.run(["launchctl", "list", LABEL], capture_output=True, text=True)
    return "launchd agent: loaded" if result.returncode == 0 else "launchd agent: not loaded"
