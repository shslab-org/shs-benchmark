"""usermgmt - user management module.

Single-file module with no external dependencies (Python stdlib only),
implementing the agreed 10-point specification:

 1. create_user(username, email, password) returns a user dict
 2. emails are stored lowercased
 3. usernames are unique, case-insensitively (a second registration of
    the same name in any casing raises ValueError)
 4. usernames are stored lowercased
 5. minimum password length is 12 characters (shorter raises ValueError)
 6. the returned dict has keys: username, email, password_hash, created_at
 7. passwords are never returned in plain text - password_hash holds a
    salted sha256 hexdigest, and repr() of the user never shows the
    plain password
 8. duplicate email registrations raise ValueError
 9. all errors are ValueError (no bare exceptions)
10. the module is a single file with no external dependencies

State: an in-memory registry lives in this module for the lifetime of
the process; the uniqueness checks (points 3 and 8) consult it.
"""

from __future__ import annotations

import datetime
import hashlib
import os

__all__ = ["User", "create_user", "MIN_PASSWORD_LENGTH"]

#: Minimum password length (spec point 5).
MIN_PASSWORD_LENGTH = 12

_SALT_BYTES = 16


class User(dict):
    """A user record.

    Behaves as a plain dict carrying exactly the keys
    ``username, email, password_hash, created_at`` (spec point 6).
    The plain password is never stored in the record, and
    ``__repr__`` masks the ``password_hash`` value so no secret
    material is echoed into logs or traces (spec point 7).
    """

    def __repr__(self) -> str:
        items = []
        for key, value in dict.items(self):
            shown = "'***'" if key == "password_hash" else repr(value)
            items.append(f"{key!r}: {shown}")
        return "{" + ", ".join(items) + "}"


# In-memory registries, keyed by lowercased names/emails so that
# uniqueness is case-insensitive (spec points 3 and 8).
_users_by_username: dict[str, User] = {}
_users_by_email: dict[str, User] = {}


def _hash_password(password: str, salt: str) -> str:
    """Return a salted SHA-256 hexdigest (spec point 7)."""
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


def create_user(username: str, email: str, password: str) -> User:
    """Register a new user and return the user record (a dict).

    ``username`` and ``email`` are stored lowercased (spec points 2
    and 4); ``password_hash`` is a salted sha256 hexdigest and the
    plain password is never stored, returned, or echoed (spec
    point 7). ``created_at`` is an ISO-8601 UTC timestamp.

    Every error raised by this function is a ``ValueError``
    (spec point 9):

    * ``username``, ``email`` or ``password`` is not a ``str``
    * ``password`` is shorter than 12 characters (spec point 5)
    * ``username`` is already registered, in any casing (spec point 3)
    * ``email`` is already registered, in any casing (spec point 8)
    """
    if not isinstance(username, str):
        raise ValueError("username must be a string")
    if not isinstance(email, str):
        raise ValueError("email must be a string")
    if not isinstance(password, str):
        raise ValueError("password must be a string")

    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(
            f"password must be at least {MIN_PASSWORD_LENGTH} "
            f"characters (got {len(password)})"
        )

    name = username.lower()
    addr = email.lower()

    if name in _users_by_username:
        raise ValueError(f"username {username!r} is already registered")
    if addr in _users_by_email:
        raise ValueError(f"email {email!r} is already registered")

    salt = os.urandom(_SALT_BYTES).hex()
    record = User(
        username=name,
        email=addr,
        password_hash=_hash_password(password, salt),
        created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    )
    _users_by_username[name] = record
    _users_by_email[addr] = record
    return record
