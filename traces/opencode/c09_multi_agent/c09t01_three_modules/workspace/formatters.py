def as_table(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    header = rows[0]
    widths = [len(cell) for cell in header]
    for row in rows[1:]:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(cell))
    lines = []
    def fmt_row(cells: list[str]) -> str:
        padded = [cells[i].ljust(widths[i]) if i < len(cells) else " " * widths[i] for i in range(len(widths))]
        return "| " + " | ".join(padded) + " |"
    lines.append(fmt_row(header))
    sep = "| " + " | ".join("-" * w for w in widths) + " |"
    lines.append(sep)
    for row in rows[1:]:
        lines.append(fmt_row(row))
    return "\n".join(lines)
