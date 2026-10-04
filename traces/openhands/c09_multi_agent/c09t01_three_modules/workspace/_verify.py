from textutils import word_count
from validators import is_email
from formatters import as_table

# Module 1
assert word_count("a b c") == 3
assert word_count("") == 0
assert word_count("multiple   spaces") == 2
assert word_count("one") == 1
assert word_count("a\tb\nc\nd") == 4
print("textutils OK")

# Module 2
assert is_email("x@y.z") is True
assert is_email("user.name@domain.co.uk") is True
assert is_email("a_b-c+d@sub.example.org") is True
assert is_email("") is False
assert is_email("no-at-sign.com") is False
assert is_email("a@@b.com") is False
assert is_email("@domain.com") is False
assert is_email("user@") is False
assert is_email("user@domain") is False
assert is_email("user@.com") is False
assert is_email("user@dom..ain.com") is False
assert is_email("a b@c.d") is False
assert is_email(123) is False
print("validators OK")

# Module 3
out = as_table([["metric", "value"], ["word_count", "5"]])
lines = out.split("\n")
assert lines[0] == "| metric | value |", repr(lines[0])
assert lines[1] == "| -------- | ---------- |", repr(lines[1])
assert lines[2] == "| word_count | 5 |", repr(lines[2])
out2 = as_table([["a", "bb", "ccc"], ["12", "3", "4"]])
assert out2.split("\n")[0] == "| a | bb | ccc |", repr(out2)
assert out2.split("\n")[1] == "| - | -- | --- |", repr(out2)
assert out2.split("\n")[2] == "| 12 | 3 | 4  |", repr(out2)
assert as_table([]) == ""
print("formatters OK")

# Integration
from main import build_report
text = "The quick brown fox. Email: jane.doe@corp.io and bob@site.com, not foo@bar or x@@y.z"
report = build_report(text)
print()
print(report)
assert "word_count" in report
assert "word_count | 12" in report, "word count value wrong"
assert "jane.doe@corp.io" in report
assert "bob@site.com" in report
assert "foo@bar" not in report
assert "x@@y.z" not in report
assert "valid_email_count" in report
assert "2" in report
assert "metric" in report and "value" in report
print()
print("INTEGRATION OK - ALL CHECKS PASSED")
