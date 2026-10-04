#!/usr/bin/env python3
"""Generate benchmark tasks: C06 Git Engineering + C07 Long-Horizon."""
import json, os, shutil
from gen_tasks_c5 import mk
from gen_tasks_c1_c2 import T

# ============================ C06 GIT ENGINEERING ============================

c06t01_baseline = {
    "app.py": 'def main():\n    print("app v1")\n',
    "utils.py": 'def helper():\n    return 42\n',
    "notes.txt": "random scratch notes, should NOT be committed\nlog.txt junk\ndebug_dump.json junk\n",
    "README.md": "# Demo app\n",
}

c06t01_verify = '''#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c06t01"
def git(*a):
    return vlib.run_cmd(["git"] + list(a), ws, timeout=30)
checks = []
rc, out = git("rev-parse", "--is-inside-work-tree")
checks.append({"name": "git repository initialized", "ok": rc == 0 and out.strip() == "true", "points": 4})
rc, out = git("log", "--oneline")
commits = [l for l in out.strip().split("\\n") if l.strip()] if rc == 0 else []
checks.append({"name": "at least 3 commits", "ok": len(commits) >= 3, "points": 5, "detail": str(len(commits)) + " commits"})
rc, out = git("ls-files")
tracked = out.strip().split("\\n") if rc == 0 else []
checks.append({"name": "app code tracked", "ok": "app.py" in tracked and "utils.py" in tracked,
               "points": 3, "detail": str(tracked[:6])})
checks.append({"name": "scratch notes NOT tracked", "ok": "notes.txt" not in tracked, "points": 3})
gi = os.path.join(ws, ".gitignore")
checks.append({"name": ".gitignore exists and covers notes", "ok": os.path.exists(gi) and "notes" in open(gi).read(),
               "points": 3})
rc, out = git("log", "--format=%s")
subjects = out.strip().split("\\n") if rc == 0 else []
descriptive = sum(1 for s in subjects if len(s.strip()) > 8)
checks.append({"name": "commit messages are descriptive", "ok": rc == 0 and descriptive >= 3,
               "points": 2, "detail": str(subjects[:5])})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
'''

c06t02_baseline = {
    "calc.py": '''"""Calculator with a bug in divide()."""


def add(a, b):
    return a + b


def divide(a, b):
    return a / b        # BUG: ZeroDivisionError instead of None
''',
    "test_calc.py": '''import pytest
from calc import add, divide


def test_add():
    assert add(2, 3) == 5


def test_divide_by_zero_should_return_none():
    assert divide(4, 0) is None


def test_divide_ok():
    assert divide(9, 3) == 3
''',
    "TASK.md": """Workflow task (do it with real git commands):

1. `git init`, commit everything on `main` as "Initial commit" - tests will
   FAIL, that is expected (bug present by design)
2. Create a branch named `fix/divide-by-zero`
3. On that branch: change divide() so that dividing by zero returns None
   (keep everything else), commit with message "Fix divide by zero"
4. Switch back to `main` and merge the branch into main
5. At the end: on `main`, `python -m pytest test_calc.py` must PASS, the
   branch `fix/divide-by-zero` must still exist, and the working tree clean.""",
}

c06t02_verify = '''#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c06t02"
def git(*a):
    return vlib.run_cmd(["git"] + list(a), ws, timeout=30)
checks = []
rc, out = git("rev-parse", "--is-inside-work-tree")
checks.append({"name": "git repo exists", "ok": rc == 0, "points": 3})
rc, out = git("branch", "--list", "fix/divide-by-zero")
checks.append({"name": "branch fix/divide-by-zero exists", "ok": rc == 0 and "fix/divide-by-zero" in out,
               "points": 4, "detail": out.strip()})
rc, out = git("log", "--oneline", "main")
mainlog = [l for l in out.strip().split("\\n") if l.strip()] if rc == 0 else []
checks.append({"name": "main has >= 2 commits (initial + fix via merge/ff)",
               "ok": len(mainlog) >= 2, "points": 3, "detail": str(len(mainlog))})
rc, out = git("log", "--oneline", "fix/divide-by-zero")
branchlog = [l for l in out.strip().split("\\n") if l.strip()] if rc == 0 else []
checks.append({"name": "fix branch has its own commit", "ok": len(branchlog) >= 2,
               "points": 3, "detail": str(len(branchlog))})
tdir = os.path.dirname(os.path.abspath(__file__))
rc, out = vlib.write_and_run_pytest(ws, open(os.path.join(tdir, "baseline", "test_calc.py")).read(), test_name="test_final.py")
checks.append({"name": "tests PASS on main after merge", "ok": rc == 0, "points": 6,
               "detail": out[-300:] if rc != 0 else "passed"})
rc, out = git("status", "--porcelain")
checks.append({"name": "clean working tree", "ok": rc == 0 and out.strip() == "", "points": 1, "detail": out.strip()[:100]})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
'''

c06t03_baseline = {
    "service.py": 'def ping():\n    return "pong"\n',
    "HISTORY.md": """The git history of this project (it was exported; you must RECREATE it):

1. commit "Add ping service"            (added service.py)         -> tag v0.1.0
2. commit "Add ping error handling"     (modified service.py)
3. commit "Add metrics endpoint"        (modified service.py)      -> tag v0.2.0
4. commit "Fix metrics counter race"    (modified service.py)
5. commit "Add healthcheck"             (modified service.py)      -> tag v0.3.0
6. commit "Update README"               (modified README.md)

TASK.md has the full instructions.""",
    "TASK.md": """Changelog task:

1. `git init`; recreate the 6-commit history EXACTLY as described in
   HISTORY.md (6 commits, in that order, with those exact messages; add a
   small realistic change to service.py / README.md for each; tag the 1st,
   3rd and 5th commit as v0.1.0, v0.2.0, v0.3.0)
2. Then write CHANGELOG.md in Keep-a-Changelog style with one section per
   version tag (## [0.3.0] first):
   Each section must mention the actual changes contained in the commits
   that belong to that version (derive them from git log), and must include
   the tag name. End with git status clean.""",
    "README.md": "# Service\n",
}

c06t03_verify = '''#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c06t03"
def git(*a):
    return vlib.run_cmd(["git"] + list(a), ws, timeout=30)
checks = []
rc, out = git("rev-parse", "--is-inside-work-tree")
checks.append({"name": "git repo exists", "ok": rc == 0, "points": 2})
rc, out = git("tag")
tags = set(out.strip().split("\\n")) if rc == 0 and out.strip() else set()
need = {"v0.1.0", "v0.2.0", "v0.3.0"}
checks.append({"name": "3 version tags exist", "ok": need.issubset(tags), "points": 4, "detail": str(sorted(tags))})
rc, out = git("log", "--oneline")
n = len([l for l in out.strip().split("\\n") if l.strip()]) if rc == 0 else 0
checks.append({"name": "6 history commits recreated (extra commits allowed)", "ok": n >= 6, "points": 4, "detail": str(n) + " commits"})
cl = os.path.join(ws, "CHANGELOG.md")
ok_cl = os.path.exists(cl)
checks.append({"name": "CHANGELOG.md exists", "ok": ok_cl, "points": 3})
if ok_cl:
    txt = open(cl).read()
    checks.append({"name": "sections for all three versions", "ok": all(v in txt for v in ("0.1.0", "0.2.0", "0.3.0")), "points": 3})
    low = txt.lower()
    checks.append({"name": "content derived from history (mentions ping/metrics/healthcheck)",
                   "ok": ("ping" in low and "metrics" in low and ("health" in low or "readme" in low)),
                   "points": 4})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
'''

c06t04_baseline = {
    "config.py": '''"""Shared config. greeting() will be changed on both branches."""


APP_NAME = "DemoApp"


def greeting():
    return f"Hello, valued user of {APP_NAME}"
''',
    "test_config.py": '''from config import greeting, APP_NAME


def test_app_name():
    assert APP_NAME == "DemoApp"


def test_greeting_is_string():
    assert isinstance(greeting(), str) and "DemoApp" in greeting()
''',
    "TASK.md": """Merge-conflict resolution task:

1. `git init`; commit all files as "Initial commit" on `main`
2. Create branch `feature/b-casual-greeting`; there, change greeting() to
   return f"Hey {APP_NAME} fan!" - commit "Casual greeting"
3. Back on `main`, change greeting() to return
   f"Hello, valued user of {APP_NAME} (v2)" - commit "Formal greeting v2"
4. Merge `feature/b-casual-greeting` into `main` - you WILL hit a conflict in
   greeting(); resolve it so the final greeting is the COMBINED style:
       return f"Hey there, valued user of {APP_NAME} (v2)!"
5. Commit the resolution ("Merge feature/b-casual-greeting"). At the end the
   suite must pass with this additional test present in test_config.py:

       def test_greeting_combined():
           assert greeting() == "Hey there, valued user of DemoApp (v2)!"

   (append that test to test_config.py). No conflict markers left anywhere,
   working tree clean, and `git log --merges` shows a merge commit.""",
}

c06t04_verify = '''#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c06t04"
def git(*a):
    return vlib.run_cmd(["git"] + list(a), ws, timeout=30)
checks = []
rc, out = git("rev-parse", "--is-inside-work-tree")
checks.append({"name": "git repo exists", "ok": rc == 0, "points": 2})
cfg = os.path.join(ws, "config.py")
src = open(cfg).read() if os.path.exists(cfg) else ""
markers = ("<<<<<<<", ">>>>>>>", "=======")
checks.append({"name": "no conflict markers left", "ok": not any(m in src for m in markers), "points": 4})
rc2, out2 = vlib.run_cmd([sys.executable, "-c",
    "import sys; sys.path.insert(0,'.'); from config import greeting; print(greeting())"], ws, timeout=30)
final_ok = rc2 == 0 and "Hey there, valued user of DemoApp (v2)!" in out2
checks.append({"name": "combined greeting produced", "ok": final_ok, "points": 6,
               "detail": out2.strip()[-120:]})
rc, out = git("log", "--oneline", "--merges")
has_merge = rc == 0 and out.strip() != ""
checks.append({"name": "merge commit exists on main", "ok": has_merge, "points": 4, "detail": out.strip()[:120]})
tc = os.path.join(ws, "test_config.py")
has_test = os.path.exists(tc) and "test_greeting_combined" in open(tc).read()
checks.append({"name": "combined-greeting test added", "ok": has_test, "points": 2})
rc3, out3 = vlib.run_cmd([sys.executable, "-m", "pytest", "-q", "test_config.py", "-p", "no:cacheprovider"], ws, timeout=60)
checks.append({"name": "test suite passes on final state", "ok": rc3 == 0, "points": 2,
               "detail": out3[-200:] if rc3 != 0 else "passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
'''

c06t05_baseline = {
    "TASK.md": """Rebase task (do it with real git):

1. `git init`; create `main.txt` containing the single line "one"; commit "Add one" on main
2. Create branch `feature`; on it, create `feature.txt` containing "feature work";
   commit "Add feature"
3. Back on main: append "two" on a new line of main.txt; commit "Add two"
4. Still on main: append "three" on a new line of main.txt; commit "Add three"
5. Switch to feature; REBASE feature onto main (no merge commits!)
6. On feature, append a new line "feature-continued" to feature.txt;
   commit "Continue feature"
7. Finally merge feature into main USING --ff-only (fast-forward only).

Final state on main:
- main.txt has one/two/three (three lines), feature.txt has "feature work" +
  "feature-continued"
- `git log --merges main` is EMPTY (linear history)
- `git log --oneline main` contains all 5 commits in order
- working tree clean""",
    "placeholder.txt": "remove me when you start\n",
}

c06t05_verify = '''#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c06t05"
def git(*a):
    return vlib.run_cmd(["git"] + list(a), ws, timeout=30)
checks = []
rc, out = git("rev-parse", "--is-inside-work-tree")
checks.append({"name": "git repo exists", "ok": rc == 0, "points": 2})
rc, out = git("log", "--oneline", "--merges", "main")
merges = out.strip() if rc == 0 else "?"
checks.append({"name": "linear history (no merge commits on main)", "ok": rc == 0 and merges == "",
               "points": 5, "detail": merges[:150]})
rc, out = git("log", "--format=%s", "main")
subjects = out if rc == 0 else ""
need_sub = ["Add one", "Add two", "Add three", "Add feature", "Continue feature"]
have_all = all(s in subjects for s in need_sub)
checks.append({"name": "all 5 commits present on main after ff-merge", "ok": have_all,
               "points": 4, "detail": subjects[:200]})
mt = os.path.join(ws, "main.txt"); ft = os.path.join(ws, "feature.txt")
main_ok = os.path.exists(mt) and all(w in open(mt).read() for w in ("one", "two", "three"))
feat_ok = os.path.exists(ft) and all(w in open(ft).read() for w in ("feature work", "feature-continued"))
checks.append({"name": "main.txt contains one/two/three", "ok": main_ok, "points": 2})
checks.append({"name": "feature.txt contains feature work + continuation", "ok": feat_ok, "points": 2})
rc, out = git("log", "--format=%s", "main")
order_ok = rc == 0 and out.strip().split("\\n")[-1].strip() == "Add one"
checks.append({"name": "root commit is 'Add one' (real history)", "ok": order_ok, "points": 2})
rc, out = git("status", "--porcelain")
checks.append({"name": "clean working tree", "ok": rc == 0 and out.strip() == "", "points": 3, "detail": out.strip()[:100]})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
'''

# ============================ C07 LONG-HORIZON ============================

c07t01_verify = '''#!/usr/bin/env python3
import json, os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c07t01"
checks = []
cli = vlib.find_file(ws, "todo.py")
checks.append({"name": "todo.py exists", "ok": bool(cli), "points": 4, "detail": str(cli)})
if cli:
    d = tempfile.mkdtemp()
    datafile = os.path.join(d, "todos.json")
    def run(args):
        return vlib.run_cmd([sys.executable, cli] + args, os.path.dirname(cli), timeout=60,
                            env_extra={"TODO_FILE": datafile})
    rc, out = run(["add", "Write benchmark report"])
    checks.append({"name": "add command works", "ok": rc == 0, "points": 3, "detail": out[-150:]})
    rc, out = run(["add", "Ship it"])
    rc, out = run(["list"])
    ok = rc == 0 and "Write benchmark report" in out and "Ship it" in out
    checks.append({"name": "list shows added items", "ok": ok, "points": 4, "detail": out[-200:]})
    rc, out = run(["done", "1"])
    rc, out = run(["list"])
    ok = rc == 0 and ("[x]" in out or "done" in out.lower())
    checks.append({"name": "done marks item (visible in list)", "ok": ok, "points": 4, "detail": out[-200:]})
    ok = os.path.exists(datafile)
    if ok:
        try:
            data = json.load(open(datafile))
            ok = isinstance(data, (list, dict)) and len(data) >= 2
        except Exception:
            ok = False
    checks.append({"name": "state persisted to JSON between runs", "ok": ok, "points": 5})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
'''

c07t01_prompt = """Build a complete, working command-line TODO application in this
directory. Long-horizon task - plan, implement, test, verify, deliver.

Requirements:
- File `todo.py`, runnable as `python todo.py <command> [args]`
- Commands: `add <text>`, `list`, `done <number>` (1-based position), `rm <number>`
- Items persist across runs in a JSON file whose path comes from the
  TODO_FILE environment variable (default: ./todos.json)
- `list` output shows one item per line with a checkbox: `[ ]` pending, `[x]` done
- Errors handled gracefully (bad numbers, missing args -> exit code != 0 with
  a clear message on stderr)
- Include a `--help`

Verification runs the CLI as a black box (add/list/done + persistence across
separate invocations). Self-test everything before finishing."""

c07t02_baseline = {
    "docs/getting-started.md": "# Getting Started\n\nWelcome to **DemoKit**.\n\n## Install\n\nRun the installer and follow the prompts.\n",
    "docs/architecture.md": "# Architecture\n\nDemoKit has three layers.\n\n## Core\n\nThe core handles parsing.\n\n## Plugins\n\nPlugins extend the core.\n",
    "docs/faq.md": "# FAQ\n\nWhy DemoKit? Because it is small and fast.\n\n## License\n\nMIT.\n",
    "TASK.md": """Build a tiny static site generator and run it:

1. Write `build.py`: converts every .md file in docs/ to an .html file in
   site/ (flat: same basename, .html)
2. Each page must have: <title> from the first # heading, the markdown
   converted to HTML (headings, paragraphs, bold), and a simple navigation
   bar on every page linking to ALL pages
3. index.html: a landing page in site/ linking to all generated pages
4. RUN the generator to actually produce site/ with 4 html files
5. Keep the original docs/ untouched. Verify your output by reading the
   generated files back.""",
}

c07t02_verify = '''#!/usr/bin/env python3
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
'''

c07t03_verify = '''#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c07t03"
checks = []
client = None
for name in ("httpclient.py", "client.py", "retryclient.py", "fetch.py"):
    c = vlib.find_file(ws, name)
    if c:
        client = c
        break
if not client:
    for p in vlib.py_files(ws):
        if "def fetch_with_retry" in open(p).read():
            client = p
            break
checks.append({"name": "httpclient.py with fetch_with_retry exists", "ok": bool(client), "points": 5, "detail": str(client)})
if client:
    tests = [p for p in vlib.py_files(ws) if "test" in os.path.basename(p)]
    checks.append({"name": "agent-authored tests exist", "ok": bool(tests), "points": 4, "detail": str(tests)[:150]})
    base = os.path.dirname(client)
    rc, out = vlib.write_and_run_pytest(base, \'\'\'
import sys, threading, http.server, socketserver, os
sys.path.insert(0, os.path.abspath("."))
from httpclient import fetch_with_retry

class H(http.server.BaseHTTPRequestHandler):
    hits = 0
    def do_GET(self):
        H.hits += 1
        if H.hits < 3:
            self.send_response(503)
        else:
            self.send_response(200)
        self.end_headers()
        self.wfile.write(b\\'{"ok": true}\\')
    def log_message(self, *a): pass

srv = socketserver.TCPServer(("127.0.0.1", 0), H)
port = srv.server_address[1]
t = threading.Thread(target=srv.serve_forever, daemon=True)
t.start()

def test_retries_then_succeeds():
    H.hits = 0
    data, status = fetch_with_retry("http://127.0.0.1:%d/" % port, retries=5, backoff=0.01)
    assert status == 200 and H.hits == 3

def test_respects_max_retries():
    H.hits = 0
    data, status = fetch_with_retry("http://127.0.0.1:%d/" % port, retries=1, backoff=0.01)
    assert status == 503 and H.hits == 2
\'\'\')
    checks.append({"name": "hidden behavior tests (retry-then-succeed + give-up)", "ok": rc == 0, "points": 9,
                   "detail": out[-400:] if rc != 0 else "passed"})
    if tests:
        env = dict(os.environ); env["PYTHONPATH"] = base
        rc2, out2 = vlib.run_cmd([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"] + tests, base, timeout=90, env_extra=env)
        checks.append({"name": "agent's own tests pass", "ok": rc2 == 0, "points": 2,
                       "detail": out2[-250:] if rc2 != 0 else "passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
'''

c07t03_prompt = """Build a retrying HTTP client library using ONLY the Python standard
library (urllib.request - no requests/httpx).

Deliverables in this directory:
1. `httpclient.py` exposing:
       fetch_with_retry(url, retries=3, backoff=0.5, timeout=5) -> (data, status)
   - retries on connection errors AND 5xx responses: up to `retries` extra
     attempts, sleeping `backoff` seconds after each failure, doubling the
     backoff each retry (exponential)
   - returns (body-as-text-or-parsed-json, final_http_status)
   - 4xx responses are NOT retried
2. `tests/` with pytest tests you write yourself: cover success,
   retry-then-success, give-up-after-retries, and 4xx-no-retry (mock or stub
   the HTTP layer; you may also spin up a local http.server in a thread)
3. A short README.md documenting the API
Run your tests until they pass. Plan, build, test, fix, verify."""

c07t04_baseline = {
    "README.md": "# Shop\n\nA small shop demo. This README is OUT OF DATE: it only covers the cart,\nnot pricing. Update it as part of your work.\n",
    "shop/__init__.py": "",
    "shop/cart.py": '''class Cart:
    """Shopping cart. BUG: remove() does nothing (tests fail)."""

    def __init__(self):
        self._items = {}

    def add(self, sku, qty=1):
        self._items[sku] = self._items.get(sku, 0) + qty

    def remove(self, sku):
        pass  # TODO broken

    def items(self):
        return dict(self._items)
''',
    "shop/pricing.py": '''def final_price(qty, unit_price, bulk_threshold, bulk_discount):
    """Total price with bulk discount. BUG: discount never applied."""
    return qty * unit_price
''',
    "tests/test_cart.py": '''from shop.cart import Cart


def test_cart_add_remove():
    c = Cart()
    c.add("apple", 2)
    c.add("pear", 1)
    c.remove("apple")
    assert c.items() == {"pear": 1}


def test_cart_quantity_update():
    c = Cart()
    c.add("apple", 2)
    c.add("apple", 3)
    assert c.items() == {"apple": 5}
''',
    "tests/test_pricing.py": '''from shop.pricing import final_price


def test_pricing_bulk():
    assert final_price(10, 1.0, bulk_threshold=10, bulk_discount=0.9) == 9.0


def test_pricing_normal():
    assert final_price(5, 2.0, bulk_threshold=10, bulk_discount=0.9) == 10.0
''',
    "TASK.md": """Long-horizon maintenance task on this repository (a git repo with 1
commit; git identity is already configured in this environment). ALL of the
following must be done, verified, and committed:

1. Run the test suite (python -m pytest -q). Two areas fail.
2. FIX the remove() bug in shop/cart.py.
3. FIX the bulk-discount bug in shop/pricing.py: when qty >= bulk_threshold,
   total = qty * unit_price * bulk_discount.
4. NEW FEATURE: add `shop/backup.py` with `backup_json(cart, path)` that
   writes the cart's items to path as JSON (indent=2). Add tests for it in
   tests/test_backup.py.
5. Update README.md to document cart, pricing (including the bulk rule) and
   the backup feature.
6. Commit your work in at least 2 git commits with descriptive messages.
   Final state: the full test suite passes and git status is clean.""",
}

c07t04_verify = '''#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c07t04"
checks = []
rc, out = vlib.write_and_run_pytest(ws, \'\'\'
import sys, os
sys.path.insert(0, os.path.abspath("."))
from shop.cart import Cart
from shop.pricing import final_price

def test_cart_add_remove():
    c = Cart()
    c.add("apple", 2)
    c.add("pear", 1)
    c.remove("apple")
    assert c.items() == {"pear": 1}

def test_cart_quantity_update():
    c = Cart()
    c.add("apple", 2)
    c.add("apple", 3)
    assert c.items() == {"apple": 5}

def test_pricing_bulk():
    assert final_price(10, 1.0, bulk_threshold=10, bulk_discount=0.9) == 9.0

def test_pricing_normal():
    assert final_price(5, 2.0, bulk_threshold=10, bulk_discount=0.9) == 10.0
\'\'\', test_name="t_final.py")
checks.append({"name": "all 4 hidden tests pass (2 bug fixes)", "ok": rc == 0, "points": 8,
               "detail": out[-500:] if rc != 0 else "passed"})
bk = vlib.find_file(ws, "backup.py")
ok_bk = bool(bk) and "def backup_json" in open(bk).read()
checks.append({"name": "backup feature exists (shop/backup.py with backup_json)", "ok": ok_bk, "points": 4})
bt = os.path.join(ws, "tests", "test_backup.py")
checks.append({"name": "tests for backup added", "ok": os.path.exists(bt) and "def test" in open(bt).read(), "points": 2})
rdme = open(os.path.join(ws, "README.md")).read().lower() if os.path.exists(os.path.join(ws, "README.md")) else ""
checks.append({"name": "README updated (cart + pricing/backup mentioned)",
               "ok": "cart" in rdme and ("pricing" in rdme or "backup" in rdme), "points": 2})
rc, out = vlib.run_cmd(["git", "-C", ws, "log", "--oneline"], ws, timeout=20)
n_commits = len([l for l in out.strip().split("\\n") if l.strip()]) if rc == 0 and out.strip() else 0
checks.append({"name": "work committed with git (>= 2 commits)", "ok": n_commits >= 2,
               "points": 4, "detail": str(n_commits) + " commits"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
'''

c07t05_baseline = {
    "TASK.md": """Build and RUN a data pipeline over the dirty CSV in data/sales_raw.csv.

Columns: order_id,region,product,qty,unit_price
Known problems in the data:
- some qty values are 0/negative or not integers  -> drop those rows
- some unit_price values are empty or not floats  -> drop those rows
- region values are inconsistent case (e.g. " west", "WEST", "East") -> normalize to Title-case ("West")
- duplicate order_id rows -> keep the first occurrence only

Deliverables:
1. pipeline.py: reads the CSV, applies ALL cleaning rules, computes:
   - total_sales (sum of qty*unit_price over cleaned rows, rounded to 2)
   - sales_by_region (same rounding, per region)
   - sales_by_product
   - row counts: input_rows, cleaned_rows, dropped_rows
2. Run it: write report.json (this exact name, repo root or out/)
3. Do NOT modify data/sales_raw.csv
4. Verify your numbers by hand on a few rows before finishing.""",
    "data/sales_raw.csv": """order_id,region,product,qty,unit_price
1001,West,Widget,2,9.99
1002,east,Gadget,1,24.50
1003,West,Widget,0,9.99
1004,NORTH,Gizmo,3,5.00
1005,East,Gadget,-2,24.50
1006,west ,Widget,4,9.99
1007,South,Gizmo,1,not_a_price
1008,South,Gizmo,2,5.00
1001,West,Widget,2,9.99
1009,north,Gizmo,1,5.00
1010,East,Widget,12,1.50
1011,,Gadget,1,10.00
1012,South,Widget,2,
""",
}

c07t05_verify = '''#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c07t05"
checks = []
pipe = vlib.find_file(ws, "pipeline.py") or vlib.find_file(ws, "run_pipeline.py")
checks.append({"name": "pipeline.py exists", "ok": bool(pipe), "points": 2, "detail": str(pipe)})
rep = None
for cand in ("report.json", "out/report.json", "output/report.json", "data/report.json"):
    p = os.path.join(ws, cand)
    if os.path.exists(p):
        rep = p
        break
checks.append({"name": "report.json produced", "ok": bool(rep), "points": 4, "detail": str(rep)})
if rep:
    try:
        r = json.load(open(rep))
        blob = json.dumps(r).lower()
        has_counts = ("input_rows" in blob or "cleaned_rows" in blob or "dropped_rows" in blob
                      or ("input" in blob and "cleaned" in blob))
        checks.append({"name": "row counts present (input/cleaned/dropped)", "ok": has_counts, "points": 4,
                       "detail": blob[:200]})
        checks.append({"name": "aggregates present (total + by_region + by_product)",
                       "ok": "total" in blob and "region" in blob and "product" in blob, "points": 5})
        # expected cleaned rows: 1001,1002,1004,1006,1008,1009,1010 = 7 rows (1011 has no region, 1012 no price)
        n_cleaned = r.get("cleaned_rows") or (r.get("row_counts") or {}).get("cleaned_rows")
        checks.append({"name": "cleaned_rows == 7 or 8 (exact computation)", "ok": n_cleaned in (7, 8),
                       "points": 2, "detail": "got: " + str(n_cleaned)})
        # total: 2*9.99 + 1*24.50 + 3*5.00 + 4*9.99 + 2*5.00 + 1*5.00 + 12*1.50 = 19.98+24.5+15+39.96+10+5+18 = 132.44
        total = r.get("total_sales")
        ok_total = isinstance(total, (int, float)) and min(abs(total - 132.44), abs(total - 142.44)) < 0.05
        checks.append({"name": "total_sales == 132.44 or 142.44 (+-0.05)", "ok": ok_total, "points": 2,
                       "detail": "got: " + str(total)})
    except Exception as e:
        checks.append({"name": "report parseable JSON", "ok": False, "points": 15, "detail": str(e)[:150]})
src_dirty = os.path.join(ws, "data", "sales_raw.csv")
ok_untouched = os.path.exists(src_dirty) and "not_a_price" in open(src_dirty).read()
checks.append({"name": "input data untouched", "ok": ok_untouched, "points": 1})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
'''

# expected numbers for c07t05 (recorded for audit):
# cleaned rows: 1001(West,2x9.99), 1002(East,1x24.50), 1004(North,3x5), 1006(West,4x9.99),
#               1008(South,2x5), 1009(North,1x5), 1010(East,12x1.5)  => 7 rows
# total = 19.98 + 24.50 + 15.00 + 39.96 + 10.00 + 5.00 + 18.00 = 132.44


def main():
    mk("c06_git_engineering", "c06t01_init_commits", "Init repo + logical commits",
       "In THIS directory (it is not yet a git repository), set up version control:\\n1. git init\\n2. Create a .gitignore that excludes notes.txt and any *.log / *.tmp files (notes.txt is scratch and must never be tracked)\\n3. Commit app.py, utils.py and README.md in LOGICAL commits - not one giant commit: at least 3 commits, each with a descriptive message (>8 chars, imperative style)\\n4. git status must be clean at the end (nothing untracked except ignored files)\\nDo not modify app.py, utils.py or README.md content. Do not track notes.txt.",
       c06t01_verify, baseline=c06t01_baseline)
    mk("c06_git_engineering", "c06t02_branch_fix_merge", "Branch, fix, merge",
       "Do the entire task described in TASK.md in this directory, using real git commands. Work step by step; verify every requirement yourself before finishing.",
       c06t02_verify, baseline=c06t02_baseline)
    mk("c06_git_engineering", "c06t03_changelog", "Recreate history + CHANGELOG",
       "Do the entire task described in TASK.md in this directory (details also in HISTORY.md), using real git commands. Work step by step; verify every requirement yourself before finishing.",
       c06t03_verify, baseline=c06t03_baseline)
    mk("c06_git_engineering", "c06t04_conflict", "Resolve merge conflict",
       "Do the entire task described in TASK.md in this directory, using real git commands. Work step by step; verify every requirement yourself before finishing.",
       c06t04_verify, baseline=c06t04_baseline)
    mk("c06_git_engineering", "c06t05_rebase", "Rebase + ff-merge linear",
       "Do the entire task described in TASK.md in this directory, using real git commands. Work step by step; verify every requirement yourself before finishing.",
       c06t05_verify, baseline=c06t05_baseline)
    mk("c07_long_horizon", "c07t01_todo_cli", "TODO CLI app", c07t01_prompt, c07t01_verify)
    mk("c07_long_horizon", "c07t02_site_generator", "Static site generator",
       "Build the static site generator described in TASK.md in this directory. Plan, implement, RUN the generator, and verify the produced HTML before finishing. Keep docs/ untouched.",
       c07t02_verify, baseline=c07t02_baseline)
    mk("c07_long_horizon", "c07t03_http_client", "Retrying HTTP client + tests", c07t03_prompt, c07t03_verify)
    mk("c07_long_horizon", "c07t04_repo_maintenance", "Repo maintenance batch",
       "Do the entire maintenance task described in TASK.md in this directory (fix bugs, add feature + tests, update README, make at least 2 descriptive git commits; full test suite must pass at the end).",
       c07t04_verify, baseline=c07t04_baseline)
    # c07t04 baseline is turned into a git repo AT STREAM TIME (git_baseline flag)
    _tp = os.path.join(T, "c07_long_horizon", "c07t04_repo_maintenance", "task.json")
    import json as _json
    _spec = _json.load(open(_tp))
    _spec["git_baseline"] = True
    _json.dump(_spec, open(_tp, "w"), indent=2)
    print("c07t04 git_baseline flag set")
    mk("c07_long_horizon", "c07t05_data_pipeline", "Dirty CSV pipeline",
       "Build and RUN the data pipeline described in TASK.md in this directory. Do not modify data/sales_raw.csv. Produce report.json and double-check the numbers before finishing.",
       c07t05_verify, baseline=c07t05_baseline)
    print("c06 + c07 tasks generated")


if __name__ == "__main__":
    main()
