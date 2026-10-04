"""Module 2: simple input validators."""

import re

# Simple practical email shape: x@y.z
# - local part: one or more "word-ish" chars, may contain . _ -
# - exactly one @
# - domain: labels separated by dots, at least one dot overall
_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$")


def is_email(s: str) -> bool:
    """Return True if *s* looks like a practical email address (x@y.z)."""
    if not isinstance(s, str):
        return False
    s = s.strip()
    if s.count("@") != 1:
        return False
    return bool(_EMAIL_RE.match(s))
