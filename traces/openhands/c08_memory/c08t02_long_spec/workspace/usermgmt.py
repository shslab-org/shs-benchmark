"""User management module.

A single-file module with no external dependencies.

Spec:
1. create_user(username, email, password) returns a user dict
2. emails are stored lowercased
3. usernames are unique, case-insensitively (duplicate raises ValueError)
4. usernames are stored lowercased
5. minimum password length is 12 characters (shorter raises ValueError)
6. the returned dict has keys: username, email, password_hash, created_at
7. passwords are never returned in plain text - password_hash contains a
   salted sha256 hexdigest, and repr() of the user never shows the plain
   password
8. duplicate email registrations raise ValueError
9. all errors are ValueError (no bare exceptions)
10. the module is a single file usermgmt.py with no external dependencies
"""

import hashlib
import secrets
from datetime import datetime, timezone

# In-memory user store: username -> user dict.
_users = {}
# In-memory email store: email (lowercased) -> True, to detect duplicates.
_emails = set()


def _hash_password(password: str) -> str:
    """Return a salted SHA-256 hexdigest for the given password."""
    salt = secrets.token_hex(16)
    digest = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return f"{salt}${digest}"


def create_user(username: str, email: str, password: str) -> dict:
    """Create a new user and return their user dict.

    All errors are raised as ValueError (no bare exceptions).
    """
    # Validate password length first.
    if len(password) < 12:
        raise ValueError(
            f"Password must be at least 12 characters (got {len(password)})"
        )

    # Normalize and validate username (case-insensitive uniqueness).
    user_key = username.lower()
    if user_key in _users:
        raise ValueError(
            f"Username {username!r} is already taken (case-insensitive)"
        )

    # Normalize and validate email (uniqueness).
    email_key = email.lower()
    if email_key in _emails:
        raise ValueError(f"Email {email!r} is already registered")

    # Build the user dict with exactly the spec'd keys.
    user = {
        "username": user_key,
        "email": email_key,
        "password_hash": _hash_password(password),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    # Persist into the in-memory stores.
    _users[user_key] = user
    _emails.add(email_key)
    return user


def _repr_user(user: dict) -> str:
    """Return a safe repr that never exposes the plain password.

    The user dict itself only ever contains a password_hash, but we also
    guarantee repr() of any user object shows no plain text password.
    """
    return (
        f"User(username={user['username']!r}, "
        f"email={user['email']!r}, "
        f"password_hash={user['password_hash']!r}, "
        f"created_at={user['created_at']!r})"
    )


def get_user(username: str) -> dict:
    """Look up an existing user by username (case-insensitive).

    Raises ValueError if the username is not found.
    """
    user = _users.get(username.lower())
    if user is None:
        raise ValueError(f"Username {username!r} not found")
    return user


def reset() -> None:
    """Clear all users and emails (useful for testing)."""
    _users.clear()
    _emails.clear()
