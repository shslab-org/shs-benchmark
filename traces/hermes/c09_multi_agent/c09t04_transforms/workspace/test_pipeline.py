"""Verification: individual transforms + pipeline (incl. failing skipped)."""

import sys

from pipeline import Transform, run_pipeline, upper, strip, reverse, word_count_wrap

failures = []


def check(label, actual, expected):
    ok = actual == expected
    print(f"[{'ok' if ok else 'FAIL'}] {label}: {actual!r}" + ("" if ok else f" != expected {expected!r}"))
    if not ok:
        failures.append(label)


# --- individual transforms (each verified on its own) ---
check("upper('abc')", upper("abc"), "ABC")
check("strip('  x  ')", strip("  x  "), "x")
check("reverse('abc')", reverse("abc"), "cba")
check("word_count_wrap('a b c')", word_count_wrap("a b c"), "3")
check("word_count_wrap('  ')", word_count_wrap("  "), "0")
check("word_count_wrap('')", word_count_wrap(""), "0")

t = Transform("up", upper)
check("Transform.apply", t.apply("ok"), "OK")
check("Transform enabled defaults True", Transform("x", upper).enabled, True)
check("Transform enabled explicit False", Transform("x", upper, enabled=False).enabled, False)


def explode(v):
    raise RuntimeError("boom")


BAD = Transform("explode", explode)
GOOD1 = Transform("up", upper)
GOOD2 = Transform("rev", reverse)

# --- pipeline: failing transform is skipped, value passes through ---
res = run_pipeline("abc", [GOOD1, BAD, GOOD2])
check("pipeline skips failing transform", res, "CBA")

res2, errors = run_pipeline("abc", [GOOD1, BAD, GOOD2], collect_errors=True)
check("pipeline result with collect_errors", res2, "CBA")
check("error list = names of failed transforms", errors, ["explode"])

# disabled transform is skipped silently even if it would fail
NEVER = Transform("never", explode, enabled=False)
res3, e3 = run_pipeline("abc", [GOOD1, NEVER, GOOD2], collect_errors=True)
check("disabled failing transform leaves no error", e3, [])
check("value flows through disabled transform", res3, "CBA")

# failing transform alone with no collect_errors: value unchanged, no raise
check("failing transform alone (no collect_errors)", run_pipeline("abc", [BAD]), "abc")

# failing transform alone with collect_errors: value unchanged, named in errors
r4, e4 = run_pipeline("abc", [BAD], collect_errors=True)
check("failing transform alone (collect_errors) value", r4, "abc")
check("failing transform alone (collect_errors) errors", e4, ["explode"])

print()
print("ALL PASS" if not failures else f"FAILURES: {failures}")
sys.exit(1 if failures else 0)
