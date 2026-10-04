"""Token service. Depends only on contract.py.

Tokens are stateless: value = "<random>.<hmac>" where the HMAC is
computed over (user, expires, random) with a process key. A forged
token (wrong user/expires pairing, missing or bad signature, or any
string that is not a well-formed token dict/JSON) is rejected.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
from typing import Any, Union

from contract import Token, now_ts

TOKEN_TTL_SECONDS = 3600

# Key is stable within a process; set TOKEN_SIGNING_KEY for cross-process
# validation. Never embedded in the token itself.
_env_key = os.environ.get("TOKEN_SIGNING_KEY")
_SIGNING_KEY: bytes = _env_key.encode() if _env_key else secrets.token_bytes(32)


def _sign(user: str, expires: int, rand: str) -> str:
    msg = f"{user}|{expires}|{rand}".encode()
    return hmac.new(_SIGNING_KEY, msg, hashlib.sha256).hexdigest()


def issue_token(user: str) -> Token:
    """Issue a token for `user` that expires in 3600 seconds."""
    if not isinstance(user, str) or not user:
        raise ValueError("user must be a non-empty string")
    rand = secrets.token_hex(32)
    expires = now_ts() + TOKEN_TTL_SECONDS
    value = f"{rand}.{_sign(user, expires, rand)}"
    return Token(value=value, user=user, expires=expires)


def _token_payload(token_or_str: Any) -> "dict | None":
    """Normalize input to a dict payload; None if not token-shaped."""
    if isinstance(token_or_str, Token):
        return token_or_str.to_dict()
    if isinstance(token_or_str, dict):
        return token_or_str
    if isinstance(token_or_str, str):
        try:
            d = json.loads(token_or_str)
        except (ValueError, TypeError):
            return None
        return d if isinstance(d, dict) else None
    return None


def verify_token(token_or_str: Union[Token, dict, str]) -> "str | None":
    """Return the username when the token is valid and unexpired, else None.

    Accepts a Token object, a token dict (Token.to_dict()), or a JSON
    string of that dict. Rejects forgeries (bad/missing signature),
    expired tokens, and malformed input.
    """
    payload = _token_payload(token_or_str)
    if not isinstance(payload, dict):
        return None
    try:
        value = payload["value"]
        user = payload["user"]
        expires = int(payload["expires"])
    except (KeyError, TypeError, ValueError):
        return None
    if not isinstance(value, str) or not isinstance(user, str):
        return None
    parts = value.split(".")
    if len(parts) != 2:
        return None
    rand, sig = parts
    expected = _sign(user, expires, rand)
    if not hmac.compare_digest(sig, expected):
        return None
    if expires <= now_ts():
        return None
    return user
