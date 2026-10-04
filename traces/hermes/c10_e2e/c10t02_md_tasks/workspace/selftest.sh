#!/bin/bash
# Black-box self-test of tasks_cli.py against TASKS_DIR.
set -u
cd "$(dirname "$0")"
export TASKS_DIR="$(pwd)/selftest_tasks"

python3 - <<'PY'
import shutil
shutil.rmtree("selftest_tasks", ignore_errors=True)
PY

run() { python3 tasks_cli.py "$@"; }

echo "== add x3 =="
run add "Write quarterly report" --priority high
run add "Buy milk"
run add "Fix login bug" --priority high

echo "== file contents =="
for f in "$TASKS_DIR"/*.md; do echo "--- $f"; cat "$f"; done

echo "== list (open only) =="
run list

echo "== mark 2 done =="
run done 2
echo "== file 2 after done =="
cat "$TASKS_DIR/2.md"

echo "== list (open only, should exclude 2) =="
run list

echo "== list --all =="
run list --all

echo "== rm 1 =="
run rm 1
echo "== dir after rm =="
ls "$TASKS_DIR"

echo "== add again -> id must be 4 =="
run add "New task"

echo "== rm nonexistent (expect error, exit 1) =="
run rm 99 && echo "FAIL: rm 99 succeeded" || echo "ok: rm 99 failed as expected (exit=$?)"

echo "== done nonexistent (expect error) =="
run done 99 && echo "FAIL: done 99 succeeded" || echo "ok: done 99 failed as expected"

echo "== list --all =="
run list --all

echo "== hand-edit: flip 3 to done by editing the file, then list --all =="
sed -i 's/^Status: open/Status: done/' "$TASKS_DIR/3.md"
run list --all

echo "== hand-edit: missing Status line -> done adds it under the title =="
echo "# Orphan title" > "$TASKS_DIR/4.md"
run done 4
cat "$TASKS_DIR/4.md"

echo "== empty dir case =="
python3 - <<'PY'
import shutil, subprocess, os, tempfile
d = tempfile.mkdtemp()
env = dict(os.environ, TASKS_DIR=d)
out = subprocess.run(["python3", "tasks_cli.py", "list"], env=env, capture_output=True, text=True)
print("list with no tasks dir ->", repr(out.stdout.strip()), "rc=", out.returncode)
out = subprocess.run(["python3", "tasks_cli.py", "add", "First"], env=env, capture_output=True, text=True)
print("add into fresh dir ->", repr(out.stdout.strip()), "rc=", out.returncode)
out = subprocess.run(["python3", "tasks_cli.py", "list"], env=env, capture_output=True, text=True)
print("list after first add ->", repr(out.stdout.strip()), "rc=", out.returncode)
shutil.rmtree(d, ignore_errors=True)
PY

echo "== priority validation (expect argparse error) =="
run add "Bad" --priority urgent && echo "FAIL: bad priority accepted" || echo "ok: bad priority rejected"

echo "== all lifecycle steps completed =="
