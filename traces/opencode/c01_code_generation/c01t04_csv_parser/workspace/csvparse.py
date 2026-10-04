"""RFC-4180-style CSV parser.

Parses comma-separated values with quoted fields (commas, newlines and
doubled quotes are supported inside quotes).
"""


def parse_csv(text: str) -> list[list[str]]:
    """Parse CSV text into a list of records, each a list of strings.

    Handles:
    - comma-separated fields, one record per line
    - quoted fields containing commas, newlines and escaped quotes
      (a doubled "" inside quotes becomes a single ")
    - empty fields (e.g. ``a,,b``)
    - a trailing newline at the end of the input (does not yield an
      extra empty record)
    """
    rows: list[list[str]] = []
    row: list[str] = []
    field: list[str] = []
    in_quotes = False
    i = 0
    n = len(text)

    while i < n:
        ch = text[i]
        if in_quotes:
            if ch == '"':
                if i + 1 < n and text[i + 1] == '"':
                    field.append('"')
                    i += 1
                else:
                    in_quotes = False
            else:
                field.append(ch)
        else:
            if ch == '"':
                in_quotes = True
            elif ch == ",":
                row.append("".join(field))
                field = []
            elif ch == "\n" or ch == "\r":
                if row or field:
                    row.append("".join(field))
                rows.append(row)
                field = []
                row = []
                if ch == "\r" and i + 1 < n and text[i + 1] == "\n":
                    i += 1
            else:
                field.append(ch)
        i += 1

    if row or field:
        row.append("".join(field))
        rows.append(row)

    return rows
