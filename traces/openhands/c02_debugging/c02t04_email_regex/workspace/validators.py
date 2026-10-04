"""Email validation (practical subset of email syntax)."""

import re

# local part: letters/digits/._%+-, no leading/trailing/consecutive dots
# domain: hyphenated labels, TLD of 2+ letters
EMAIL_RE = re.compile(
    r"^[A-Za-z0-9%+\-]+(\.[A-Za-z0-9%+\-]+)*"
    r"@[A-Za-z0-9]([A-Za-z0-9\-]*[A-Za-z0-9])?"
    r"(\.[A-Za-z0-9]([A-Za-z0-9\-]*[A-Za-z0-9])?)*"
    r"\.[A-Za-z]{2,}$"
)


def is_valid_email(addr):
    """Return True when addr is a syntactically valid email address."""
    return bool(EMAIL_RE.match(addr))
