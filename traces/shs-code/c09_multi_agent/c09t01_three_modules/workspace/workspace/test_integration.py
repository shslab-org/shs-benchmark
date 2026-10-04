"""Full verification battery: 3 standalone modules + integration, run as a
script file (avoids the intermittent inline-heredoc runner artifact)."""
import doctest, sys
sys.path.insert(0, '/home/z/my-project/bench_ws/shs-code/c09_multi_agent/c09t01_three_modules')

import textutils
r = doctest.testmod(textutils, verbose=False); assert r.failed == 0, r
from textutils import word_count
assert word_count("hello world") == 2
assert word_count("  one   two three  ") == 3
assert word_count("") == 0
assert word_count("   ") == 0
assert word_count("a\tb\nc") == 3
print("textutils.py: PASS")

import validators
r = doctest.testmod(validators, verbose=False); assert r.failed == 0, r
from validators import is_email
for e in ["user@example.com", "a@b.co", "x@y.z", "first.last@sub.domain.org",
          "user+tag@domain.io", "123@456.com"]:
    assert is_email(e), f"should be valid: {e!r}"
for e in ["no-at-sign.com", "a@b", "a b@c.com", "@missing-local.com",
          "a@@b.com", "a@.com", "a@b@c.com", "abc", "", "user@ex ample.com"]:
    assert not is_email(e), f"should be invalid: {e!r}"
assert not is_email(123) and not is_email(None)
print("validators.py: PASS")

import formatters
r = doctest.testmod(formatters, verbose=False); assert r.failed == 0, r
from formatters import as_table
assert as_table([["metric", "value"], ["words", "42"]]) == \
    "| metric | value |\n| --- | --- |\n| words | 42 |"
assert as_table([]) == ""
assert as_table([["h"], [42], [None]]) == "| h |\n| --- |\n| 42 |\n| None |"
out = as_table([["a", "b", "c"], ["1"], ["2", "3", "4", "5"]])
assert out.split("\n")[2] == "| 1 |  |  |", out
assert out.split("\n")[3] == "| 2 | 3 | 4 |", out
print("formatters.py: PASS")

import main
r = doctest.testmod(main, verbose=False); assert r.failed == 0, r
from main import build_report

out = build_report("Hi John at john@example.com please reply")
assert out == (
    "| metric | value |\n| --- | --- |\n| Word count | 6 |\n"
    "| Valid emails found | 1 |\n| Email 1 | john@example.com |"
), out

out = build_report("mail a@b.co a@b.co c@d.org now")
assert out == (
    "| metric | value |\n| --- | --- |\n| Word count | 5 |\n"
    "| Valid emails found | 2 |\n| Email 1 | a@b.co |\n| Email 2 | c@d.org |"
), out

out = build_report("nothing to see here, just words")
assert out == (
    "| metric | value |\n| --- | --- |\n| Word count | 7 |\n"
    "| Valid emails found | 0 |"
), out

out = build_report("try @x.com, a@b, x@y.z? and good@ok.com")
lines = out.split("\n")
assert lines[2] == "| Word count | 10 |", lines
assert lines[3] == "| Valid emails found | 2 |", lines
assert lines[4] == "| Email 1 | x@y.z |", lines
assert lines[5] == "| Email 2 | good@ok.com |", lines

out = build_report("see jane@x.com.")
assert out.split("\n")[4] == "| Email 1 | jane@x.com |", out

out = build_report("")
assert out == (
    "| metric | value |\n| --- | --- |\n| Word count | 0 |\n"
    "| Valid emails found | 0 |"
), out

print("INTEGRATION: ALL CHECKS PASSED")
print("--- demo ---")
print(build_report("Contact jane.doe@acme.io or support@acme.io for help. Also ops@dev.corp.net."))
