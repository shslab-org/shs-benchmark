"""String utilities — CONTAINS SEEDED BUGS for the QA benchmark."""
import re


def slugify(text):
    """Lowercase, non-alphanumerics -> single hyphen, strip ends."""
    s = re.sub(r"[^a-z0-9]+", "-", text.lower())      # BUG 1: no strip of leading/trailing '-'
    return s


def truncate(text, width, ellipsis="..."):
    """Truncate with ellipsis so total length never exceeds width."""
    if len(text) <= width:                             # BUG 2: off-by-one, should be <= width - len(ellipsis) branch
        return text
    return text[: width - len(ellipsis)] + ellipsis    # BUG 2b: when width <= len(ellipsis) -> negative slice


def camel_to_snake(name):
    """Convert CamelCase to snake_case."""
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return s1.lower()                                   # BUG 3: misses acronym boundary (HTTPServer -> h_t_t_p_server)


def count_vowels(text):
    return sum(1 for ch in text.lower() if ch in "aeiou")   # correct on purpose
