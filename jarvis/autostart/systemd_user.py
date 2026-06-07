"""Linux autostart via a systemd *user* service (reaches the audio session)."""

from __future__ import annotations

import subprocess
from pathlib import Path

SERVICE_NAME = "jarvis.service"
SERVICE_PATH = Path.home() / ".config" / "systemd" / "user" / SERVICE_NAME


def unit_text(exec_cmd: str) -> str:
    return f"""[Unit]
Description=Jarvis voice assistant
After=default.target

[Service]
Type=simple
ExecStart={exec_cmd}
Restart=on-failure
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=default.target
"""


def install(exec_cmd: str) -> str:
    SERVICE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SERVICE_PATH.write_text(unit_text(exec_cmd))
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)
    subprocess.run(["systemctl", "--user", "enable", "--now", SERVICE_NAME], check=False)
    return f"Installed systemd user service at {SERVICE_PATH}"


def uninstall() -> str:
    subprocess.run(["systemctl", "--user", "disable", "--now", SERVICE_NAME], check=False)
    if SERVICE_PATH.exists():
        SERVICE_PATH.unlink()
    return "Removed Jarvis systemd user service."


def status() -> str:
    result = subprocess.run(
        ["systemctl", "--user", "is-enabled", SERVICE_NAME],
        capture_output=True,
        text=True,
    )
    state = (result.stdout or result.stderr).strip()
    return f"systemd user service: {state or 'not installed'}"
