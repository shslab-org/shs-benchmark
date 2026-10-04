#!/usr/bin/env python3
"""Tiny static site generator.

Converts every .md file in docs/ to a flat .html file in site/
(same basename, .html). Each page gets a <title> from the first
`#` heading, markdown converted to HTML (headings, paragraphs,
**bold**), and a navigation bar linking to ALL pages. An
index.html landing page links to every generated page.
"""

import html
import re
from pathlib import Path

ROOT = Path(__file__).parent
DOCS = ROOT / "docs"
SITE = ROOT / "site"


def md_to_html(text):
    """Convert markdown (headings, paragraphs, **bold**) to HTML."""
    out = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            level = len(m.group(1))
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
        else:
            out.append(f"<p>{inline(line)}</p>")
    return "\n".join(out)


def inline(text):
    """Escape HTML, then turn **bold** into <strong>."""
    escaped = html.escape(text)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)


def first_heading(text, fallback):
    m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else fallback


def page(title, nav_items, body):
    nav = "\n".join(
        '<li><a href="{}">{}</a></li>'.format(href, html.escape(label))
        for href, label in nav_items
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{html.escape(title)}</title>
</head>
<body>
<nav>
<ul>
{nav}
</ul>
</nav>
{body}
</body>
</html>
"""


def main():
    SITE.mkdir(exist_ok=True)

    pages = []  # (href, title, body)
    for md in sorted(DOCS.glob("*.md")):
        text = md.read_text()
        title = first_heading(text, md.stem)
        pages.append((f"{md.stem}.html", title, md_to_html(text)))

    nav_items = [(href, title) for href, title, _ in pages]

    for href, title, body in pages:
        (SITE / href).write_text(page(title, nav_items, body))
        print(f"wrote {href}")

    links = "\n".join('<li><a href="{}">{}</a></li>'.format(href, html.escape(title))
                      for href, title in nav_items)
    index_body = f"<h1>Index</h1>\n<p>Documentation pages:</p>\n<ul>\n{links}\n</ul>\n"
    (SITE / "index.html").write_text(page("Index", nav_items, index_body))
    print("wrote index.html")


if __name__ == "__main__":
    main()
