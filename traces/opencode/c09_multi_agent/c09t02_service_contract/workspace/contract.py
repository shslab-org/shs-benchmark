import time


def now_ts() -> int:
    return int(time.time())


class Token:
    def __init__(self, value: str, user: str, expires: int):
        self.value = value
        self.user = user
        self.expires = expires

    def to_dict(self) -> dict:
        return {"value": self.value, "user": self.user, "expires": self.expires}

    @classmethod
    def from_dict(cls, data: dict) -> "Token":
        return cls(value=data["value"], user=data["user"], expires=data["expires"])
