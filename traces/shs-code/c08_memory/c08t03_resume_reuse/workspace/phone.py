def normalize_phone(p: str) -> str:
    """Strip everything except digits; return "" if there are no digits.

    Examples:
        normalize_phone("+1 (555) 123-4567") -> "15551234567"
        normalize_phone("abc")                -> ""
    """
    return "".join(ch for ch in p if ch.isdigit())


if __name__ == "__main__":
    assert normalize_phone("+1 (555) 123-4567") == "15551234567"
    assert normalize_phone("abc") == ""
    assert normalize_phone("tel: 800-555-0199 ext. 12") == "800555019912"
    print("All self-checks passed.")
