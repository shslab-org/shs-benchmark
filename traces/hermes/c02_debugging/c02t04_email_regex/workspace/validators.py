"""Email validation: practical email syntax via regex."""

import re

# Local part: letters/digits/._%+- (dot never leading, trailing, or doubled).
# Domain: labels of letters/digits with inner hyphens (no leading/trailing
# hyphen), subdomains allowed, TLD of 2+ letters.
EMAIL_RE = re.compile(
    r"^(?:[A-Za-z0-9_%+-]+(?:\.[A-Za-z0-9_%+-]+)*)"  # local part
    r"@(?:(?:[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)\.)+"  # labels
    r"[A-Za-z]{2,}$"  # TLD
)


def is_valid_email(addr):
    """Return True when addr is a syntactically valid email address."""
    return bool(EMAIL_RE.match(addr))
