"""User management module.

Single-file, stdlib-only implementation of the agreed 10-point spec:

1. create_user(username, email, password) returns a user dict.
2. Emails are stored lowercased.
3. Usernames are unique case-insensitively; duplicate (any casing) raises ValueError.
4. Usernames are stored lowercased.
5. Minimum password length is 12; shorter raises ValueError.
6. Returned dict keys: username, email, password_hash, created_at.
7. Plain passwords are never stored/returned; password_hash is a salted
   sha256 hexdigest; repr() of the user never shows the plain password.
8. Duplicate email (case-insensitive) raises ValueError.
9. All errors are ValueError (no bare exceptions).
10. Single file, no external dependencies (stdlib only).
"""

import hashlib
import secrets
from datetime import datetime, timezone

# In-memory user store: normalized (lowercased) username -> user dict.
_users = {}
# Set of normalized (lowercased) emails for O(1) duplicate checks.
_emails = set()


def _now_iso_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash_password(password: str, salt: str) -> str:
    """Salted sha256 hexdigest of the password."""
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


def create_user(username: str, email: str, password: str) -> dict:
    """Create and register a user; returns the user dict.

    Raises ValueError for: empty username/email, short password (<12),
    duplicate username (case-insensitive), duplicate email (case-insensitive).
    """
    # Normalize at intake.
    name = (username or "").lower()
    mail = (email or "").lower()

    if not name:
        raise ValueError("username must not be empty")
    if not mail:
        raise ValueError("email must not be empty")
    if len(password) < 12:
        raise ValueError("password must be at least 12 characters")
    if name in _users:
        raise ValueError(f"username {username!r} is already registered")
    if mail in _emails:
        raise ValueError(f"email {email!r} is already registered")

    salt = secrets.token_hex(16)
    user = {
        "username": name,
        "email": mail,
        "password_hash": _hash_password(password, salt),
        "created_at": _now_iso_utc(),
    }
    _users[name] = user
    _emails.add(mail)
    return user


def reset() -> None:
    """Clear the in-memory store (useful for tests)."""
    _users.clear()
    _emails.clear()


def get_user(username: str) -> dict | None:
    """Look up a user by (case-insensitive) username; None if absent."""
    return _users.get((username or "").lower())
