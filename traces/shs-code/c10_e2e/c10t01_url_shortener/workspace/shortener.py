"""URL shortener with deterministic hash-based codes and JSON persistence.

Storage: in-memory dict backed by a JSON file (``shortener_data.json``)
created next to this module. The file is auto-loaded on import and saved on
every mutation, so codes survive process restarts.

Public API:
    shorten(url, alias=None) -> str   deterministic short code (>= 6 chars)
    resolve(code) -> str | None        original URL, or None if unknown
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Optional

__all__ = ["shorten", "resolve", "DATA_FILE", "CODE_ALPHABET", "CODE_LEN"]

# Data file lives next to this module so any process using the module
# shares the same on-disk store.
DATA_FILE: Path = Path(__file__).resolve().parent / "shortener_data.json"

# 63 chars, unambiguous; guarantees codes are 6+ characters.
CODE_ALPHABET: str = (
    "0123456789"
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "-"
    "_"
)
CODE_LEN: int = 6

_ALIAS_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def _load() -> dict:
    """Load mapping from disk into memory (created on first save)."""
    global _mapping
    if DATA_FILE.exists():
        try:
            _mapping = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            _mapping = {}
    else:
        _mapping = {}
    return _mapping


def _save() -> None:
    DATA_FILE.write_text(json.dumps(_mapping, indent=2), encoding="utf-8")


# Auto-load on import so an existing store is usable immediately.
_mapping: dict = _load()


def _make_code(url: str) -> str:
    """Deterministic 6-char base63 code from the URL."""
    digest = hashlib.sha256(url.encode("utf-8")).digest()
    value = int.from_bytes(digest[:8], "big")
    code = []
    for _ in range(CODE_LEN):
        value, rem = divmod(value, len(CODE_ALPHABET))
        code.append(CODE_ALPHABET[rem])
    return "".join(reversed(code))


def shorten(url: str, alias: Optional[str] = None) -> str:
    """Shorten ``url`` and return its code.

    - Deterministic: the same ``url`` always yields the same code
      (unless a custom alias was used for it).
    - ``alias``: an explicit code. Must be a new, unused code;
      reusing one (or using an invalid one) raises ``ValueError``.
    """
    if not isinstance(url, str) or not url:
        raise ValueError("url must be a non-empty string")

    code = alias
    if code is not None:
        if not _ALIAS_RE.fullmatch(code) or len(code) < CODE_LEN:
            raise ValueError(
                f"invalid alias {code!r}: must be {CODE_LEN}+ chars of "
                "A-Z a-z 0-9 - _"
            )
        if code in _mapping:
            raise ValueError(f"alias {code!r} is already in use")
    else:
        # Same URL shortened twice -> same code (idempotent).
        for existing_code, existing_url in _mapping.items():
            if existing_url == url:
                return existing_code
        code = _make_code(url)

    _mapping[code] = url
    _save()
    return code


def resolve(code: str) -> Optional[str]:
    """Return the original URL for ``code``, or ``None`` if unknown."""
    return _mapping.get(code)
