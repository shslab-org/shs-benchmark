"""A tiny URL shortener.

In-memory store backed by a JSON file that lives next to this module, so
short codes survive process restarts. Codes are deterministic per URL when
no custom alias is supplied (hash-based).

Public API:
    shorten(url, alias=None) -> str
    resolve(code) -> str | None

Test-only helpers:
    reset(store=None, data_file=None)
"""

from __future__ import annotations

import hashlib
import json
import threading
from pathlib import Path

# The JSON data file lives in the same directory as this module.
_DATA_FILE = Path(__file__).with_name("data.json")

_lock = threading.Lock()
_store: dict[str, str] = {}
_loaded = False


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def _ensure_loaded() -> None:
    """Load the JSON data file into the in-memory store on first use."""
    global _loaded
    if _loaded:
        return
    if _DATA_FILE.exists():
        with _DATA_FILE.open() as f:
            data = json.load(f)
        if isinstance(data, dict):
            _store.update(data)
    _loaded = True


def _save() -> None:
    """Persist the current store to the JSON data file (atomically)."""
    if _DATA_FILE is None:
        return
    tmp = _DATA_FILE.with_suffix(".tmp")
    with tmp.open("w") as f:
        json.dump(_store, f, indent=2, sort_keys=True)
    tmp.replace(_DATA_FILE)


def _hash_code(url: str) -> str:
    """Deterministic 8-char code derived from the URL."""
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:8]


def reset(store: dict[str, str] | None = None,
          data_file: str | Path | None = None) -> None:
    """Reset module state (intended for tests).

    Pass `data_file` to point the module at a different JSON file (e.g. a
    pytest tmp dir). Pass `store` to pre-seed the in-memory mapping.
    """
    global _store, _DATA_FILE, _loaded
    with _lock:
        _store = dict(store) if store is not None else {}
        if data_file is not None:
            _DATA_FILE = Path(data_file)
        _loaded = False
        _ensure_loaded()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def shorten(url: str, alias: str | None = None) -> str:
    """Return a short code for `url`, persisting it to the store.

    - When `alias` is given it is used as the code. Re-using an alias that
      already maps to a *different* URL raises ``ValueError``.
    - When `alias` is None a deterministic hash-based code (8 chars) is used,
      so the same URL always yields the same code.
    """
    with _lock:
        _ensure_loaded()
        if not isinstance(url, str) or not url:
            raise ValueError("url must be a non-empty string")

        code = alias.strip() if alias else _hash_code(url)
        if not code:
            raise ValueError("alias must be a non-empty string")

        existing = _store.get(code)
        if existing is not None and existing != url:
            if alias:
                raise ValueError(f"alias {code!r} is already in use")
            # Hash collision with a different URL: let the new mapping win,
            # keeping behaviour deterministic per URL.

        _store[code] = url
        _save()
        return code


def resolve(code: str) -> str | None:
    """Return the original URL for `code`, or None when unknown."""
    with _lock:
        _ensure_loaded()
        return _store.get(code)
