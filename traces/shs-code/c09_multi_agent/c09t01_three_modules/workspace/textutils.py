"""textutils: whitespace token counting utilities."""


def word_count(text: str) -> int:
    """Return the number of whitespace-separated tokens in *text*.

    Consecutive whitespace (spaces, tabs, newlines) is treated as a single
    separator, matching the semantics of ``str.split()``.

    Examples:
        >>> word_count("hello world")
        2
        >>> word_count("  one   two three  ")
        3
        >>> word_count("")
        0
        >>> word_count("   ")
        0
    """
    return len(text.split())
