"""Diagnostic: replicate the exact failing battery context and instrument
_extract_valid_emails to see why 'john@example.com' is not found."""
import doctest, sys
sys.path.insert(0, '/home/z/my-project/bench_ws/shs-code/c09_multi_agent/c09t01_three_modules')

import textutils
r = doctest.testmod(textutils, verbose=False); assert r.failed == 0

import validators
r = doctest.testmod(validators, verbose=False); assert r.failed == 0
from validators import is_email
print("validators.is_email ok:", is_email("john@example.com"), "file:", validators.__file__)

import formatters
r = doctest.testmod(formatters, verbose=False); assert r.failed == 0

import main
r = doctest.testmod(main, verbose=False)
print("main doctest:", r, "failed:", r.failed)
print("main.is_email is validators.is_email:", main.is_email is validators.is_email)
print("main.is_email file:", getattr(main.is_email, "__module__", "?"))

from main import build_report, _extract_valid_emails

s = "Hi John at john@example.com please reply"
cands = main._EMAIL_CANDIDATE_RE.findall(s)
print("candidates:", cands)
for c in cands:
    c2 = c.rstrip(".")
    print("candidate:", repr(c2))
    print("  main.is_email:", main.is_email(c2))
    print("  validator.is_email:", validators.is_email(c2))
    print("  direct call result:", _extract_valid_emails(s))
out = build_report(s)
print("report:\n" + out)
print("email count in report:", out.count("Email "))
