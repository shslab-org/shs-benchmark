"""Black-box lifecycle test: runs tasks_cli.py as a subprocess against a
fresh temp TASKS_DIR and asserts observable behavior at every step."""
import os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(ROOT, "tasks_cli.py")

def run(env_dir, *args):
    env = dict(os.environ, TASKS_DIR=env_dir)
    r = subprocess.run([sys.executable, CLI, *args],
                       capture_output=True, text=True, env=env, cwd=ROOT)
    return r

def md(env_dir, tid):
    return os.path.join(env_dir, f"{tid:04d}.md")

tmp = tempfile.mkdtemp(prefix="tasks_test_")
try:
    failures = []
    def check(name, cond, extra=""):
        if cond:
            print(f"  PASS: {name}")
        else:
            print(f"  FAIL: {name} {extra}")
            failures.append(name)

    # --- 1. add three tasks, different priorities
    r = run(tmp, "add", "Buy groceries", "--priority", "high")
    check("add 1 exit 0", r.returncode == 0, r.stderr)
    check("add 1 announces id 1", "added task 1" in r.stdout, r.stdout)

    r = run(tmp, "add", "Ship release")
    check("add 2 exit 0 (default priority)", r.returncode == 0, r.stderr)
    check("add 2 announces id 2", "added task 2" in r.stdout, r.stdout)

    r = run(tmp, "add", "Water plants", "--priority", "low")
    check("add 3 announces id 3", "added task 3" in r.stdout, r.stdout)

    # --- 2. verify markdown file contents
    t1 = open(md(tmp, 1)).read()
    check("0001.md has heading", "# Buy groceries" in t1, repr(t1))
    check("0001.md status open", re.search(r"^- status: open$", t1, re.M) is not None, repr(t1))
    check("0001.md priority high", re.search(r"^- priority: high$", t1, re.M) is not None, repr(t1))
    t2 = open(md(tmp, 2)).read()
    check("0002.md default priority med", re.search(r"^- priority: med$", t2, re.M) is not None, repr(t2))
    check("0002.md status open", "- status: open" in t2, repr(t2))
    check("files named 0001-0003", all(os.path.isfile(md(tmp, i)) for i in (1, 2, 3)))

    # --- 3. list: open tasks only
    r = run(tmp, "list")
    check("list exit 0", r.returncode == 0, r.stderr)
    out = r.stdout
    check("list shows all 3 open", all(f" {i} " in out or f"{i}" in out for i in (1, 2, 3)), out)
    check("list has headers", all(h in out for h in ("id", "status", "priority", "title")), out)
    check("list has status values", "open" in out, out)

    # --- 4. done 2, verify file flipped
    r = run(tmp, "done", "2")
    check("done exit 0", r.returncode == 0, r.stderr)
    t2b = open(md(tmp, 2)).read()
    check("0002.md now done", re.search(r"^- status: done$", t2b, re.M) is not None, repr(t2b))
    check("0002.md title preserved", "# Ship release" in t2b, repr(t2b))
    check("0002.md priority preserved", "- priority: med" in t2b, repr(t2b))

    # --- 5. list default excludes done; --all includes it
    r = run(tmp, "list")
    check("list (open) hides done task 2", "Ship release" not in r.stdout, r.stdout)
    check("list (open) keeps tasks 1,3", "Buy groceries" in r.stdout and "Water plants" in r.stdout, r.stdout)
    r = run(tmp, "list", "--all")
    check("list --all shows done task", "Ship release" in r.stdout, r.stdout)
    check("list --all shows status done", "done" in r.stdout, r.stdout)

    # --- 6. rm task 1
    r = run(tmp, "rm", "1")
    check("rm exit 0", r.returncode == 0, r.stderr)
    check("0001.md deleted", not os.path.isfile(md(tmp, 1)))

    # --- 7. id stability: new task must get id 4, not reusing 1 or 2
    r = run(tmp, "add", "Refactor parser")
    check("new task after delete+done gets id 4 (stable, no reuse)",
          "added task 4" in r.stdout, r.stdout)
    check("0004.md exists", os.path.isfile(md(tmp, 4)))
    check("0001.md still absent", not os.path.isfile(md(tmp, 1)))

    # --- 8. list reflects current state
    r = run(tmp, "list")
    check("final list: task 4 open", "Refactor parser" in r.stdout, r.stdout)
    check("final list: no task 1 (deleted)", "Buy groceries" not in r.stdout, r.stdout)
    check("final list: no done task 2", "Ship release" not in r.stdout, r.stdout)
    r = run(tmp, "list", "--all")
    check("final list --all: task 2 done", "Ship release" in r.stdout and "done" in r.stdout, r.stdout)

    # --- 9. error handling: done/rm on nonexistent id exits nonzero
    r = run(tmp, "done", "99")
    check("done 99 fails", r.returncode != 0 and "not found" in r.stderr, r.stderr)
    r = run(tmp, "rm", "99")
    check("rm 99 fails", r.returncode != 0 and "not found" in r.stderr, r.stderr)

    # --- 10. empty-dir list
    empty = tempfile.mkdtemp(prefix="tasks_empty_")
    r = run(empty, "list")
    check("list on empty dir says 'no tasks'", "no tasks" in r.stdout, r.stdout)

    print()
    if failures:
        print(f"RESULT: {len(failures)} FAILURES: {failures}")
        sys.exit(1)
    print("RESULT: ALL CHECKS PASSED")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
