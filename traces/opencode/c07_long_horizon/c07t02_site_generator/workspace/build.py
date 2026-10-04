import re
from pathlib import Path

DOCS = Path("docs")
SITE = Path("site")


def md_to_html(text):
    lines = text.split("\n")
    out = []
    para = []

    def flush():
        if para:
            out.append("<p>" + " ".join(para) + "</p>")
            para.clear()

    for line in lines:
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            flush()
            level = len(m.group(1))
            out.append(f"<h{level}>{m.group(2)}</h{level}>")
        elif line.strip() == "":
            flush()
        else:
            para.append(line.strip())
    flush()

    html = "\n".join(out)
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
    return html


def build():
    SITE.mkdir(exist_ok=True)
    md_files = sorted(DOCS.glob("*.md"))
    pages = []
    for f in md_files:
        text = f.read_text()
        title_match = re.search(r"^#\s+(.+)", text, re.MULTILINE)
        title = title_match.group(1) if title_match else f.stem
        body = md_to_html(text)
        pages.append((f.stem + ".html", title))

    nav = "\n".join(
        f'  <a href="{href}">{t}</a>' for href, t in pages
    )

    for href, title in pages:
        src = DOCS / (href[:-5] + ".md")
        body = md_to_html(src.read_text())
        html = (
            "<!DOCTYPE html>\n"
            "<html>\n"
            "<head>\n"
            f'  <title>{title}</title>\n'
            "</head>\n"
            "<body>\n"
            "  <nav>\n"
            f"{nav}\n"
            "  </nav>\n"
            f"  {body}\n"
            "</body>\n"
            "</html>\n"
        )
        (SITE / href).write_text(html)

    links = "\n".join(
        f'  <li><a href="{href}">{t}</a></li>' for href, t in pages
    )
    index = (
        "<!DOCTYPE html>\n"
        "<html>\n"
        "<head>\n"
        "  <title>Home</title>\n"
        "</head>\n"
        "<body>\n"
        "  <h1>DemoKit</h1>\n"
        "  <ul>\n"
        f"{links}\n"
        "  </ul>\n"
        "</body>\n"
        "</html>\n"
    )
    (SITE / "index.html").write_text(index)
    print(f"Generated {len(pages) + 1} files in {SITE}/")


if __name__ == "__main__":
    build()
