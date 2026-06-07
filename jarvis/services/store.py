"""Tiny SQLite-backed persistence for notes, to-dos, and reminders.

Uses only the standard library so it works everywhere with no extra deps.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Reminder:
    id: int
    text: str
    due_iso: str
    done: bool


class Store:
    def __init__(self, db_path: Path) -> None:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                due_iso TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            );
            """
        )
        self._conn.commit()

    # --- notes / to-dos ---
    def add_note(self, text: str) -> int:
        cur = self._conn.execute("INSERT INTO notes (text) VALUES (?)", (text,))
        self._conn.commit()
        return int(cur.lastrowid)

    def list_notes(self) -> list[str]:
        rows = self._conn.execute("SELECT text FROM notes ORDER BY id").fetchall()
        return [r["text"] for r in rows]

    def clear_notes(self) -> int:
        cur = self._conn.execute("DELETE FROM notes")
        self._conn.commit()
        return cur.rowcount

    # --- reminders ---
    def add_reminder(self, text: str, due_iso: str) -> int:
        cur = self._conn.execute(
            "INSERT INTO reminders (text, due_iso) VALUES (?, ?)", (text, due_iso)
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def list_reminders(self, include_done: bool = False) -> list[Reminder]:
        query = "SELECT * FROM reminders"
        if not include_done:
            query += " WHERE done = 0"
        query += " ORDER BY due_iso"
        rows = self._conn.execute(query).fetchall()
        return [
            Reminder(id=r["id"], text=r["text"], due_iso=r["due_iso"], done=bool(r["done"]))
            for r in rows
        ]

    def mark_reminder_done(self, reminder_id: int) -> None:
        self._conn.execute("UPDATE reminders SET done = 1 WHERE id = ?", (reminder_id,))
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()
