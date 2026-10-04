def normalize_phone(p: str) -> str:
    """Strip everything except digits; return "" when no digits are present."""
    digits = [c for c in p if c.isdigit()]
    return "".join(digits)


def format_intl(p: str) -> str:
    """Format as +<country_code> with the rest grouped in chunks of 3."""
    digits = normalize_phone(p)
    if not digits:
        return ""
    if digits.startswith("1"):
        country_code, rest = digits[0], digits[1:]
    else:
        country_code, rest = digits[:2], digits[2:]
    chunks = [rest[i : i + 3] for i in range(0, len(rest), 3)]
    return "+" + country_code + " " + " ".join(chunks)


if __name__ == "__main__":
    assert normalize_phone("+1 (555) 123-4567") == "15551234567"
    assert normalize_phone("abc") == ""
    assert normalize_phone("1-800-555-0199") == "18005550199"
    assert format_intl("+1 (555) 123-4567") == "+1 555 123 456 7"
    assert format_intl("44 20 7123 0000") == "+44 207 123 000 0"
    assert format_intl("abc") == ""
