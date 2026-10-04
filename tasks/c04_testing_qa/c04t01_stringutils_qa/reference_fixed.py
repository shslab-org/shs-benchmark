"""String utilities — reference fixed version."""
import re


def slugify(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower())
    return s.strip("-")


def truncate(text, width, ellipsis="..."):
    if width <= len(ellipsis):
        return ellipsis[:width]
    if len(text) <= width:
        return text
    return text[: width - len(ellipsis)] + ellipsis


def camel_to_snake(name):
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def count_vowels(text):
    return sum(1 for ch in text.lower() if ch in "aeiou")
