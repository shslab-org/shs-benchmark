import re

from textutils import word_count
from validators import is_email
from formatters import as_table

_EMAIL_CANDIDATE_RE = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')

def build_report(text: str) -> str:
    wc = word_count(text)
    candidates = _EMAIL_CANDIDATE_RE.findall(text)
    valid_emails = [e for e in candidates if is_email(e)]
    rows = [
        ["metric", "value"],
        ["word_count", str(wc)],
        ["valid_emails", ", ".join(valid_emails) if valid_emails else "none"],
    ]
    return as_table(rows)
