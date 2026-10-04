"""Module 3: output formatting helpers."""


def as_table(rows: list[list[str]]) -> str:
    """Render *rows* as a Markdown-style table.

    The first row is treated as the header. Cells are separated by
    " | " and a dashed separator row follows the header. Columns are
    aligned to the widest cell, but trailing spaces before the closing
    pipe are trimmed so lines end with exactly one space per "|".

    Returns the rendered table as a string (lines joined by newlines).
    """
    if not rows:
        return ""

    width = len(rows[0])
    col_widths = [0] * width
    for row in rows:
        for i, cell in enumerate(row):
            if i < width:
                col_widths[i] = max(col_widths[i], len(str(cell)))

    lines = []
    for i, row in enumerate(rows):
        cells = [str(cell) for cell in row]
        # pad every cell to its column width, then trim trailing spaces on
        # the last cell so each rendered line ends with exactly one space
        cells = [
            cells[j].rstrip() if j == width - 1 else cells[j].ljust(col_widths[j])
            for j in range(width)
        ]
        # the header separator dashes use the full column widths; the last
        # cell's dashes are trimmed so the line ends with exactly one space
        if i == 0:
            dashes = ["-" * col_widths[j] for j in range(width)]
            dashes[-1] = dashes[-1].rstrip()
            lines.append("| " + " | ".join(dashes) + " |")

    return "\n".join(lines)
