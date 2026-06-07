"""Optional background scheduler for timers/reminders.

Wraps APScheduler when available; degrades to a no-op stub otherwise so the
rest of the system (and the tests) work without the extra dependency. Jobs
that fire simply invoke a callback with a message.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Callable

log = logging.getLogger(__name__)

Notifier = Callable[[str], None]


class Scheduler:
    def __init__(self, notifier: Notifier | None = None) -> None:
        self.notifier = notifier or (lambda msg: log.info("Reminder: %s", msg))
        self._scheduler = None
        try:
            from apscheduler.schedulers.background import BackgroundScheduler

            self._scheduler = BackgroundScheduler()
            self._scheduler.start()
            self.available = True
        except Exception:  # APScheduler missing or failed to start
            self.available = False
            log.info("APScheduler unavailable; reminders are stored but won't auto-fire")

    def schedule_at(self, when: datetime, message: str) -> bool:
        """Schedule a one-off notification. Returns whether it was armed live."""
        if not self._scheduler:
            return False
        self._scheduler.add_job(self.notifier, "date", run_date=when, args=[message])
        return True

    def shutdown(self) -> None:
        if self._scheduler:
            self._scheduler.shutdown(wait=False)
