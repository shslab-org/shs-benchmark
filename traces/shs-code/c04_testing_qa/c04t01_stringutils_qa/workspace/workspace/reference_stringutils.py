"""Correct reference implementation of the stringutils SPEC.

Used ONLY to verify that tests_agent/test_stringutils.py passes against a
spec-compliant module. This file lives in workspace/ and is NOT the shipped
module — the shipped stringutils.py must remain untouched.
"""
import re


def slugify(text: str) -> str:
    lowered = text.lower()
    # Replace every run of non-alphanumeric characters with a single hyphen.
    collapsed = re.sub(r"[^a-z0-9]+", "-", lowered)
    # Remove leading/trailing hyphens.
    return collapsed.strip("-")


def truncate(text: str, width: int, ellipsis: str = "...") -> str:
    if len(text) <= width:
        return text
    if width < len(ellipsis):
        # Return a prefix of the ellipsis cut to width.
        return ellipsis[:width]
    # Result is exactly width chars: text truncated to (width - len(ellipsis))
    # plus the ellipsis.
    return text[: width - len(ellipsis)] + ellipsis


def camel_to_snake(name: str) -> str:
    if not name:
        return name
    # Split at boundaries: a run of uppercase followed by a lowercase
    # (acronym-then-word), or lower->upper transitions.
    # 1) Insert a separator before a capital letter that is followed by a
    #    lowercase one, when preceded by a lowercase or a digit.
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    # 2) Split an acronym run from the following word: "HTTPServer" ->
    #    "HTTP_Server", which step 1 already handled only if preceded by
    #    lowercase. Handle acronym->word boundary: uppercase run followed
    #    by uppercase+lowercase.
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", s)
    return s.lower()


def count_vowels(text: str) -> int:
    vowels = set("aeiou")
    return sum(1 for ch in text.lower() if ch in vowels)
