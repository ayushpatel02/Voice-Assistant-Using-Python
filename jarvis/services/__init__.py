"""Cross-cutting infrastructure shared by skills."""

from __future__ import annotations

from dataclasses import dataclass

from ..config.settings import Settings
from .scheduler import Scheduler
from .store import Store


@dataclass
class Services:
    store: Store
    scheduler: Scheduler

    @classmethod
    def create(cls, settings: Settings) -> "Services":
        store = Store(settings.data_dir / "jarvis.db")
        scheduler = Scheduler()
        return cls(store=store, scheduler=scheduler)

    def shutdown(self) -> None:
        self.scheduler.shutdown()
        self.store.close()


__all__ = ["Services", "Store", "Scheduler"]
