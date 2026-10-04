"""main: report builder integrating textutils, validators and formatters."""

import re

from textutils import word_count
from validators import is_email
from formatters import as_table

# Candidate email extraction: something like local@domain.tld, greedy enough
# to capture the full token, filtered afterwards by is_email().
_EMAIL_CANDIDATE_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+")


def _extract_valid_emails(text: str) -> list[str]:
    """Return the valid email addresses found in *text*, in order of
    appearance, duplicates removed."""
    seen = set()
    found = []
    for candidate in _EMAIL_CANDIDATE_RE.findall(text):
        # Strip a trailing punctuation that may have been captured (e.g. "."
        # at end of a sentence is not part of the address).
        candidate = candidate.rstrip(".")
        if candidate not in seen and is_email(candidate):
            seen.add(candidate)
            found.append(candidate)
    return found


def build_report(text: str) -> str:
    """Build a Markdown summary table for *text*.

    Uses all three modules:
      * ``textutils.word_count`` — counts whitespace-separated words.
      * ``validators.is_email`` — validates candidate email addresses
        extracted from the text.
      * ``formatters.as_table`` — renders the result as a two-column
        ``[metric, value]`` table.

    The table contains:
      * ``Word count`` — number of words in *text*
      * ``Valid emails found`` — count of distinct valid email addresses
      * one row per valid email address found (``Email 1``, ``Email 2``, ...)

    For example, ``build_report("Hi John at john@example.com please reply")``
    returns::

        | metric | value |
        | --- | --- |
        | Word count | 6 |
        | Valid emails found | 1 |
        | Email 1 | john@example.com |
    """
    wc = word_count(text)
    emails = _extract_valid_emails(text)

    rows: list[list[str]] = [["metric", "value"]]
    rows.append(["Word count", str(wc)])
    rows.append(["Valid emails found", str(len(emails))])
    for i, email in enumerate(emails, start=1):
        rows.append([f"Email {i}", email])

    return as_table(rows)


if __name__ == "__main__":
    sample = (
        "Contact jane.doe@acme.io or support@acme.io for help. "
        "Invalid ones: @no.local, a@b, bad @ x@y.z? "
        "Also reach out to ops@dev.corp.net."
    )
    print(build_report(sample))
