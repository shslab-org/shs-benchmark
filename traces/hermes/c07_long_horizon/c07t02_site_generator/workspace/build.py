#!/usr/bin/env python3
"""Tiny static site generator: docs/*.md -> site/*.html (flat) + site/index.html.

Supports #/##/### headings, paragraphs, and **bold**. Every generated page
gets a navigation bar linking to ALL pages (including the index). The
original docs/ files are never modified.
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
SITE = ROOT / "site"


def md_to_html(md_text: str) -> tuple[str, str]:
    """Convert markdown to HTML.

    Returns (title_from_first_h1, html_body). The body includes the h1
    element when the source had one.
    """
    lines = md_text.splitlines()
    out: list[str] = []
    title = ""
    para: list[str] = []

    def flush_para() -> None:
        if para:
            text = " ".join(para)
            text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
            out.append(f"<p>{text}</p>")
            para.clear()

    for raw in lines:
        line = raw.strip()
        m = re.match(r"^(#{1,3})\s+(.*)$", line)
        if m:
            flush_para()
            level = len(m.group(1))
            heading = html.escape(m.group(2))
            if level == 1 and not title:
                title = heading
            out.append(f"<h{level}>{heading}</h{level}>")
        elif not line:
            flush_para()
        else:
            para.append(html.escape(line))
    flush_para()
    return title, "\n".join(out)


def render_page(title: str, body: str, links: list[tuple[str, str]]) -> str:
    """Render a full HTML page with a nav bar built from (label, href) pairs."""
    nav = " ".join(f'<a href="{href}">{html.escape(label)}</a>' for label, href in links)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{html.escape(title)}</title>
</head>
<body>
<nav class="site-nav">{nav}</nav>
<main>
{body}
</main>
</body>
</html>
"""


def main() -> None:
    SITE.mkdir(exist_ok=True)

    converted: dict[str, tuple[str, str]] = {}  # basename -> (title, body)
    for md_path in sorted(DOCS.glob("*.md")):
        title, body = md_to_html(md_path.read_text(encoding="utf-8"))
        if not title:
            title = md_path.stem
        if "<h1>" not in body:
            body = f"<h1>{html.escape(title)}</h1>\n{body}"
        converted[md_path.stem] = (title, body)

    # Nav links: Home + every generated doc page (in sorted order).
    all_links: list[tuple[str, str]] = [("Home", "index.html")]
    for stem, (title, _) in converted.items():
        all_links.append((title, f"{stem}.html"))

    for stem, (title, body) in converted.items():
        (SITE / f"{stem}.html").write_text(
            render_page(title, body, all_links), encoding="utf-8"
        )

    # index.html: landing page linking to all generated pages.
    items = "\n".join(f'<li><a href="{href}">{html.escape(label)}</a></li>'
                     for label, href in all_links[1:])
    index_body = f"<h1>Index</h1>\n<ul>\n{items}\n</ul>"
    (SITE / "index.html").write_text(
        render_page("Index", index_body, all_links), encoding="utf-8"
    )

    print(f"Generated {len(converted)} doc pages + index.html in {SITE}/")


if __name__ == "__main__":
    main()
