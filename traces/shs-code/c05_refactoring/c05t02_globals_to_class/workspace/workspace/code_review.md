# Refactor Summary: sessions.py globals -> SessionStore

## Changes
- `sessions.py` now defines `SessionStore`, holding all state on the instance
  (`self._sessions`, `self._next_id`); constructor starts empty.
- Operations (identical behavior):
  - `create(user)` -> new sequential session id (starts at 1, per-instance)
  - `close(sid)` -> marks session inactive (no-op if unknown id)
  - `active_count()` -> number of active sessions
  - `reset_all()` -> clears state, resets id counter
- No module-level state; module functions do not use `global` (verified via grep).

## Verification
- `python -m pytest -x -q` -> 3 passed (in test_sessions.py):
  1. basic create/close/active_count flow
  2. two independent store instances don't share state
  3. close on unknown id is a no-op
- Grep confirms zero `global` keyword occurrences in sessions.py.

## Skill check
Input validation: close() tolerates unknown ids; edge cases: empty store ->
active_count() == 0; no N+1/loop concerns at this scale. No security issues.
