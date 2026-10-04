import secrets

from contract import Token, now_ts

_TOKEN_TTL = 3600
_ISSUED: dict[str, Token] = {}


def issue_token(user: str) -> Token:
    token = Token(value=secrets.token_urlsafe(32), user=user, expires=now_ts() + _TOKEN_TTL)
    _ISSUED[token.value] = token
    return token


def verify_token(token_or_str):
    if isinstance(token_or_str, str):
        token = _ISSUED.get(token_or_str)
    elif isinstance(token_or_str, dict):
        token = Token.from_dict(token_or_str)
        token = _ISSUED.get(token.value)
    elif isinstance(token_or_str, Token):
        token = _ISSUED.get(token_or_str.value)
    else:
        return None
    if token is None:
        return None
    if now_ts() >= token.expires:
        return None
    return token.user
