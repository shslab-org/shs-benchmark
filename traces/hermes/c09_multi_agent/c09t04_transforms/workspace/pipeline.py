"""Map-reduce style transform framework.

A pipeline applies a list of independent Transform objects to a value in
order. A transform that raises is skipped (value passes through unchanged);
with collect_errors=True the failures are reported alongside the result.
"""

from __future__ import annotations

import functools
from typing import Any, Callable, List, Tuple


class Transform:
    """A named, optional, independently verifiable transformation."""

    def __init__(self, name: str, fn: Callable[[Any], Any], enabled: bool = True):
        self.name = name
        self.fn = fn
        self.enabled = enabled

    def apply(self, value: Any) -> Any:
        """Apply the underlying function to value."""
        return self.fn(value)

    def __repr__(self) -> str:
        state = "enabled" if self.enabled else "disabled"
        return f"Transform({self.name!r}, {state})"


def run_pipeline(value: Any, transforms: List[Transform], collect_errors: bool = False):
    """Apply transforms in order to value.

    - Disabled transforms are skipped silently.
    - A transform that raises an exception is skipped; the value passes
      through unchanged by that step.
    - If collect_errors is True, returns (result, errors) where errors is a
      list of the names of transforms that raised, in pipeline order.
      Otherwise returns just the result.
    """
    result = value
    errors: List[str] = []
    for transform in transforms:
        if not transform.enabled:
            continue
        try:
            result = transform.apply(result)
        except Exception:
            if collect_errors:
                errors.append(transform.name)
            # skipped: value unchanged, keep flowing
    if collect_errors:
        return result, errors
    return result


# ---------------------------------------------------------------------------
# Independent example transforms. Each one is self-contained and could be
# developed and verified on its own (no dependencies on the others).
# ---------------------------------------------------------------------------

def upper(value: str) -> str:
    return value.upper()


def strip(value: str) -> str:
    return value.strip()


def reverse(value: str) -> str:
    return value[::-1]


def word_count_wrap(value: str) -> str:
    """Return the whitespace-separated word count of value, as a string."""
    return str(len(value.split()))


UPPER = Transform("upper", upper)
STRIP = Transform("strip", strip)
REVERSE = Transform("reverse", reverse)
WORD_COUNT = Transform("word_count_wrap", word_count_wrap)

EXAMPLE_TRANSFORMS = [UPPER, STRIP, REVERSE, WORD_COUNT]


if __name__ == "__main__":
    source = "  hello benchmark  "
    print(f"input: {source!r}")
    value = source
    for transform in EXAMPLE_TRANSFORMS:
        value = run_pipeline(value, [transform])
        print(f"  after {transform.name:14s} -> {value!r}")
