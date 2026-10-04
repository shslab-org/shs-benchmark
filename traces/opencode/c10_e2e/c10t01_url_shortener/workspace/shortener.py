"""URL shortener library with in-memory + JSON file persistence.

Codes are deterministic: the same URL always yields the same code
(hash-based, 6+ characters). Custom aliases are honored; alias
collisions raise ValueError.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import threading

_ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
_CODE_LEN = 8
_ALIAS_RE = re.compile(r"^[A-Za-z0-9_-]{4,64}$")
_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shortener_data.json")

_lock = threading.Lock()
_store: dict[str, str] = {}
_url_to_code: dict[str, str] = {}
_loaded = False


def _load() -> None:
    global _loaded
    if _loaded:
        return
    _loaded = True
    if os.path.exists(_DATA_FILE):
        try:
            with open(_DATA_FILE, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict):
                for code, url in data.items():
                    _store[str(code)] = str(url)
        except (json.JSONDecodeError, OSError):
            _store.clear()
    for code, url in _store.items():
        _url_to_code[url] = code


def _save() -> None:
    global _loaded
    _load()
    with open(_DATA_FILE, "w", encoding="utf-8") as fh:
        json.dump(_store, fh, ensure_ascii=False, sort_keys=True)


def _make_code(url: str) -> str:
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
    return "".join(_ALPHABET[int(digest[i : i + 2], 16) % len(_ALPHABET)] for i in range(0, _CODE_LEN * 2, 2))


def shorten(url: str, alias: str | None = None) -> str:
    """Return the short code for *url*.

    Deterministic for the same url (hash-based, 8 chars).
    A custom *alias* is honored when given; a collision with an
    existing code (any url) raises ValueError.
    """
    global _loaded
    if not url:
        raise ValueError("url must be a non-empty string")
    with _lock:
        _load()
        if alias is not None:
            if not _ALIAS_RE.match(alias):
                raise ValueError(f"invalid alias: {alias!r}")
            if alias in _store:
                raise ValueError(f"alias collision: {alias!r} is already in use")
            _store[alias] = url
            _url_to_code[url] = alias
            _save()
            return alias
        existing = _url_to_code.get(url)
        if existing is not None:
            return existing
        code = _make_code(url)
        while code in _store:
            code = _make_code(code + url)
        _store[code] = url
        _url_to_code[url] = code
        _save()
        return code


def resolve(code: str) -> str | None:
    """Return the original url for *code*, or None when unknown."""
    with _lock:
        _load()
        return _store.get(code)


def _reset() -> None:
    """Clear the in-memory store and remove the data file (test helper)."""
    global _loaded
    with _lock:
        _store.clear()
        _url_to_code.clear()
        _loaded = False
        if os.path.exists(_DATA_FILE):
            os.remove(_DATA_FILE)
