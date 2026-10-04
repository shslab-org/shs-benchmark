def normalize_phone(p: str) -> str:
    return "".join(ch for ch in p if ch.isdigit())


def format_intl(p: str) -> str:
    digits = normalize_phone(p)
    if not digits:
        return ""
    cc_len = 1 if digits[0] == "1" else 2
    cc, rest = digits[:cc_len], digits[cc_len:]
    chunks = [rest[i : i + 3] for i in range(0, len(rest), 3)]
    return f"+{cc} " + " ".join(chunks)


if __name__ == "__main__":
    assert normalize_phone("+1 (555) 123-4567") == "15551234567"
    assert normalize_phone("abc") == ""
    assert normalize_phone("555.1234") == "5551234"
