## Task: c08t03_resume_reuse — extend phone.py with format_intl (COMPLETE)
**Status:** DONE & VERIFIED (session: SHS Code)

### Deliverable
- `phone.py` in task dir `/home/z/my-project/bench_ws/shs-code/c08_memory/c08t03_resume_reuse/` now contains TWO functions:
  1. `normalize_phone(p: str) -> str` — UNCHANGED (strips non-digits; "" if none).
  2. `format_intl(p: str) -> str` — NEW. Reuses normalize_phone. Format: `+<cc> <chunks-of-3>`.
     CC rule: first 1 digit if number starts with "1", else first 2 digits. Remainder grouped L→R in chunks of 3, single spaces. No digits → "".

### Spec examples (verified passing)
- `format_intl("+1 (555) 123-4567") == "+1 555 123 456 7"`
- `format_intl("44 20 7123 0000") == "+44 207 123 000 0"`
- `format_intl("abc") == ""`, `format_intl("") == ""`

### Edge cases verified
- `"123"→"+1 23"`, `"44"→"+44"` (CC-only, no trailing space — handled by explicit `if not rest: return "+"+cc`), `"7 495 1234"→"+74 951 234"`, `"445"→"+44 5"`, `"12"→"+1 2"`.

### Verification method
- `python3 phone.py` → "all self-checks passed" (8 asserts in `__main__`, re-ran on final file state).
- Extended edge-case asserts via python_execute → "ALL EDGE-CASE CHECKS PASSED".
- No separate test files exist for phone.py (find returned none; "test_cart.py" in git log is an unrelated ancestor commit).
- Log persisted to `logs/verify_phone.txt`.

### Resume note for future sessions
If asked to "verify both functions still work" or to do more here — the implementation is already complete and passing; just re-run `python3 phone.py` to reconfirm. No pending work.
