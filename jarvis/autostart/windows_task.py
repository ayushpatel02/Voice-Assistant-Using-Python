"""Windows autostart via a Task Scheduler 'at log on' task."""

from __future__ import annotations

import subprocess

TASK_NAME = "JarvisAssistant"


def create_command(exec_cmd: str) -> list[str]:
    return [
        "schtasks",
        "/Create",
        "/SC",
        "ONLOGON",
        "/TN",
        TASK_NAME,
        "/TR",
        exec_cmd,
        "/RL",
        "LIMITED",
        "/F",
    ]


def install(exec_cmd: str) -> str:
    subprocess.run(create_command(exec_cmd), check=False)
    return f"Created scheduled task {TASK_NAME!r} (runs at logon)."


def uninstall() -> str:
    subprocess.run(["schtasks", "/Delete", "/TN", TASK_NAME, "/F"], check=False)
    return f"Removed scheduled task {TASK_NAME!r}."


def status() -> str:
    result = subprocess.run(
        ["schtasks", "/Query", "/TN", TASK_NAME], capture_output=True, text=True
    )
    return "scheduled task: present" if result.returncode == 0 else "scheduled task: absent"
