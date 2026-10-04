#!/usr/bin/env bash
# Black-box test suite for todo.py
# Usage: bash workspace/black_box_tests.sh
# Exits 0 if all checks pass, 1 otherwise.
set -u
cd "$(dirname "$0")/.."   # repo root (where todo.py lives)

PASS=0; FAIL=0
check() { # desc, expected_exit, actual_exit
  if [ "$2" = "$3" ]; then PASS=$((PASS+1)); echo "PASS: $1"; else FAIL=$((FAIL+1)); echo "FAIL: $1 (expected exit $2, got $3)"; fi
}
assert_out() { # desc, expected_substring, actual
  case "$3" in *"$2"*) PASS=$((PASS+1)); echo "PASS: $1";; *) FAIL=$((FAIL+1)); echo "FAIL: $1 — missing [$2] in output: $3";; esac
}

# --- isolated store via TODO_FILE ---
export TODO_FILE="$(mktemp -d)/store.json"

# 1. list on empty store
OUT=$(python todo.py list); RC=$?
check "list on empty store exit 0" 0 $RC
assert_out "empty-list hint message" "No items yet" "$OUT"

# 2. add three items across SEPARATE invocations (persistence)
python todo.py add "buy milk"      >/dev/null; check "add #1 exit 0" 0 $?
python todo.py add "write report"  >/dev/null; check "add #2 exit 0" 0 $?
python todo.py add "call mom"      >/dev/null; check "add #3 exit 0" 0 $?

# 3. list shows 3 pending items with [ ]
OUT=$(python todo.py list); check "list exit 0" 0 $?
assert_out "item1 [ ] pending" "[ ] buy milk" "$OUT"
assert_out "item3 [ ] pending" "[ ] call mom" "$OUT"
assert_out "positions numbered" "3. [ ] call mom" "$OUT"

# 4. done 2 (separate invocation) -> [x]
python todo.py done 2 >/dev/null; check "done 2 exit 0" 0 $?
OUT=$(python todo.py list)
assert_out "item2 now [x]" "2. [x] write report" "$OUT"
assert_out "item1 still pending" "1. [ ] buy milk" "$OUT"

# 5. rm 1 -> item removed, list renumbered
python todo.py rm 1 >/dev/null; check "rm 1 exit 0" 0 $?
OUT=$(python todo.py list); check "list after rm exit 0" 0 $?
assert_out "write report now #1" "1. [x] write report" "$OUT"
assert_out "call mom now #2" "2. [ ] call mom" "$OUT"
case "$OUT" in *"buy milk"*) echo "FAIL: removed item still present"; FAIL=$((FAIL+1));; *) echo "PASS: removed item gone"; PASS=$((PASS+1));; esac

# 6. errors -> non-zero exit + stderr message
OUT=$(python todo.py done 99 2>&1); RC=$?
[ $RC -ne 0 ]; check "done 99 (out of range) exit !=0" 0 $?
assert_out "done 99 stderr message" "does not exist" "$OUT"
python todo.py rm 0 2>&1 >/dev/null; RC=$?
[ $RC -ne 0 ]; check "rm 0 exit !=0" 0 $?
python todo.py done abc 2>&1 >/dev/null; RC=$?
[ $RC -ne 0 ]; check "done abc exit !=0" 0 $?
python todo.py done 2>&1 >/dev/null; RC=$?
[ $RC -ne 0 ]; check "done missing number exit !=0" 0 $?
python todo.py add 2>&1 >/dev/null; RC=$?
[ $RC -ne 0 ]; check "add missing text exit !=0" 0 $?
python todo.py 2>&1 >/dev/null; RC=$?
[ $RC -ne 0 ]; check "no command exit !=0" 0 $?
python todo.py bogus 2>&1 >/dev/null; RC=$?
[ $RC -ne 0 ]; check "unknown command exit !=0" 0 $?

# 7. --help exit 0 and mentions commands
OUT=$(python todo.py --help); check "--help exit 0" 0 $?
assert_out "--help mentions add" "add" "$OUT"
assert_out "--help mentions rm" "rm" "$OUT"

# 8. TODO_FILE env var honored (separate store is isolated)
export TODO_FILE="$(mktemp -d)/other.json"
OUT=$(python todo.py list)
assert_out "separate TODO_FILE empty" "No items yet" "$OUT"
python todo.py add "only in other store" >/dev/null
OUT=$(python todo.py list)
assert_out "other store has its item" "only in other store" "$OUT"

# 9. default path (./todos.json) when TODO_FILE unset
unset TODO_FILE
rm -f ./todos.json
python todo.py add "default path item" >/dev/null; check "default-path add exit 0" 0 $?
[ -f ./todos.json ]; check "todos.json created in cwd" 0 $?
OUT=$(python todo.py list)
assert_out "default-path persistence" "default path item" "$OUT"
rm -f ./todos.json

echo "=================================="
echo "RESULTS: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ]
