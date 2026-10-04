"""RFC-4180-style CSV parser implemented as a hand-rolled state machine.

Provides `parse_csv(text)`, which parses a CSV string (without using the
standard-library `csv` module) and returns it as a list of rows, where each
row is a list of string fields.

Supported features:
    - comma-separated fields, one record per line
    - quoted fields (surrounded by double quotes) that may contain commas,
      newlines, and escaped quotes (a doubled `""` inside a quoted field
      represents a single literal quote)
    - empty fields (e.g. ``a,,b`` -> ``["a", "", "b"]``)
    - a trailing newline at the end of the input does not produce a
      spurious empty final row
    - CRLF line endings: a `\r` immediately followed by `\n` is treated as a
      single line ending

The parser is a small explicit state machine with three states:

    IN_FIELD  - accumulating an unquoted field value
    IN_QUOTED - inside a quoted field value
    ESCAPE    - just saw a `"` while inside a quoted field; the next
                character decides whether it is an escaped quote, the end
                of the field (when followed by `,` or a line ending), or is
                leniently kept as part of the value

Non-quoted fields are terminated by a comma or a line ending. Quoted fields
may span multiple lines; embedded commas and newlines are kept as part of
the field value.
"""

__all__ = ["parse_csv"]


def parse_csv(text: str) -> list[list[str]]:
    """Parse an RFC-4180-style CSV string into a list of rows.

    Each row is a list of string fields. Quoted fields may contain commas,
    newlines, and escaped quotes (a doubled `""` is stored as a single
    `"`). Empty fields are preserved (e.g. ``a,,b`` -> ``["a", "", "b"]``).
    A trailing newline at the end of the input does not produce a spurious
    empty final row.

    Args:
        text: The CSV input as a single string.

    Returns:
        A list of rows; each row is a list of string fields. If the input
        is empty, an empty list is returned.

    Example:
        >>> parse_csv('a,"b,c",d')
        [['a', 'b,c', 'd']]
        >>> parse_csv('a,"x\\ny",c')
        [['a', 'x\\ny', 'c']]
        >>> parse_csv('a,,b')
        [['a', '', 'b']]
        >>> parse_csv('a,b,c\\n')
        [['a', 'b', 'c']]
    """
    # Three states of the hand-rolled state machine.
    IN_FIELD = 0   # building an unquoted field value
    IN_QUOTED = 1  # inside a quoted field value
    ESCAPE = 2     # just saw a `"` while in a quoted field

    rows: list[list[str]] = []
    row: list[str] = []
    field: list[str] = []
    state = IN_FIELD
    cr_pending = False  # a `\r` just ended a record; skip the following `\n`
    opened = False      # a quoted field has been opened (for the final flush)

    for ch in text:
        if state == IN_FIELD:
            if ch == '"':
                # Start of a quoted field.
                opened = True
                state = IN_QUOTED
            elif ch == ",":
                row.append("".join(field))
                field = []
            elif ch == "\r":
                # CRLF support: end the record now; a following `\n` is
                # skipped as the same line ending.
                row.append("".join(field))
                field = []
                rows.append(row)
                row = []
                cr_pending = True
                opened = False
            elif ch == "\n":
                if cr_pending:
                    cr_pending = False
                    continue  # the `\r` already ended this record
                row.append("".join(field))
                field = []
                rows.append(row)
                row = []
                opened = False
            else:
                field.append(ch)

        elif state == IN_QUOTED:
            if ch == '"':
                state = ESCAPE
            else:
                # Regular characters, embedded commas, and embedded
                # newlines are all part of the quoted value.
                field.append(ch)

        else:  # ESCAPE
            if ch == '"':
                # Doubled quote inside a quoted field -> literal quote.
                field.append('"')
                state = IN_QUOTED
            elif ch == ",":
                row.append("".join(field))
                field = []
                state = IN_FIELD
                cr_pending = False
            elif ch == "\r":
                row.append("".join(field))
                field = []
                rows.append(row)
                row = []
                state = IN_FIELD
                cr_pending = True
                opened = False
            elif ch == "\n":
                if cr_pending:
                    cr_pending = False
                    state = IN_FIELD
                    opened = False
                    continue  # the `\r` already ended this record
                row.append("".join(field))
                field = []
                rows.append(row)
                row = []
                state = IN_FIELD
                opened = False
            else:
                # Lenient handling of malformed input: keep the closing
                # quote and the unexpected character as part of the value.
                field.append('"')
                field.append(ch)
                state = IN_QUOTED

    # Flush a pending field/row when the input does not end with a line
    # ending (e.g. `"a,b"`), or when a quoted field was opened but never
    # terminated (e.g. `'"'` or `'""'` -> `[""]`). A completed trailing
    # newline leaves `field`, `row` and `opened` all empty, so nothing
    # spurious is emitted.
    if field or row or opened:
        row.append("".join(field))
        rows.append(row)

    return rows
