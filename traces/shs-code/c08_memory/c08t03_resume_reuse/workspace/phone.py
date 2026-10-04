"""Phone number normalization helper.

Usage:
    from phone import normalize_phone, format_intl
    normalize_phone("+1 (555) 123-4567")  # -> "15551234567"
    normalize_phone("abc")                # -> ""
    format_intl("+1 (555) 123-4567")      # -> "+1 555 123 456 7"

Self-checks: run `python3 phone.py` and expect "all self-checks passed".
"""


def normalize_phone(p: str) -> str:
    """Strip everything except digits from p; return "" if no digits.

    Examples:
        "+1 (555) 123-4567" -> "15551234567"
        "abc"               -> ""
    """
    return "".join(ch for ch in p if ch.isdigit())


def format_intl(p: str) -> str:
    """Format p as "+<country_code> <rest in chunks of 3>".

    Normalizes via normalize_phone first (reused); returns "" if no digits.
    Country code: first 1 digit when the normalized number starts with "1",
    otherwise the first 2 digits. The remainder is grouped left-to-right in
    chunks of 3, joined by single spaces.

    Examples:
        "+1 (555) 123-4567" -> "+1 555 123 456 7"
        "44 20 7123 0000"   -> "+44 207 123 000 0"
        "abc"               -> ""
    """
    digits = normalize_phone(p)
    if not digits:
        return ""

    # Country code: 1 leading digit for "1" (NA prefix), else 2 digits.
    cc_len = 1 if digits[0] == "1" else 2
    cc = digits[:cc_len]
    rest = digits[cc_len:]

    if not rest:
        # CC-only input: no trailing space (e.g. "44" -> "+44")
        return "+" + cc

    chunks = [rest[i:i + 3] for i in range(0, len(rest), 3)]
    return "+" + cc + " " + " ".join(chunks)


if __name__ == "__main__":
    # Quick self-checks
    assert normalize_phone("+1 (555) 123-4567") == "15551234567"
    assert normalize_phone("abc") == ""
    assert normalize_phone("call me at 555.1234") == "5551234"

    assert format_intl("+1 (555) 123-4567") == "+1 555 123 456 7"
    assert format_intl("44 20 7123 0000") == "+44 207 123 000 0"
    assert format_intl("abc") == ""
    assert format_intl("") == ""
    print("all self-checks passed")
