"""Test doubles: a fake platform and helpers to build a Context offline."""

from __future__ import annotations

from pathlib import Path

from jarvis.config.settings import Settings
from jarvis.core.session import Session
from jarvis.platform.base import PlatformController
from jarvis.services import Services
from jarvis.skills.base import Context


class FakePlatform(PlatformController):
    """Records calls instead of touching the real OS."""

    def __init__(self) -> None:
        super().__init__(allow_power=True)
        self.calls: list[tuple[str, object]] = []

    def open_app(self, name: str) -> str:
        self.calls.append(("open_app", name))
        return f"opened {name}"

    def open_url(self, url: str) -> str:
        self.calls.append(("open_url", url))
        return f"opened {url}"

    def set_volume(self, percent: int) -> str:
        self.calls.append(("set_volume", percent))
        return f"volume {percent}"

    def set_brightness(self, percent: int) -> str:
        self.calls.append(("set_brightness", percent))
        return f"brightness {percent}"

    def _power_command(self, action: str) -> list[str] | None:
        self.calls.append(("power", action))
        return None  # don't actually run anything


def make_context(tmp_path: Path) -> Context:
    settings = Settings()
    settings.data_dir = tmp_path
    services = Services.create(settings)
    return Context(
        settings=settings,
        session=Session(channel="test"),
        services=services,
        platform=FakePlatform(),
    )
