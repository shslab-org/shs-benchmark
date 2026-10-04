def normalize_phone(p: str) -> str:
    """Strip everything except digits; return "" if there are none."""
    return "".join(ch for ch in p if ch.isdigit())


def format_intl(p: str) -> str:
    """Normalize p, then format as +<country_code> <rest in groups of 3>.

    Country code is the first 1 digit when the number starts with 1,
    otherwise the first 2 digits. The remainder is grouped in chunks
    of 3 digits (left to right), joined by single spaces.
    Returns "" when the input has no digits.
    """
    digits = normalize_phone(p)
    if not digits:
        return ""
    if digits[0] == "1":
        cc, rest = digits[0], digits[1:]
    else:
        cc, rest = digits[:2], digits[2:]
    if not rest:
        return "+" + cc
    chunks = [rest[i : i + 3] for i in range(0, len(rest), 3)]
    return f"+{cc} " + " ".join(chunks)


if __name__ == "__main__":
    # quick self-checks
    assert normalize_phone("+1 (555) 123-4567") == "15551234567"
    assert normalize_phone("abc") == ""
    assert format_intl("+1 (555) 123-4567") == "+1 555 123 456 7"
    assert format_intl("44 20 7123 0000") == "+44 207 123 000 0"
    assert format_intl("abc") == ""
    print("all checks passed")
