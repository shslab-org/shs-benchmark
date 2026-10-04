"""Integration: build a summary report from free text.

Combines all three modules:
- textutils.word_count   (Module 1)
- validators.is_email    (Module 2)
- formatters.as_table    (Module 3)
"""

import re

from textutils import word_count
from validators import is_email
from formatters import as_table

# Candidate tokens that contain "@" are the email candidates.
_EMAIL_CANDIDATE_RE = re.compile(r"\S+@\S+")


def build_report(text: str) -> str:
    """Return a Markdown summary table for *text*.

    The table has columns [metric, value] and includes:
    - the total word count (via Module 1),
    - each unique email address found in the text, kept only if it
      passes Module 2's validation,
    - a row for the total number of valid emails found.
    """
    count = word_count(text)

    candidates = _EMAIL_CANDIDATE_RE.findall(text)
    valid_emails: list[str] = []
    for cand in candidates:
        cand = cand.strip(".,;!?()[]{}\"'")
        if cand and is_email(cand) and cand not in valid_emails:
            valid_emails.append(cand)

    rows: list[list[str]] = [["metric", "value"]]
    rows.append(["word_count", str(count)])
    for email in valid_emails:
        rows.append([email, "valid_email"])
    rows.append(["valid_email_count", str(len(valid_emails))])

    return as_table(rows)


if __name__ == "__main__":
    sample = (
        "Hello world, this is a test. "
        "Contact us at sales@example.com or support@my-site.org. "
        "Not an email: @@@ or noatsign.com. "
        "Also a bad one: a@b. See https://x.co/page?a@b.c for details."
    )
    print(build_report(sample))
