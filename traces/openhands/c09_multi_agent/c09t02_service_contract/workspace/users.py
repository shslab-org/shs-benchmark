"""User service: registration and authentication with salted sha256 passwords."""

import hashlib
import secrets

from contract import Token, now_ts  # noqa: F401  (contract types available to callers)

# username -> (salt, sha256 hex digest)
_users: dict[str, tuple[str, str]] = {}


def _hash(password: str, salt: str) -> str:
    return hashlib.sha256((salt + password).encode()).hexdigest()


def register(username: str, password: str) -> None:
    if username in _users:
        raise ValueError(f"username already registered: {username}")
    salt = secrets.token_hex(16)
    _users[username] = (salt, _hash(password, salt))


def authenticate(username: str, password: str) -> bool:
    entry = _users.get(username)
    if entry is None:
        return False
    salt, digest = entry
    return secrets.compare_digest(_hash(password, salt), digest)
