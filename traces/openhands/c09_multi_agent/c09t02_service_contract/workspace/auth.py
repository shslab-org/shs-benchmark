"""Token service: issues and verifies unguessable tokens."""

import secrets

from contract import Token, now_ts

_TOKEN_TTL = 3600

_tokens: dict[str, Token] = {}


def issue_token(user: str) -> Token:
    token = Token(value=secrets.token_urlsafe(32), user=user, expires=now_ts() + _TOKEN_TTL)
    _tokens[token.value] = token
    return token


def verify_token(token_or_str) -> str | None:
    if isinstance(token_or_str, Token):
        value = token_or_str.value
    else:
        value = token_or_str
    token = _tokens.get(value)
    if token is None:
        return None
    if now_ts() >= token.expires:
        del _tokens[value]
        return None
    return token.user
