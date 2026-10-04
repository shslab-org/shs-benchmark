"""RFC-4180-style CSV parser.

Provides a single function, :func:`parse_csv`, which turns a string of
comma-separated-values into a list of records (each a list of field
strings).  The parser is a hand-written character-level state machine;
it does NOT use the standard-library ``csv`` module.

Supported input forms
---------------------
- Fields separated by commas, one record per line.
- Line terminators may be LF (``\\n``), CR (``\\r``) or CRLF (``\\r\\n``).
- A field may be double-quoted; inside a quoted field:
  * commas and line breaks are taken literally,
  * a doubled double-quote (``""``) produces a single literal ``"``.
- Empty fields (e.g. ``a,,b``) yield empty strings.
- A single trailing newline at the end of the input does not produce a
  spurious empty final record.  Empty input yields no records at all.

Quotes that appear in the middle of an *unquoted* field (i.e. not at the
start of the field) are kept as literal characters, matching the
lenient behaviour of most real-world CSV tools.

Example
-------
    >>> parse_csv('a,"b,c",d\n')
    [['a', 'b,c', 'd']]
    >>> parse_csv('"a""b",c')
    [['a"b', 'c']]
"""

__all__ = ["parse_csv"]


def parse_csv(text: str) -> list[list[str]]:
    """Parse *text* as an RFC-4180-style CSV document.

    Parameters
    ----------
    text:
        The CSV content as a string.  May contain fields, records,
        quoted fields (with embedded commas/newlines and ``""`` escaped
        quotes), empty fields and a trailing line terminator.

    Returns
    -------
    list[list[str]]
        One inner list per record, each containing the fields of that
        record as plain strings (quotes stripped, ``""`` unescaped).
        An empty input returns ``[]``; a trailing newline after the
        final record does not add an empty record.
    """
    records: list[list[str]] = []
    record: list[str] = []
    field: list[str] = []
    in_quotes = False
    i = 0
    n = len(text)

    def close_field() -> None:
        record.append("".join(field))
        field.clear()

    def close_record() -> None:
        close_field()
        records.append(list(record))
        record.clear()

    while i < n:
        c = text[i]
        if in_quotes:
            if c == '"':
                if i + 1 < n and text[i + 1] == '"':
                    field.append('"')   # doubled quote -> literal quote
                    i += 2
                else:
                    in_quotes = False   # closing quote
                    i += 1
            else:
                field.append(c)         # literal: comma, newline, ...
                i += 1
        else:
            if c == '"' and not field:
                in_quotes = True        # quoted field starts here
                i += 1
            elif c == ",":
                close_field()
                i += 1
            elif c == "\n":
                close_record()
                i += 1
            elif c == "\r":
                close_record()
                i += 2 if i + 1 < n and text[i + 1] == "\n" else 1
            else:
                field.append(c)
                i += 1

    # Flush whatever is pending, unless the input ended with a line
    # terminator (in which case close_record() has already run) or was
    # empty to begin with.
    if field or record:
        close_record()

    return records
