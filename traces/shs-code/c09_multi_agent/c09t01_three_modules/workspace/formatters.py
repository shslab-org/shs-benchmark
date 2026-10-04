"""formatters: Markdown-style table rendering."""


def as_table(rows: list[list[str]]) -> str:
    """Render *rows* as a Markdown-style table.

    The first row is the header row; a separator line of ``---`` cells
    follows it. Each cell is joined with ``|`` delimiters. For example,
    ``as_table([["metric", "value"], ["words", "42"]])`` produces a
    three-line string::

        | metric | value |
        | --- | --- |
        | words | 42 |

    Empty input (``[]``) returns the empty string. Ragged rows shorter
    than the header are padded with empty cells; longer rows are
    truncated to the header width.
    """
    if not rows:
        return ""
    header = rows[0]
    ncols = len(header)
    lines = []
    lines.append("| " + " | ".join(str(c) for c in header) + " |")
    lines.append("| " + " | ".join("---" for _ in range(ncols)) + " |")
    for row in rows[1:]:
        # Pad short rows, ignore extra cells beyond the header width.
        cells = [str(c) for c in row]
        cells += [""] * (ncols - len(cells))
        cells = cells[:ncols]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)
