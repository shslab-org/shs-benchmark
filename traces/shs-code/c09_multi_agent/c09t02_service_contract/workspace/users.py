"""User service — depends ONLY on contract.py.

Stores salted SHA-256 password digests. No plaintext passwords are
ever kept. Each user gets a random 16-byte salt; the stored digest
is ``sha256(salt || password)``.
"""

from __future__ import annotations

import hashlib
import secrets
from typing import Dict, Tuple

# In-memory storage keyed by username -> (salt_hex, hex_digest).
_USERS: Dict[str, Tuple[str, str]] = {}

_SALT_BYTES = 16


def _digest(salt_hex: str, password: str) -> str:
    return hashlib.sha256(
        bytes.fromhex(salt_hex) + password.encode("utf-8")
    ).hexdigest()


def register(username: str, password: str) -> None:
    """Register a new user.

    Raises:
        ValueError: if the username or password is empty, or the
                    username already exists.
    """
    if not username:
        raise ValueError("username must be non-empty")
    if not password:
        raise ValueError("password must be non-empty")
    if username in _USERS:
        raise ValueError(f"duplicate username: {username!r}")

    salt = secrets.token_bytes(_SALT_BYTES)
    digest = _digest(salt.hex(), password)
    _USERS[username] = (salt.hex(), digest)


def authenticate(username: str, password: str) -> bool:
    """Return True when ``username``/``password`` match a registered record.

    Unknown usernames return ``False`` (no exception, no timing leak
    beyond the standard ``secrets.compare_digest`` cost).
    """
    record = _USERS.get(username)
    if record is None:
        return False
    salt_hex, expected = record
    return secrets.compare_digest(_digest(salt_hex, password), expected)


def _reset_for_tests() -> None:
    """Clear all registered users. Test-only hook."""
    _USERS.clear()
