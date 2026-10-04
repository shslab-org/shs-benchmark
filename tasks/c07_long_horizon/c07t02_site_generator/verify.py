#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c07t02"
checks = []
gen = vlib.find_file(ws, "build.py") or vlib.find_file(ws, "generate.py") or vlib.find_file(ws, "ssg.py")
checks.append({"name": "generator script exists (build.py)", "ok": bool(gen), "points": 4, "detail": str(gen)})
html_dir = None
for cand in ("site", "out", "output", "html", "public", "dist", "."):
    p = os.path.join(ws, cand)
    if os.path.isdir(p) and any(f.endswith(".html") for f in os.listdir(p)):
        html_dir = p
        break
checks.append({"name": "HTML output produced", "ok": bool(html_dir), "points": 4, "detail": str(html_dir)})
if html_dir:
    pages = {name: open(os.path.join(html_dir, name)).read() for name in os.listdir(html_dir) if name.endswith(".html")}
    checks.append({"name": "4 HTML pages (3 docs + index)", "ok": len(pages) >= 4, "points": 3, "detail": str(list(pages)[:6])})
    allh = " ".join(pages.values()).lower()
    checks.append({"name": "pages contain converted content (headings/paragraphs)",
                   "ok": ("<h1>" in allh or "<h2>" in allh) and ("<p>" in allh or "<li>" in allh), "points": 3})
    checks.append({"name": "index.html with navigation links", "ok": "index.html" in pages and "href" in pages.get("index.html", "").lower(), "points": 3})
    checks.append({"name": "titles rendered", "ok": "<title>" in allh, "points": 2})
    checks.append({"name": "markdown sources intact", "ok": os.path.isdir(os.path.join(ws, "docs")) and len(os.listdir(os.path.join(ws, "docs"))) >= 3, "points": 1})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
