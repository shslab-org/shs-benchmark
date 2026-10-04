"""Email validation (practical syntax)."""

import re

# Local part: letters/digits/._%+- ; no leading dot, no consecutive dots.
#   First char must not be a dot; every dot must be immediately followed by
#   an allowed char, which simultaneously forbids trailing and doubled dots.
LOCAL = r"[A-Za-z0-9_%+-](?:[A-Za-z0-9_%+-]|\.(?=[A-Za-z0-9_%+-]))*"
# Domain: labels of alnum/hyphens starting & ending with alnum,
# optional subdomain labels, TLD of 2+ letters.
LABEL = r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?"
EMAIL_RE = re.compile(
    r"^"
    r"(?:" + LOCAL + r")"
    r"@"
    r"(?:" + LABEL + r"(?:\." + LABEL + r")*\." + r"[A-Za-z]{2,})"
    r"$"
)


def is_valid_email(addr):
    """Return True when addr is a syntactically valid email address."""
    return bool(EMAIL_RE.match(addr))
