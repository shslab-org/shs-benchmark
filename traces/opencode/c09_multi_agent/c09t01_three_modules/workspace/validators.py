import re

_EMAIL_RE = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')

def is_email(s: str) -> bool:
    return bool(_EMAIL_RE.match(s))
