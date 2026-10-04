# Issue #47: DateRange.overlaps misses touching ranges

Booking ranges that share exactly one boundary day (checkout == next check-in)
report `overlaps() == False`. Our policy: sharing a single day means overlap.

Repro:
    from datetime import date
    from daterange import DateRange
    a = DateRange(date(2026,3,10), date(2026,3,20))
    b = DateRange(date(2026,3,20), date(2026,3,25))
    assert a.overlaps(b)  # currently fails

Your job (QA team): write a REGRESSION TEST ONLY, in
tests_agent/test_daterange_regression.py, that demonstrates the reported bug
(the test must fail against the current shipped code). The maintainers will
fix the bug later; your test must also pass against the future fixed version.
Do NOT modify daterange.py. Do not test unrelated behavior — this is a
targeted regression test for issue #47 (you may include 1-3 tightly related
boundary cases).