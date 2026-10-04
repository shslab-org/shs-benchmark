"""Independent example transforms for the pipeline framework.

Each function is a pure ``value -> value`` transform that can be developed
and verified on its own, then wrapped in a ``Transform`` for use in
``run_pipeline``.
"""


def upper(value):
    """Return value with letters upper-cased."""
    return value.upper()


def strip(value):
    """Return value with surrounding whitespace removed."""
    return value.strip()


def reverse(value):
    """Return value reversed."""
    return value[::-1]


def word_count_wrap(value):
    """Return the whitespace-split word count of value as a string."""
    return str(len(value.split()))
