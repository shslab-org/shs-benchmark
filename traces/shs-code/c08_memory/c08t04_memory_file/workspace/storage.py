"""Storage backend for the tiny notes app.

Per the 2026-10-04 decision log entry in MEMORY.md, notes are persisted as
JSON (chosen over CSV because the data is nested and JSON round-trips
types losslessly).
"""

from __future__ import annotations

import json
from pathlib import Path


def save_notes(notes: list, path: str) -> None:
    """Persist `notes` to `path` as JSON.

    Parent directories are created if missing. The file is written
    atomically-enough for this app's needs (single writer), formatted
    with indentation so the file stays human-readable.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as fh:
        json.dump(notes, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def load_notes(path: str) -> list:
    """Load notes from `path` as a list.

    A missing file (or missing parent) yields an empty list rather than
    raising, matching the app's "no notes yet" state.
    """
    target = Path(path)
    if not target.exists():
        return []
    with target.open("r", encoding="utf-8") as fh:
        return json.load(fh)
