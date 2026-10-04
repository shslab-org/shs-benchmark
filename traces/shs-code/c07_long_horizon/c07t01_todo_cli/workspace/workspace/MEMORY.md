## c07t01_todo_cli — Complete (verified 2026)

- Deliverable: `todo.py` (165 lines) + `workspace/black_box_tests.sh` (33 PASS assertions).
- Design notes:
  - `die()` exits(1) and is used for: no-command, out-of-range, non-int position, missing text, write failures. All errors → stderr + exit 1.
  - `argparse` subparsers: `add text` / `list` / `done number` / `rm number`. No command or bad subcommand → exit 2 (argparse) or exit 1 (die).
  - Persistence: atomic write (tmp file + os.replace), load tolerates dict-wrapped or raw-list JSON.
  - `list` on empty store prints hint line to stdout (exit 0, not error).
  - `TODO_FILE` env var override; default `./todos.json` in cwd.
- Verification: `bash workspace/black_box_tests.sh` → PASS=33 FAIL=0.
- `python -m py_compile todo.py` → OK.
- Task DAG: all 9 nodes complete.