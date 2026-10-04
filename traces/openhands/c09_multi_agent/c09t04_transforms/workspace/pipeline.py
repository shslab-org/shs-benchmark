"""Small map-reduce style transformation framework.

Each Transform is an independent, self-contained unit that can be
developed and verified on its own. run_pipeline chains them together,
skipping any transform that raises, and optionally collecting the
names of the failed transforms.
"""


class Transform:
    """A named transformation applied to a value."""

    def __init__(self, name: str, fn, enabled: bool = True):
        self.name = name
        self.fn = fn
        self.enabled = enabled

    def apply(self, value):
        """Return fn(value), or value unchanged when disabled."""
        if not self.enabled:
            return value
        return self.fn(value)


def run_pipeline(value, transforms: list, collect_errors: bool = False):
    """Apply transforms in order.

    A transform that raises an exception is skipped (value unchanged).
    If collect_errors is True, returns (result, errors) where errors is
    the list of names of the failed transforms; otherwise just result.
    """
    errors = []
    for transform in transforms:
        try:
            value = transform.apply(value)
        except Exception:
            errors.append(transform.name)
    if collect_errors:
        return value, errors
    return value


# --- Independent example transforms -------------------------------------
# Each one is self-contained and can be tested in isolation.

def _to_str(value):
    """Helpers guard against non-string input."""
    return value if isinstance(value, str) else str(value)


def upper(value):
    """Uppercase the value."""
    return _to_str(value).upper()


def strip(value):
    """Strip surrounding whitespace."""
    return _to_str(value).strip()


def reverse(value):
    """Reverse the value."""
    return _to_str(value)[::-1]


def word_count_wrap(value):
    """Return the number of whitespace-separated words as a string."""
    return str(len(_to_str(value).split()))


# Default pipeline of the four independent transforms.
DEFAULT_TRANSFORMS = [
    Transform("upper", upper),
    Transform("strip", strip),
    Transform("reverse", reverse),
    Transform("word_count_wrap", word_count_wrap),
]


if __name__ == "__main__":
    source = "  hello benchmark  "
    print(f"start: {source!r}")
    for transform in DEFAULT_TRANSFORMS:
        source = transform.apply(source)
        print(f"after {transform.name}: {source!r}")
