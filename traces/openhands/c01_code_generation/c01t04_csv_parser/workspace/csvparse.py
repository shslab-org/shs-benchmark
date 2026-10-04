def parse_csv(text: str) -> list[list[str]]:
    """Parse an RFC-4180-style CSV string into a list of records.

    Each record is a list of string fields. Handles:
    - comma-separated fields, one record per line
    - quoted fields containing commas, newlines, and escaped
      quotes (a doubled "" inside a quoted field becomes ")
    - empty fields and a trailing newline at the end of input
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
                # Possible escaped quote (doubled "").
                if i + 1 < n and text[i + 1] == '"':
                    field.append('"')
                    i += 2
                    continue
                in_quotes = False
                i += 1
                continue
            # Everything else inside quotes is literal,
            # including commas and newlines.
            field.append(ch)
            i += 1
            continue

        # Unquoted state.
        if ch == '"':
            in_quotes = True
            i += 1
            continue
        if ch == ',':
            row.append("".join(field))
            field = []
            i += 1
            continue
        if ch == '\r':
            # Handle \r\n or lone \r as end of record.
            if i + 1 < n and text[i + 1] == '\n':
                i += 2
            else:
                i += 1
            row.append("".join(field))
            rows.append(row)
            row = []
            field = []
            continue
        if ch == '\n':
            row.append("".join(field))
            rows.append(row)
            row = []
            field = []
            i += 1
            continue
        field.append(ch)
        i += 1

    # Finalize a pending record if the input does not end with a newline.
    # After a newline, both `row` and `field` are empty; if either still
    # holds content, there was a record on the final line.
    if field or row:
        row.append("".join(field))
        rows.append(row)

    return rows
