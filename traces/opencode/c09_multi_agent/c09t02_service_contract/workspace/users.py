import hashlib
import secrets


class _UserStore:
    def __init__(self):
        self._users: dict[str, tuple[str, str]] = {}

    def register(self, username: str, password: str) -> None:
        if username in self._users:
            raise ValueError(f"username already registered: {username}")
        salt = secrets.token_hex(16)
        digest = hashlib.sha256((salt + password).encode()).hexdigest()
        self._users[username] = (salt, digest)

    def authenticate(self, username: str, password: str) -> bool:
        entry = self._users.get(username)
        if entry is None:
            return False
        salt, digest = entry
        candidate = hashlib.sha256((salt + password).encode()).hexdigest()
        return secrets.compare_digest(candidate, digest)


_store = _UserStore()


def register(username: str, password: str) -> None:
    _store.register(username, password)


def authenticate(username: str, password: str) -> bool:
    return _store.authenticate(username, password)
