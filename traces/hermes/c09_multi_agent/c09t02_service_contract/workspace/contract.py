"""Shared contract for the decomposed services.

Both auth.py and users.py depend ONLY on this module. They must not
import each other.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, fields
from typing import Any, Dict


def now_ts() -> int:
    """Current unix time as int seconds."""
    return int(time.time())


@dataclass
class Token:
    """Authentication token issued by the auth service.

    value: unguessable token material (opaque to consumers)
    user:  username the token was issued for
    expires: unix-ts (seconds) after which the token is invalid
    """

    value: str
    user: str
    expires: int

    def to_dict(self) -> Dict[str, Any]:
        return {f.name: getattr(self, f.name) for f in fields(self)}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Token":
        return cls(value=d["value"], user=d["user"], expires=int(d["expires"]))
