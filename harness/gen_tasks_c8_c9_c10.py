#!/usr/bin/env python3
"""Generate benchmark tasks: C08 Memory, C09 Multi-Agent, C10 End-to-End."""
import json, os, shutil
from gen_tasks_c5 import mk

# ============================ C08 MEMORY (two-turn) ============================

c08t01_verify = '''#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c08t01"
checks = []
cfg = None
for name in ("config.py", "conf.py", "settings.py"):
    c = vlib.find_file(ws, name)
    if c:
        cfg = c
        break
checks.append({"name": "config file exists", "ok": bool(cfg), "points": 5, "detail": str(cfg)})
if cfg:
    src = open(cfg).read()
    checks.append({"name": "CODENAME == PURPLE-TIGER", "ok": "PURPLE-TIGER" in src, "points": 5})
    checks.append({"name": "PORT == 8734", "ok": "8734" in src, "points": 5})
    checks.append({"name": "HTTP library == requests", "ok": "requests" in src.lower(), "points": 5})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
'''

c08t01_prompt = """Hi! Quick context before we start working together on this project:

- The project codename is PURPLE-TIGER
- The service will run on port 8734
- We have decided to use the 'requests' library for all HTTP calls (not urllib)

Just acknowledge this for now - do not create any files yet."""

c08t01_prompt2 = """Now, based on what we agreed earlier, create a file `config.py` in this
directory defining three constants:

    CODENAME = ...   # the project codename we agreed on
    PORT = ...       # the port number we agreed on
    HTTP_LIBRARY = ...   # the HTTP library name we agreed on

Use exactly the values from our earlier discussion."""

c08t02_verify = '''#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c08t02"
checks = []
mod = None
for name in ("usermgmt.py", "users.py", "user_management.py", "accounts.py"):
    c = vlib.find_file(ws, name)
    if c:
        mod = c
        break
if not mod:
    for p in vlib.py_files(ws):
        if "def create_user" in open(p).read():
            mod = p
            break
checks.append({"name": "user management module found", "ok": bool(mod), "points": 4, "detail": str(mod)})
if mod:
    base = os.path.dirname(mod)
    rc, out = vlib.write_and_run_pytest(base, \'\'\'
import sys, os, pytest
sys.path.insert(0, os.path.abspath("."))
import usermgmt as um

def test_email_lowercased():
    u = um.create_user("Bob", "Bob@Example.COM", "abcdefghijklmnop")
    assert u["email"] == "bob@example.com"

def test_username_unique_case_insensitive():
    um.create_user("A", "a@x.com", "abcdefghijklmnop")
    with pytest.raises(ValueError):
        um.create_user("a", "other@x.com", "abcdefghijklmnop")

def test_min_password_12():
    with pytest.raises(ValueError):
        um.create_user("B", "b@x.com", "short")

def test_username_normalized_lower():
    u = um.create_user("MixedCase", "m@x.com", "abcdefghijklmnop")
    assert u["username"] == "mixedcase"

def test_no_pii_in_repr():
    u = um.create_user("C", "c@x.com", "abcdefghijklmnop")
    assert "abcdefghijklmnop" not in repr(u)
\'\'\', test_name="t_memory_spec.py", extra_files={"usermgmt.py": open(mod).read()})
    checks.append({"name": "constraints from turn-1 spec enforced (5 hidden checks)", "ok": rc == 0,
                   "points": 16, "detail": out[-500:] if rc != 0 else "passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
'''

c08t02_prompt = """We are designing a user management module. Here is the FULL specification
we agreed on - remember it, we will implement it later (do NOT write code
yet, just acknowledge):

1. create_user(username, email, password) returns a user dict
2. emails are stored lowercased
3. usernames are unique, case-insensitively (second registration of the same
   name in any casing raises ValueError)
4. usernames are stored lowercased
5. minimum password length is 12 characters (shorter raises ValueError)
6. the returned dict has keys: username, email, password_hash, created_at
7. passwords are never returned in plain text - password_hash contains a
   salted sha256 hexdigest, and repr() of the user never shows the plain
   password
8. duplicate email registrations raise ValueError
9. all errors are ValueError (no bare exceptions)
10. the module is a single file usermgmt.py with no external dependencies"""

c08t02_prompt2 = """Now implement the user management module we specified earlier. Follow the
specification from our previous discussion exactly - all 10 points. Write
usermgmt.py and verify it yourself with a few quick checks."""

c08t03_verify = '''#!/usr/bin/env python3
import json, os, sys, ast
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c08t03"
checks = []
ph = vlib.find_file(ws, "phone.py")
checks.append({"name": "phone.py exists", "ok": bool(ph), "points": 3, "detail": str(ph)})
if ph:
    base = os.path.dirname(ph)
    rc, out = vlib.write_and_run_pytest(base, \'\'\'
import sys, os
sys.path.insert(0, os.path.abspath("."))
from phone import normalize_phone, format_intl

def test_normalize_digits():
    assert normalize_phone("+1 (555) 123-4567") == "15551234567"

def test_normalize_na():
    assert normalize_phone("abc") == ""

def test_format_intl_us():
    assert format_intl("+1 (555) 123-4567") == "+1 555 123 456 7"

def test_format_intl_other():
    assert format_intl("44 20 7123 0000") == "+44 207 123 000 0"
\'\'\')
    checks.append({"name": "both functions behave per spec", "ok": rc == 0, "points": 13,
                   "detail": out[-450:] if rc != 0 else "passed"})
    src = open(ph).read()
    tree = ast.parse(src)
    calls = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
            calls.add(n.func.id)
    reuse = "format_intl" in calls and "normalize_phone" in calls
    checks.append({"name": "format_intl REUSES normalize_phone (turn-1 function, not reimplemented)",
                   "ok": reuse, "points": 4})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
'''

c08t03_prompt = """Implement `phone.py` in this directory with ONE function:

    def normalize_phone(p: str) -> str
        # strips everything except digits; returns "" for no digits at all
        # examples: "+1 (555) 123-4567" -> "15551234567"; "abc" -> ""

Include 2-3 quick self-checks (in comments or a __main__ block). Do not
create other files."""

c08t03_prompt2 = """Extend phone.py with a SECOND function:

    def format_intl(p: str) -> str
        # normalizes the phone number using normalize_phone (reuse it!), then
        # formats as: +<country_code> <rest with spaces every 3 digits>
        # country code rule: the first 1 digit when the number starts with 1,
        # otherwise the first 2 digits; the remainder is grouped in chunks
        # of 3 (left to right), joined by single spaces:
        # "+1 (555) 123-4567" -> "+1 555 123 456 7"
        # "44 20 7123 0000"   -> "+44 207 123 000 0"
If the input has no digits, return "". Verify both functions still work."""

c08t04_verify = '''#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c08t04"
checks = []
mem = None
for name in ("MEMORY.md", "memory.md", "NOTES.md", "DECISIONS.md"):
    c = vlib.find_file(ws, name)
    if c:
        mem = c
        break
checks.append({"name": "memory/notes file exists", "ok": bool(mem), "points": 5, "detail": str(mem)})
if mem:
    txt = open(mem).read().lower()
    checks.append({"name": "memory records the JSON decision", "ok": "json" in txt and "csv" in txt,
                   "points": 4})
st = vlib.find_file(ws, "storage.py")
checks.append({"name": "storage.py exists", "ok": bool(st), "points": 4, "detail": str(st)})
if st:
    src = open(st).read()
    uses_json = "import json" in src or "json.dump" in src or "json.load" in src
    no_csv = ".csv" not in src and "csv.writer" not in src
    checks.append({"name": "implements JSON storage (per recorded decision)", "ok": uses_json, "points": 4})
    checks.append({"name": "does NOT implement CSV (decision respected)", "ok": no_csv, "points": 3})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
'''

c08t04_prompt = """We are building a tiny notes app in this directory. Working agreement:

1. Keep a decision log in a file called MEMORY.md: every time we make a
   decision, you record the date, the decision, and a one-line rationale.
2. Decision made RIGHT NOW: "Storage format: JSON (not CSV) - because our
   data is nested and JSON round-trips types losslessly."

For this first turn: just create MEMORY.md recording that decision and
acknowledge. Do not write any code yet."""

c08t04_prompt2 = """Now, consulting our decision log (MEMORY.md), implement `storage.py` in
this directory implementing the storage backend we chose (and explicitly
NOT the one we rejected):

    def save_notes(notes: list, path: str) -> None
    def load_notes(path: str) -> list
        # round-trip save/load; load of a missing file returns []

Add a line to MEMORY.md recording that storage.py was implemented per the
earlier decision. Verify save/load round-trips before finishing."""

c08t05_verify = '''#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c08t05"
checks = []
st = None
for name in ("db.py", "store.py", "storage.py", "database.py"):
    c = vlib.find_file(ws, name)
    if c:
        st = c
        break
checks.append({"name": "storage module exists", "ok": bool(st), "points": 4, "detail": str(st)})
if st:
    src = open(st).read().lower()
    checks.append({"name": "uses sqlite (per architecture decision)", "ok": "sqlite3" in src or "sqlite" in src,
                   "points": 6})
    checks.append({"name": "no postgres dependency (decision respected)",
                   "ok": "psycopg" not in src and "postgres" not in src, "points": 4})
    base = os.path.dirname(st)
    rc, out = vlib.write_and_run_pytest(base, \'\'\'
import sys, os
sys.path.insert(0, os.path.abspath("."))
import importlib
mod = None
for m in ("db", "store", "storage", "database"):
    try:
        mod = importlib.import_module(m); break
    except Exception: pass

def test_roundtrip(tmp_path):
    p = str(tmp_path / "t.db")
    mod.put("k1", {"v": 1})
    mod.put("k2", {"v": 2})
    assert mod.get("k1") == {"v": 1}
    assert mod.get("missing") is None
\'\'\')
    checks.append({"name": "put/get works (hidden test)", "ok": rc == 0, "points": 4,
                   "detail": out[-350:] if rc != 0 else "passed"})
out_txt = ""
for f in ("agent_output.txt", "answer.md", "ANSWER.md"):
    p = os.path.join(ws, f)
    if os.path.exists(p):
        out_txt = open(p).read().lower()
        break
answer = (out_txt + " " + (open(os.path.join(ws, "WHY.md")).read().lower() if os.path.exists(os.path.join(ws, "WHY.md")) else ""))
kw = [k in answer for k in ("local", "embedded", "no server", "serverless", "zero config", "file-based", "single file", "server that", "no separate", "lightweight")]
checks.append({"name": "SQLite rationale retained in answer (local/embedded/no-server reasons)",
               "ok": any(kw), "points": 2})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
'''

c08t05_prompt = """Architecture decision for our project (record this, we will build on it
in a later step):

We will use SQLite (stdlib sqlite3) as the storage engine - NOT Postgres,
NOT MongoDB. Rationale: the app must run fully local-first on a laptop with
zero external services; SQLite is embedded, file-based, and needs no server.

Please acknowledge this decision. Do not create any files yet."""

c08t05_prompt2 = """Two things now:

1. Implement `db.py` in this directory with the engine we decided on earlier:

       def put(key: str, value) -> None      # value is JSON-serializable
       def get(key: str, default=None)
   persisting to ./appdata.db. Verify put/get round-trips.

2. Then answer this question in your final reply (and write it to WHY.md):
   Why did we choose SQLite for this project? Give the reasons from our
   earlier discussion."""

# ============================ C09 MULTI-AGENT / PARALLEL ============================

c09t01_verify = '''#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c09t01"
checks = []
mods = {
    "textutils": vlib.find_file(ws, "textutils.py"),
    "validators": vlib.find_file(ws, "validators.py"),
    "formatters": vlib.find_file(ws, "formatters.py"),
    "main": vlib.find_file(ws, "main.py"),
}
checks.append({"name": "all 4 files exist", "ok": all(mods.values()), "points": 6, "detail": str(mods)})
if all(mods.values()):
    base = ws
    rc, out = vlib.write_and_run_pytest(base, \'\'\'
import sys, os
sys.path.insert(0, os.path.abspath("."))
from textutils import word_count
from validators import is_email
from formatters import as_table
from main import build_report

def test_units():
    assert word_count("a b c") == 3
    assert is_email("a@b.co") is True
    assert is_email("nope") is False
    assert "|" in as_table([["h1", "h2"], ["a", "b"]])

def test_integration():
    rep = build_report("Contact a@b.co or nope. Two lines here.")
    assert isinstance(rep, str) and "@" in rep
\'\'\')
    checks.append({"name": "unit + integration tests pass", "ok": rc == 0, "points": 14,
                   "detail": out[-500:] if rc != 0 else "passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
'''

c09t01_prompt = """Multi-part engineering task - decompose it (implement the three modules
independently, then integrate). This directory is the workspace.

Module 1 - `textutils.py`:
    def word_count(text: str) -> int        # whitespace-separated tokens

Module 2 - `validators.py`:
    def is_email(s: str) -> bool            # simple practical check: x@y.z

Module 3 - `formatters.py`:
    def as_table(rows: list[list[str]]) -> str
        # renders a Markdown-style table, first row = header

Integration - `main.py`:
    def build_report(text: str) -> str
        # uses ALL three modules: counts words (module 1), extracts candidate
        # emails from the text and validates them (module 2), and renders a
        # summary table [metric, value] including word count and found valid
        # emails (module 3). Returns the rendered table string.

Verify: each module standalone + the integration path before finishing."""

c09t02_verify = '''#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c09t02"
checks = []
contract = vlib.find_file(ws, "contract.py")
auth = vlib.find_file(ws, "auth.py") or os.path.join(ws, "auth", "__init__.py")
users = vlib.find_file(ws, "users.py") or os.path.join(ws, "users", "__init__.py")
checks.append({"name": "contract.py exists", "ok": bool(contract), "points": 3, "detail": str(contract)})
checks.append({"name": "auth + users components exist", "ok": bool(auth) and bool(users),
               "points": 3, "detail": f"auth={auth} users={users}"})
if contract and auth and users:
    rc, out = vlib.write_and_run_pytest(ws, \'\'\'
import sys, os
sys.path.insert(0, os.path.abspath("."))
from contract import Token, now_ts
from auth import issue_token, verify_token
from users import register, authenticate

def test_register_and_auth():
    register("alice", "wonderland9")
    assert authenticate("alice", "wonderland9") is True
    assert authenticate("alice", "wrong") is False

def test_token_flow():
    register("bob", "builder123")
    t = issue_token("bob")
    assert verify_token(t) == "bob"

def test_forged_token_rejected():
    assert verify_token("not-a-real-token") is None
\'\'\', test_name="t_services.py")
    checks.append({"name": "cross-service integration (auth<->users via contract)", "ok": rc == 0,
                   "points": 14, "detail": out[-500:] if rc != 0 else "passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
'''

c09t02_prompt = """Decomposed services task. Implement THREE independent components that
integrate through a shared contract:

1. `contract.py` (shared types):
       now_ts() -> int                         # int(time.time())
       class Token: value: str, user: str, expires: int
       # Token.to_dict()/from_dict() provided

2. `auth.py` (token service) - depends ONLY on contract.py:
       issue_token(user: str) -> Token         # expires in 3600s; value must be unguessable (secrets module)
       verify_token(token_or_str) -> str|None  # returns username when valid+unexpired, else None

3. `users.py` (user service) - depends ONLY on contract.py:
       register(username, password) -> None    # duplicate username raises ValueError; store salted sha256
       authenticate(username, password) -> bool

Integration requirement: auth.py must NOT import users.py and users.py must
NOT import auth.py (they integrate through the contract only).
Verify the full flow: register -> authenticate -> issue_token -> verify_token,
plus a forged-token rejection, before finishing."""

c09t03_verify = '''#!/usr/bin/env python3
import json, os, sys, re, ast
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c09t03"
checks = []
api = vlib.find_file(ws, "api.py")
docs = vlib.find_file(ws, "DOCS.md")
checks.append({"name": "api.py exists", "ok": bool(api), "points": 3, "detail": str(api)})
checks.append({"name": "DOCS.md exists", "ok": bool(docs), "points": 3, "detail": str(docs)})
if api and docs:
    tree = ast.parse(open(api).read())
    fns = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    need = {"create_task", "list_tasks", "complete_task", "delete_task"}
    checks.append({"name": "4 required functions implemented", "ok": need.issubset(fns), "points": 5})
    doc = open(docs).read()
    names_ok = all(n in doc for n in need)
    checks.append({"name": "docs mention all 4 functions", "ok": names_ok, "points": 3})
    # signature match: docs contain def lines matching code
    mismatch = []
    for n in need & set(fns):
        args = [a.arg for a in fns[n].args.args if a.arg != "self"]
        sig = ", ".join(args)
        if sig and f"({sig})" not in doc.replace("self, ", ""):
            mismatch.append(n + "(" + sig + ")")
    checks.append({"name": "documented signatures match code", "ok": not mismatch,
                   "points": 4, "detail": "mismatched: " + str(mismatch)})
    rc, out = vlib.write_and_run_pytest(ws, \'\'\'
import sys, os
sys.path.insert(0, os.path.abspath("."))
from api import create_task, list_tasks, complete_task, delete_task

def test_lifecycle():
    t = create_task("write docs")
    tid = t["id"]
    assert any(x["id"] == tid for x in list_tasks())
    assert complete_task(tid)["done"] is True
    delete_task(tid)
    assert all(x["id"] != tid for x in list_tasks())
\'\'\')
    checks.append({"name": "task lifecycle works", "ok": rc == 0, "points": 2,
                   "detail": out[-250:] if rc != 0 else "passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
'''

c09t03_prompt = """Parallel workstreams task: API implementation and documentation must be
produced so they stay consistent. Deliver:

1. `api.py` - an in-memory task API:
       create_task(title: str) -> dict          # returns {"id": int, "title": ..., "done": False}
       list_tasks() -> list[dict]
       complete_task(task_id: int) -> dict      # marks done=True, returns the task; unknown id raises ValueError
       delete_task(task_id: int) -> None        # unknown id raises ValueError
2. `DOCS.md` - documentation for every function with its EXACT signature
   (same parameter names and order as the code) and a one-line description
   plus one usage example per function.

Consistency will be mechanically verified: the signatures in DOCS.md must
match api.py exactly. Work on code and docs as separate workstreams, then
cross-check them before finishing."""

c09t04_verify = '''#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c09t04"
checks = []
runner = vlib.find_file(ws, "pipeline.py") or vlib.find_file(ws, "runner.py")
checks.append({"name": "runner exists (pipeline.py)", "ok": bool(runner), "points": 3, "detail": str(runner)})
if runner:
    base = os.path.dirname(runner)
    rc, out = vlib.write_and_run_pytest(base, \'\'\'
import sys, os
sys.path.insert(0, os.path.abspath("."))
from pipeline import Transform, run_pipeline

def test_upper():
    assert Transform("upper", lambda s: s.upper()).apply("abc") == "ABC"

def test_pipeline_order():
    t1 = Transform("strip", lambda s: s.strip())
    t2 = Transform("upper", lambda s: s.upper())
    out = run_pipeline("  hi  ", [t1, t2])
    assert out == "HI"

def test_skip_disabled():
    t = Transform("no", lambda s: s + "X", enabled=False)
    assert run_pipeline("a", [t]) == "a"

def test_error_isolation():
    def boom(s): raise RuntimeError("x")
    t_bad = Transform("bad", boom)
    t_ok = Transform("ok", lambda s: s + "!")
    out, errs = run_pipeline("a", [t_bad, t_ok], collect_errors=True)
    assert out == "a!" and len(errs) == 1
\'\'\')
    checks.append({"name": "transform + pipeline semantics (hidden tests)", "ok": rc == 0,
                   "points": 17, "detail": out[-500:] if rc != 0 else "passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
'''

c09t04_prompt = """Map-reduce style decomposition. Build a small transformation framework:

1. `pipeline.py`:
       class Transform:
           def __init__(self, name: str, fn, enabled: bool = True): ...
           def apply(self, value): ...          # returns fn(value)
       def run_pipeline(value, transforms: list, collect_errors: bool = False):
           # applies transforms in order; a transform raising an exception
           # is SKIPPED (value unchanged); when collect_errors=True the
           # function returns (result, errors) where errors lists the names
           # of failed transforms; otherwise just the result.

2. Four INDEPENDENT example transforms (each could be developed/verified on
   its own) in the same file or modules - `upper`, `strip`, `reverse`,
   `word_count_wrap` (returns the word count as str) - and a `__main__`
   block that runs them over the string "  hello benchmark  " and prints
   each intermediate result.

Verify each transform individually AND the pipeline (including one failing
transform being skipped with collect_errors) before finishing."""

c09t05_verify = '''#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c09t05"
checks = []
impl = None
for name in ("cart.py", "cart/cart.py"):
    p = os.path.join(ws, name)
    if os.path.exists(p):
        impl = p
        break
if not impl:
    for p in vlib.py_files(ws):
        if "class Cart" in open(p).read():
            impl = p
            break
checks.append({"name": "Cart implementation exists", "ok": bool(impl), "points": 5, "detail": str(impl)})
tests = [p for p in vlib.py_files(ws) if "test" in os.path.basename(p)]
checks.append({"name": "test suite exists (written FIRST per TDD)", "ok": bool(tests), "points": 5, "detail": str(tests)[:120]})
if impl and tests:
    n_tests = sum(open(p).read().count("def test_") for p in tests)
    checks.append({"name": ">= 6 test functions", "ok": n_tests >= 6, "points": 2, "detail": str(n_tests)})
    base = ws
    rc, out = vlib.write_and_run_pytest(base, open(tests[0]).read(), test_name="t_agent.py")
    checks.append({"name": "agent's own suite passes against own implementation", "ok": rc == 0,
                   "points": 3, "detail": out[-300:] if rc != 0 else "passed"})
    rc2, out2 = vlib.write_and_run_pytest(base, \'\'\'
import sys, os, pytest
sys.path.insert(0, os.path.abspath("."))
from cart import Cart

def test_add_increments():
    c = Cart(); c.add("a"); c.add("a")
    assert c.items() == {"a": 2}

def test_remove_removes_line():
    c = Cart(); c.add("a", 2); c.remove("a")
    assert c.items() == {}

def test_remove_missing_raises():
    c = Cart()
    with pytest.raises(ValueError):
        c.remove("ghost")

def test_total():
    c = Cart(); c.add("a", 2); c.add("b", 1)
    assert c.total({"a": 1.5, "b": 2.0}) == 5.0
\'\'\', test_name="t_ref.py")
    checks.append({"name": "implementation satisfies reference tests", "ok": rc2 == 0,
                   "points": 5, "detail": out2[-300:] if rc2 != 0 else "passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
'''

c09t05_prompt = """TDD-style parallel workstreams task. You are the coordinator for two
workstreams: TESTS and IMPLEMENTATION.

Workstream A (tests first): write `test_cart.py` - a complete pytest suite
for a shopping cart class you have NOT implemented yet. Cover: add (with
default qty 1 and explicit qty), items() snapshot, remove existing and
remove missing (ValueError), total(price_map) summing qty*unit_price for
known skus, unknown sku in total raises KeyError.

Workstream B: implement `cart.py` with class Cart satisfying that suite:
    Cart() / .add(sku, qty=1) / .remove(sku) / .items() -> dict /
    .total(price_map) -> float

Run the tests, iterate until green, then finish. Both workstreams must end
consistent with each other."""

# ============================ C10 END-TO-END ============================

c10t01_verify = '''#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c10t01"
checks = []
mod = None
for p in vlib.py_files(ws):
    if "def shorten" in open(p).read():
        mod = p
        break
checks.append({"name": "shortener module exists", "ok": bool(mod), "points": 4, "detail": str(mod)})
if mod:
    base = os.path.dirname(mod)
    m = os.path.splitext(os.path.basename(mod))[0]
    rc, out = vlib.write_and_run_pytest(base, f\'\'\'
import sys, os
sys.path.insert(0, os.path.abspath("."))
from {m} import shorten, resolve

def test_roundtrip():
    code = shorten("https://example.com/x")
    assert resolve(code) == "https://example.com/x"

def test_stable_short():
    a = shorten("https://example.com/x")
    b = shorten("https://example.com/x")
    assert a == b, "same url must map to same code"

def test_custom_alias():
    c = shorten("https://example.com/y", alias="mylink")
    assert c == "mylink" and resolve("mylink") == "https://example.com/y"

def test_alias_collision():
    shorten("https://a.com", alias="taken")
    try:
        shorten("https://b.com", alias="taken")
        raised = False
    except ValueError:
        raised = True
    assert raised

def test_resolve_unknown():
    assert resolve("nope123") is None
\'\'\')
    checks.append({"name": "shorten/resolve semantics (5 hidden tests)", "ok": rc == 0, "points": 16,
                   "detail": out[-500:] if rc != 0 else "passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
'''

c10t01_prompt = """End-to-end task: build a URL shortener library.

Product requirement: users can shorten long URLs and resolve them back.

Build in this directory:
1. `shortener.py` (or a small package) exposing:
       shorten(url: str, alias: str | None = None) -> str
           # returns the short code; deterministic for the same url
           # (hash-based, e.g. 6+ chars); custom alias honored; alias
           # collision raises ValueError
       resolve(code: str) -> str | None
           # returns the original url, or None when unknown
   Storage: in-memory dict + JSON file persistence (auto-load/save a
   data file next to the module) so codes survive process restarts.
2. `tests/test_shortener.py` - pytest suite covering: round-trip,
   determinism, custom alias, alias collision, unknown code.
3. README.md - usage example in under 20 lines.

Run the suite, make it pass, verify persistence by using the module from a
second python process. Deliver everything working."""

c10t02_verify = '''#!/usr/bin/env python3
import json, os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c10t02"
checks = []
cli = vlib.find_file(ws, "tasks_cli.py") or vlib.find_file(ws, "task_cli.py") or vlib.find_file(ws, "mdtask.py")
checks.append({"name": "CLI entry exists", "ok": bool(cli), "points": 4, "detail": str(cli)})
if cli:
    d = tempfile.mkdtemp()
    def run(args):
        return vlib.run_cmd([sys.executable, cli] + args, os.path.dirname(cli), timeout=60,
                            env_extra={"TASKS_DIR": d})
    rc, out = run(["add", "First task", "--priority", "high"])
    ok_add = rc == 0
    checks.append({"name": "add works (with flags)", "ok": ok_add, "points": 3, "detail": out[-150:]})
    rc, out = run(["list"])
    checks.append({"name": "list shows task + priority", "ok": rc == 0 and "First task" in out and "high" in out.lower(),
                   "points": 4, "detail": out[-200:]})
    rc, out = run(["done", "1"])
    rc, out = run(["list", "--all"])
    ok = rc == 0 and ("[x]" in out or "done" in out.lower())
    checks.append({"name": "done + list --all reflect state", "ok": ok, "points": 4, "detail": out[-200:]})
    mds = [f for f in os.listdir(d) if f.endswith(".md")]
    checks.append({"name": "markdown persistence (at least one .md in TASKS_DIR)", "ok": bool(mds),
                   "points": 4, "detail": str(mds)})
    rc, out = run(["add", "Second"])
    rc, out = run(["list"])
    checks.append({"name": "second add listed", "ok": "Second" in out, "points": 1})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
'''

c10t02_prompt = """End-to-end task: a markdown-backed task manager.

Product requirement: tasks live as human-editable markdown files.

Build:
1. `tasks_cli.py`: `python tasks_cli.py <command> [args]`
   - `add <title> [--priority low|med|high]` - creates one markdown file per
     task in the tasks directory (path from TASKS_DIR env var, default ./tasks):
     the file contains the title as heading, a status line (open/done), and
     the priority
   - `list [--all]` - prints open tasks (or all with --all) as a table with
     id, status, priority, title
   - `done <id>` - flips the status to done (updates the markdown file)
   - `rm <id>` - deletes the task file
2. IDs are stable small integers (1, 2, ...).
3. README.md with usage.
4. Self-test the full lifecycle before finishing. Verification runs the CLI
   as a black box against TASKS_DIR."""

c10t03_verify = '''#!/usr/bin/env python3
import json, os, sys, time, urllib.request, socket, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c10t03"
checks = []
srv = vlib.find_file(ws, "server.py") or vlib.find_file(ws, "app.py")
checks.append({"name": "server module exists", "ok": bool(srv), "points": 4, "detail": str(srv)})
if srv:
    port = 18973
    proc = subprocess.Popen([sys.executable, srv, "--port", str(port)], cwd=os.path.dirname(srv),
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ok = False
    try:
        time.sleep(2.0)
        def req(method, path, body=None):
            r = urllib.request.Request(f"http://127.0.0.1:{port}{path}", method=method,
                                       data=json.dumps(body).encode() if body else None,
                                       headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(r, timeout=5) as resp:
                    return resp.status, resp.read()
            except urllib.error.HTTPError as e:
                return e.code, e.read()
        s, b = req("GET", "/health")
        health_ok = s == 200
        s1, b1 = req("GET", "/items")
        s2, b2 = req("POST", "/items", {"name": "alpha"})
        created = json.loads(b2) if s2 in (200, 201) else {}
        iid = created.get("id")
        s3, b3 = req("GET", f"/items/{iid}") if iid else (0, b"")
        s4, b4 = req("GET", "/items/99999")
        checks.append({"name": "GET /health -> 200", "ok": health_ok, "points": 3})
        checks.append({"name": "GET /items -> 200 JSON list", "ok": s1 == 200 and isinstance(json.loads(b1), list),
                       "points": 3})
        checks.append({"name": "POST /items creates + returns id", "ok": s2 in (200, 201) and iid is not None,
                       "points": 4})
        checks.append({"name": "GET /items/{id} returns created item", "ok": s3 == 200 and iid is not None,
                       "points": 3})
        checks.append({"name": "unknown id -> 404", "ok": s4 == 404, "points": 3})
    except Exception as e:
        checks.append({"name": "server reachable", "ok": False, "points": 16, "detail": str(e)[:200]})
    finally:
        proc.terminate()
        proc.wait(timeout=10)
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
'''

c10t03_prompt = """End-to-end task: a JSON API server using ONLY the Python standard library
(http.server or socketserver - no frameworks).

Endpoints:
- GET  /health          -> 200 {"status": "ok"}
- GET  /items           -> 200 [item, ...]
- POST /items           -> 201 with the created item (accepts {"name": ...});
                           400 on invalid JSON
- GET  /items/{id}      -> 200 item | 404 when missing
- DELETE /items/{id}    -> 204 | 404

Build `server.py` runnable as `python server.py --port N`. Items persist to
a JSON file so restarts keep data. Handle malformed requests gracefully
(400/404/405, never a crash). Write tests or a self-check script that
exercises every endpoint (start server, hit it, assert) and RUN it. Include
a README.md. Deliver a verified working server."""

c10t04_verify = '''#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c10t04"
checks = []
gen = vlib.find_file(ws, "generate_report.py") or vlib.find_file(ws, "report_gen.py") or vlib.find_file(ws, "generate.py")
checks.append({"name": "report generator exists", "ok": bool(gen), "points": 4, "detail": str(gen)})
rep = None
for cand in ("report.txt", "out/report.txt", "output/report.txt"):
    p = os.path.join(ws, cand)
    if os.path.exists(p):
        rep = p
        break
checks.append({"name": "report.txt produced", "ok": bool(rep), "points": 4, "detail": str(rep)})
if rep:
    txt = open(rep).read()
    low = txt.lower()
    import re as _re
    m = _re.search(r"total revenue[^\d]*(\d+[.,]\d+)", txt, _re.I)
    ok_total = bool(m) and abs(float(m.group(1).replace(",", ".")) - 313.00) < 0.05
    checks.append({"name": "total revenue == 313.00 (+-0.05)", "ok": ok_total,
                   "points": 5, "detail": (m.group(1) if m else txt[:120])})
    checks.append({"name": "top product by revenue named (Gadget)", "ok": "gadget" in low, "points": 3})
    checks.append({"name": "region breakdown present (north/south/east/west)", "ok": all(r in low for r in ("north", "south", "east", "west")), "points": 3})
    checks.append({"name": "order count = 8", "ok": "8" in txt, "points": 1})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
'''

c10t04_baseline = {
    "data/orders.csv": """order_id,customer,product,qty,unit_price,region
5001,Acme,Gadget,3,25.00,north
5002,Globex,Widget,10,4.50,south
5003,Acme,Widget,2,4.50,east
5004,Initech,Gizmo,5,12.00,west
5005,Globex,Gadget,1,25.00,south
5006,Acme,Gizmo,4,12.00,north
5007,Initech,Widget,6,4.50,east
5008,Globex,Gizmo,2,12.00,west
""",
    "TASK.md": """Build a report generator and RUN it.

Input: data/orders.csv (columns: order_id,customer,product,qty,unit_price,region)

Deliverables:
1. `generate_report.py` producing `report.txt` containing:
   - total revenue across all orders (sum qty*unit_price, 2 decimals)
   - revenue by product, sorted descending (with amounts)
   - revenue by region (alphabetical)
   - number of unique orders
   - a clearly readable layout with headers
2. Run it and verify the numbers by hand:
   expected total revenue = 3*25 + 10*4.5 + 2*4.5 + 5*12 + 1*25 + 4*12 + 6*4.5 + 2*12
3. Do not modify data/orders.csv.""",
}

c10t05_verify = '''#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c10t05"
checks = []
core = None
for p in vlib.py_files(ws):
    if "register" in open(p).read() and ("class Calculator" in open(p).read() or "def calculate" in open(p).read()):
        core = p
        break
checks.append({"name": "calculator core with registry exists", "ok": bool(core), "points": 5, "detail": str(core)})
if core:
    base = os.path.dirname(core)
    m = os.path.splitext(os.path.basename(core))[0]
    rc, out = vlib.write_and_run_pytest(base, f\'\'\'
import sys, os
sys.path.insert(0, os.path.abspath("."))
from {m} import Calculator

def test_basic_ops():
    c = Calculator()
    c.register("add", lambda a, b: a + b)
    c.register("sub", lambda a, b: a - b)
    assert c.calculate("add", 2, 3) == 5
    assert c.calculate("sub", 5, 2) == 3

def test_unknown_op():
    c = Calculator()
    try:
        c.calculate("nope", 1, 2)
        raised = False
    except KeyError:
        raised = True
    assert raised
\'\'\')
    checks.append({"name": "registry + calculate semantics", "ok": rc == 0, "points": 8,
                   "detail": out[-350:] if rc != 0 else "passed"})
    plugins = [p for p in vlib.py_files(ws) if "plugin" in p.lower()]
    n_ops = sum(open(p).read().count("def register") for p in plugins)
    has_all = n_ops >= 4
    checks.append({"name": "4 operation plugins registered", "ok": has_all, "points": 4,
                   "detail": f"{n_ops} registrations in {len(plugins)} plugin files"})
    tests = [p for p in vlib.py_files(ws) if "test" in os.path.basename(p)]
    checks.append({"name": "tests exist and pass", "ok": bool(tests), "points": 3, "detail": str(tests)[:120]})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
'''

c10t05_prompt = """End-to-end task: a plugin-style calculator.

Architecture requirement: a minimal CORE + independent PLUGINS.

1. Core (`calculator.py`):
       class Calculator:
           def register(self, name: str, fn) -> None      # registers an operation
           def calculate(self, name: str, *args): ...     # applies it; unknown name raises KeyError
           def operations(self) -> list                   # names of registered ops
2. Plugins: `plugins/` directory with four modules (add, subtract, multiply,
   divide). Each plugin module exposes `register(calc)` that registers its
   operation on a Calculator instance. Divide must raise ZeroDivisionError
   on zero divisor (document that in its docstring).
3. `main.py` wires core + plugins, then demonstrates 2+2, 10-4, 3*3, 9/2.
4. `tests/test_calculator.py` - pytest suite for the core AND the plugins.
5. README.md - how to add a new plugin in 3 steps.

Run the suite until green; run main.py to confirm the wiring works."""


def main():
    mk("c08_memory", "c08t01_config_facts", "Retain project facts across turns", c08t01_prompt, c08t01_verify, prompt2=c08t01_prompt2)
    mk("c08_memory", "c08t02_long_spec", "Retain 10-point spec, implement later", c08t02_prompt, c08t02_verify, prompt2=c08t02_prompt2)
    mk("c08_memory", "c08t03_resume_reuse", "Extend earlier function, reuse it", c08t03_prompt, c08t03_verify, prompt2=c08t03_prompt2)
    mk("c08_memory", "c08t04_memory_file", "Decision log drives later work", c08t04_prompt, c08t04_verify, prompt2=c08t04_prompt2)
    mk("c08_memory", "c08t05_arch_decision", "Architecture decision retention + QA", c08t05_prompt, c08t05_verify, prompt2=c08t05_prompt2)

    mk("c09_multi_agent", "c09t01_three_modules", "3 modules + integration", c09t01_prompt, c09t01_verify)
    mk("c09_multi_agent", "c09t02_service_contract", "Two services + shared contract", c09t02_prompt, c09t02_verify)
    mk("c09_multi_agent", "c09t03_code_docs_match", "API + consistent docs", c09t03_prompt, c09t03_verify)
    mk("c09_multi_agent", "c09t04_transforms", "Transform framework + 4 plugins", c09t04_prompt, c09t04_verify)
    mk("c09_multi_agent", "c09t05_tdd", "TDD: tests first, then impl", c09t05_prompt, c09t05_verify)

    mk("c10_e2e", "c10t01_url_shortener", "URL shortener lib", c10t01_prompt, c10t01_verify)
    mk("c10_e2e", "c10t02_md_tasks", "Markdown task manager", c10t02_prompt, c10t02_verify)
    mk("c10_e2e", "c10t03_json_api", "Stdlib JSON API server", c10t03_prompt, c10t03_verify)
    mk("c10_e2e", "c10t04_report_gen", "Report generator from CSV", "Do the entire task described in TASK.md in this directory: build generate_report.py, RUN it to produce report.txt, verify the numbers by hand (expected total = 3*25 + 10*4.5 + 2*4.5 + 5*12 + 1*25 + 4*12 + 6*4.5 + 2*12), keep data/orders.csv untouched.", c10t04_verify, baseline=c10t04_baseline)
    mk("c10_e2e", "c10t05_plugin_calc", "Plugin calculator", c10t05_prompt, c10t05_verify)
    print("c08 + c09 + c10 tasks generated")


if __name__ == "__main__":
    main()
