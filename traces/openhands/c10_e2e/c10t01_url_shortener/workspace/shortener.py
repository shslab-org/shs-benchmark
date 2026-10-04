"""In-memory URL shortener with JSON file persistence."""

import hashlib
import json
import os
import string

_DATA_FILE = os.environ.get(
    "SHORTENER_DATA_FILE",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "shortener_data.json"),
)
_ALPHABET = string.ascii_lowercase + string.digits


class _Store:
    """code -> url mapping that persists to a JSON file."""

    def __init__(self, path: str):
        self.path = path
        self.codes: dict[str, str] = {}
        self.urls: dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.codes = dict(data.get("codes", {}))
                self.urls = dict(data.get("urls", {}))
            except (json.JSONDecodeError, OSError):
                self.codes = {}
                self.urls = {}

    def _save(self) -> None:
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"codes": self.codes, "urls": self.urls}, f, indent=2)
        os.replace(tmp, self.path)

    def add(self, code: str, url: str) -> None:
        self.codes[code] = url
        self.urls[url] = code
        self._save()

    def get(self, code: str) -> str | None:
        return self.codes.get(code)

    def code_exists(self, code: str) -> bool:
        return code in self.codes


_store = _Store(_DATA_FILE)


def _base36(n: int) -> str:
    if n == 0:
        return "0"
    chars = []
    while n:
        n, r = divmod(n, 36)
        chars.append(_ALPHABET[r])
    return "".join(reversed(chars))


def shorten(url: str, alias: str | None = None) -> str:
    """Return a short code for ``url``.

    Deterministic for the same url (hash-based, 6+ chars). A custom
    ``alias`` is honored unless it collides with an existing code, in
    which case ``ValueError`` is raised.
    """
    if not url:
        raise ValueError("url must be a non-empty string")

    if alias is not None:
        if _store.code_exists(alias):
            raise ValueError(f"alias {alias!r} already in use")
        code = alias
    elif url in _store.urls:
        code = _store.urls[url]
    else:
        digest = hashlib.sha256(url.encode("utf-8")).digest()
        code = _base36(int.from_bytes(digest[:8], "big"))
        if len(code) < 6:
            code = code.ljust(6, "0")
    _store.add(code, url)
    return code


def resolve(code: str) -> str | None:
    """Return the original url for ``code``, or None when unknown."""
    return _store.get(code)


def data_file() -> str:
    """Path of the JSON persistence file used by this module."""
    return _store.path
