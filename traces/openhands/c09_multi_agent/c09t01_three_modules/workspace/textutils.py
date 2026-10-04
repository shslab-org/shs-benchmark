"""Module 1: basic text utilities."""


def word_count(text: str) -> int:
    """Count whitespace-separated tokens in *text*."""
    return len(text.split())
