"""Storage backend for the notes app.

Format: JSON (decision 2026-10-04, see MEMORY.md) — chosen over CSV
because note data is nested and JSON round-trips types losslessly.
"""

import json
from pathlib import Path


def save_notes(notes: list, path: str) -> None:
    """Persist notes to `path` as JSON.

    Parent directories are created if missing. `notes` must be JSON-serializable.
    """
    p = Path(path)
    if p.parent != p and not p.parent.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False)


def load_notes(path: str) -> list:
    """Load notes from `path` as a list.

    Returns [] if the file does not exist.
    Raises ValueError if the file exists but is not valid JSON.
    """
    p = Path(path)
    if not p.exists():
        return []
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)
