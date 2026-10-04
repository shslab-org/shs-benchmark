"""Shared contract types for the service decomposition.

This module is the ONLY dependency allowed between auth.py and users.py.
It defines the common token type and a small time helper so that both
services integrate through the contract, never by importing each other.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, asdict, field
from typing import Any, Dict


def now_ts() -> int:
    """Current wall-clock time as integer seconds (int(time.time()))."""
    return int(time.time())


@dataclass
class Token:
    """Auth token shared between services via the contract.

    Attributes:
        value: opaque, unguessable token string.
        user:  the username the token was issued to.
        expires: unix timestamp (int seconds) after which the token is invalid.
    """

    value: str
    user: str
    expires: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Token":
        return cls(
            value=str(data["value"]),
            user=str(data["user"]),
            expires=int(data["expires"]),
        )
