#!/usr/bin/env python3
"""Static site generator.

Converts every .md file in docs/ to a flat .html file in site/,
plus an index.html landing page that links to all generated pages.
Keeps docs/ untouched.
"""

import html
import re
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "docs"
SITE_DIR = Path(__file__).parent / "site"


def md_to_html(md_text: str) -> str:
    """Minimal markdown converter: headings, paragraphs, bold."""
    lines = md_text.splitlines()
    out = []
    para = []

    def bold(text: str) -> str:
        return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)

    def flush_para():
        if para:
            joined = " ".join(para)
            out.append(f"<p>{bold(html.escape(joined, quote=False))}</p>")
            para.clear()

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush_para()
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            flush_para()
            level = len(m.group(1))
            out.append(
                f"<h{level}>{bold(html.escape(m.group(2), quote=False))}</h{level}>"
            )
        else:
            para.append(stripped)
    flush_para()
    return "\n".join(out)


def first_h1(md_text: str) -> str:
    for line in md_text.splitlines():
        m = re.match(r"^#\s+(.*)$", line.strip())
        if m:
            return m.group(1).strip()
    return "Untitled"


def render_page(title: str, body_html: str, nav_html: str) -> str:
    return f"""<html>
<head>
<meta charset="utf-8">
<title>{html.escape(title)}</title>
</head>
<body>
{nav_html}
<main>
{body_html}
</main>
</body>
</html>
"""


def build() -> None:
    SITE_DIR.mkdir(exist_ok=True)

    # First pass: read all pages, compute titles and body HTML.
    pages = {}  # stem -> (title, body_html)
    for md_path in sorted(DOCS_DIR.glob("*.md")):
        text = md_path.read_text(encoding="utf-8")
        title = first_h1(text)
        body = md_to_html(text)
        pages[md_path.stem] = (title, body)

    # Navigation bar linking to ALL pages (including the index landing page).
    nav_items = {"index": "Index"}
    for stem, (title, _) in sorted(pages.items()):
        nav_items[stem] = title
    nav_links = "".join(
        f'<a href="{stem}.html">{html.escape(title)}</a> '
        for stem, title in sorted(nav_items.items())
    )
    nav_html = f'<div class="nav">{nav_links}</div>'

    # Second pass: write each page with the shared nav bar.
    for stem, (title, body) in sorted(pages.items()):
        out_path = SITE_DIR / f"{stem}.html"
        out_path.write_text(render_page(title, body, nav_html), encoding="utf-8")
        print(f"built {out_path.name}  (title: {title})")

    # index.html landing page
    index_links = "\n".join(
        f'  <li><a href="{stem}.html">{html.escape(title)}</a></li>'
        for stem, (title, _) in sorted(pages.items())
    )
    index_body = f"""<h1>Index</h1>
<ul>
{index_links}
</ul>"""
    (SITE_DIR / "index.html").write_text(
        render_page("Index", index_body, nav_html), encoding="utf-8"
    )
    print(f"built index.html ({len(pages)} page links)")


if __name__ == "__main__":
    build()
