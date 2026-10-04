"""Shared contract: types and helpers used by the auth and users services."""

import time
from dataclasses import dataclass


def now_ts() -> int:
    return int(time.time())


@dataclass
class Token:
    value: str
    user: str
    expires: int

    def to_dict(self) -> dict:
        return {"value": self.value, "user": self.user, "expires": self.expires}

    @classmethod
    def from_dict(cls, d: dict) -> "Token":
        return cls(value=d["value"], user=d["user"], expires=d["expires"])
