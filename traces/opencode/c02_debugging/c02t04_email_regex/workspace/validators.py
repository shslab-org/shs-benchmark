"""Email validation."""

import re

EMAIL_RE = re.compile(
    r"^(?!.*\.\.)"
    r"[a-z0-9%+_-]+(?:\.(?!\.)(?:[a-z0-9%+_-]+)*)*"
    r"@"
    r"(?:[a-z0-9-]+"
    r"(?:\.[a-z0-9-]+)*"
    r"\.[a-z]{2,})$"
)


def is_valid_email(addr):
    """Return True when addr is a syntactically valid email address."""
    return bool(EMAIL_RE.match(addr))
