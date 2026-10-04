"""Token service — depends ONLY on contract.py.

Issue and verify unguessable bearer tokens. Values are generated
with the ``secrets`` module (CSPRNG), so no client can forge or
predict a valid one. A module-level registry maps value -> Token so
that string values can be verified after the fact (e.g. from an HTTP
Authorization header) while still requiring the exact issued value.
"""

from __future__ import annotations

import secrets
from typing import Union

from contract import Token, now_ts

# Token lifetime in seconds.
TOKEN_TTL_SECONDS = 3600

# 256 bits of CSPRNG entropy per token — far beyond brute-force.
_TOKEN_ENTROPY_BYTES = 32

# value (str) -> Token; lets string-based verification find the owner.
_REGISTRY: dict[str, "Token"] = {}


def _new_token_value() -> str:
    """Generate an unguessable token value (CSPRNG-backed)."""
    return secrets.token_urlsafe(_TOKEN_ENTROPY_BYTES)


def issue_token(user: str) -> Token:
    """Issue a new token for ``user`` expiring in 3600 seconds.

    Returns a fresh :class:`contract.Token` with an unguessable random
    value and ``expires == now_ts() + TOKEN_TTL_SECONDS``.
    """
    if not user:
        raise ValueError("user must be a non-empty string")
    value = _new_token_value()
    tok = Token(
        value=value,
        user=user,
        expires=now_ts() + TOKEN_TTL_SECONDS,
    )
    _REGISTRY[value] = tok
    return tok


def verify_token(token_or_str: Union[Token, str]) -> "str | None":
    """Validate a token.

    Accepts either a :class:`contract.Token` instance or the raw string
    value (e.g. taken from an HTTP ``Authorization: Bearer <value>``
    header). Returns the owning username when the token is valid and
    unexpired; ``None`` for forged, malformed, unknown, or expired
    values.
    """
    if token_or_str is None:
        return None

    if isinstance(token_or_str, Token):
        tok = token_or_str
        # Require that this exact Token was issued by this service.
        if tok.value not in _REGISTRY:
            return None
    elif isinstance(token_or_str, str):
        tok = _REGISTRY.get(token_or_str)
        if tok is None:
            return None
    else:
        return None

    if not tok.value:
        return None
    if tok.expires < now_ts():
        return None

    return tok.user


def _reset_for_tests() -> None:
    """Clear the registry. Test-only hook."""
    _REGISTRY.clear()
