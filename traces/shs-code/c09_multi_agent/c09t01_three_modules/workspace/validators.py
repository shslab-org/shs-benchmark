"""validators: practical input validation helpers."""

import re

# Simple practical email pattern: local@domain.tld
#   - local: one or more allowed characters (no spaces, no bare @)
#   - domain: at least two dot-separated labels, each starting with a
#     letter/digit, ending with a TLD of >= 1 letter
_EMAIL_RE = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]+$"
)


def is_email(s: str) -> bool:
    """Return True if *s* looks like a valid email address (x@y.z style).

    Simple, practical check — not a full RFC 5322 validator:
      * exactly one ``@``
      * non-empty local part
      * domain containing at least one dot, with non-empty labels
        (a single-letter TLD such as ``.z`` is accepted)
      * no whitespace

    Examples:
        >>> is_email("user@example.com")
        True
        >>> is_email("a@b.co")
        True
        >>> is_email("x@y.z")
        True
        >>> is_email("no-at-sign.com")
        False
        >>> is_email("a@b")
        False
        >>> is_email("a b@c.com")
        False
        >>> is_email("@missing-local.com")
        False
    """
    if not isinstance(s, str) or " " in s or s.count("@") != 1:
        return False
    return bool(_EMAIL_RE.match(s))
