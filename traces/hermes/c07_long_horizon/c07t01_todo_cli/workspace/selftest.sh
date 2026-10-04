#!/bin/bash
# Black-box self-test for todo.py. Exits non-zero on first failure.
set -u
cd "$(dirname "$0")"
SCRIPT_DIR="$PWD"
export TODO_FILE="$PWD/test_todos.json"
rm -f "$TODO_FILE"

pass=0; fail=0

check() {  # check <desc> <expected> <actual>
  if [ "$2" = "$3" ]; then pass=$((pass+1)); else
    fail=$((fail+1)); echo "FAIL: $1"; echo "  expected: $2"; echo "  actual:   $3"; fi
}
check_exit() {  # check_exit <desc> <expected_exit> <actual_exit>
  if [ "$2" -eq "$3" ]; then pass=$((pass+1)); else
    fail=$((fail+1)); echo "FAIL: $1 (exit expected $2, got $3)"; fi
}

run() { out=$(python3 todo.py "$@" 2>/tmp/todo_err); rc=$?; echo "$out"; return $rc; }

# 1. empty list
out=$(python3 todo.py list 2>/dev/null); rc=$?
check_exit "list (empty) exit" 0 $rc
check "list (empty)" "No tasks yet." "$out"

# 2. add multiple items in separate invocations (persistence)
run add "Buy milk"; check_exit "add exit" 0 $?
run add "Walk the dog"; check_exit "add exit" 0 $?
run add "Write report"; check_exit "add exit" 0 $?

# 3. list shows pending checkboxes
out=$(python3 todo.py list 2>/dev/null)
expected=$'[ ] Buy milk\n[ ] Walk the dog\n[ ] Write report'
check "list pending" "$expected" "$out"

# 4. done marks item 2
out=$(python3 todo.py done 2 2>/dev/null); rc=$?
check_exit "done exit" 0 $rc
out=$(python3 todo.py list 2>/dev/null)
expected=$'[ ] Buy milk\n[x] Walk the dog\n[ ] Write report'
check "list after done" "$expected" "$out"

# 5. rm removes item 1
out=$(python3 todo.py rm 1 2>/dev/null); rc=$?
check_exit "rm exit" 0 $rc
out=$(python3 todo.py list 2>/dev/null)
expected=$'[x] Walk the dog\n[ ] Write report'
check "list after rm" "$expected" "$out"

# 6. done out of range
err=$(python3 todo.py done 99 2>&1 >/dev/null); rc=$?
check_exit "done bad number exit" 1 $rc
check "done bad number stderr non-empty" 1 "$([ -n "$err" ] && echo 1 || echo 0)"

# 7. rm out of range after items removed
err=$(python3 todo.py rm 5 2>&1 >/dev/null); rc=$?
check_exit "rm out of range exit" 1 $rc

# 8. missing argument to add
err=$(python3 todo.py add 2>&1 >/dev/null); rc=$?
check_exit "add missing arg exit" 2 $rc

# 9. no command at all
err=$(python3 todo.py 2>&1 >/dev/null); rc=$?
check_exit "no command exit" 1 $rc

# 10. unknown command
err=$(python3 todo.py fly 2>&1 >/dev/null); rc=$?
check_exit "unknown command exit" 2 $rc

# 11. done with non-integer
err=$(python3 todo.py done abc 2>&1 >/dev/null); rc=$?
check_exit "done non-integer exit" 2 $rc

# 12. --help works
out=$(python3 todo.py --help 2>&1); rc=$?
check_exit "--help exit" 0 $rc
check "--help mentions commands" 1 "$(echo "$out" | grep -q 'add.*list.*done.*rm\|add\|list' && echo 1 || echo 0)"

# 13. persistence: file contains JSON list
check "file is valid json" 1 "$(python3 -c "import json,sys;json.load(open('$TODO_FILE'))" && echo 1 || echo 0)"

# 14. default path (no TODO_FILE) — run in a temp dir
tmpd=$(mktemp -d)
( cd "$tmpd" && unset TODO_FILE && python3 "$SCRIPT_DIR/todo.py" add "default path test" >/dev/null )
check "default path creates ./todos.json" 1 "$([ -f "$tmpd/todos.json" ] && echo 1 || echo 0)"
rm -rf "$tmpd"

# 15. corrupted JSON file is rejected, not silently overwritten
corrupt=$(mktemp)
echo "{not json" > "$corrupt"
err=$(TODO_FILE="$corrupt" python3 todo.py list 2>&1 >/dev/null); rc=$?
check_exit "corrupt file exit" 1 $rc
check "corrupt file message" 1 "$(echo "$err" | grep -qi json && echo 1 || echo 0)"
rm -f "$corrupt"

echo "----"
echo "PASS: $pass  FAIL: $fail"
[ "$fail" -eq 0 ]
