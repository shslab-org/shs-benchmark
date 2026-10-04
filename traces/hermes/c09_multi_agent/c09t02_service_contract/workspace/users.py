"""User service. Depends only on contract.py (uses now_ts for record timestamps).

Passwords are stored as salted sha256; the plaintext password never
leaves these functions. In-memory store; swap _USERS for a real
backend without changing the public API.
"""
from __future__ import annotations

import hashlib
import hmac
import secrets
from typing import Dict, Tuple

from contract import now_ts

# username -> (salt_hex, sha256_hex, registered_at)
_USERS: Dict[str, Tuple[str, str, int]] = {}


def _hash(password: str, salt: str) -> str:
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()


def register(username: str, password: str) -> None:
    """Register a new user. Duplicate username raises ValueError."""
    if not isinstance(username, str) or not username:
        raise ValueError("username must be a non-empty string")
    if not isinstance(password, str) or not password:
        raise ValueError("password must be a non-empty string")
    if username in _USERS:
        raise ValueError(f"duplicate username: {username}")
    salt = secrets.token_hex(16)
    _USERS[username] = (salt, _hash(password, salt), now_ts())


def authenticate(username: str, password: str) -> bool:
    """True iff `username` exists and `password` matches its stored hash."""
    if not isinstance(username, str) or not isinstance(password, str):
        return False
    record = _USERS.get(username)
    if record is None:
        return False
    salt, stored, _created = record
    candidate = _hash(password, salt)
    return hmac.compare_digest(candidate, stored)
