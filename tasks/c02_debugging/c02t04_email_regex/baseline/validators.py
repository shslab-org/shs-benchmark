"""Email validation. BUG: regex accepts invalid and rejects valid addresses."""

import re

EMAIL_RE = re.compile(r"^[a-z]+@[a-z]+\.[a-z]{2}$")   # BUG: too strict/wrong


def is_valid_email(addr):
    """Return True when addr is a syntactically valid email address."""
    return bool(EMAIL_RE.match(addr))
