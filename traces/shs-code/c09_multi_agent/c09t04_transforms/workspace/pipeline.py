"""Small map-reduce style transformation framework.

``Transform`` wraps a named, enabled-flagged function; ``run_pipeline``
applies a sequence of transforms in order, skipping any that raise,
optionally collecting the names of the failing transforms.
"""

from transforms import upper, strip, reverse, word_count_wrap


class Transform:
    """A named transformation to be applied within a pipeline."""

    def __init__(self, name: str, fn, enabled: bool = True):
        self.name = name
        self.fn = fn
        self.enabled = enabled

    def apply(self, value):
        """Return the result of applying this transform's function to value."""
        return self.fn(value)


def run_pipeline(value, transforms: list, collect_errors: bool = False):
    """Apply ``transforms`` to ``value`` in order.

    A transform that raises is skipped (value passes through unchanged).
    Disabled transforms are also skipped. When ``collect_errors`` is True
    the function returns ``(result, errors)`` where ``errors`` is a list of
    the names of the transforms that raised; otherwise it returns just the
    result.
    """
    result = value
    errors = []
    for t in transforms:
        if not t.enabled:
            continue
        try:
            result = t.apply(result)
        except Exception:
            errors.append(t.name)
    if collect_errors:
        return result, errors
    return result


# ---------------------------------------------------------------------------
# Demonstration (independent example transforms live in transforms.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    text = "  hello benchmark  "
    print(f"input: {text!r}")

    print(f"upper: {upper(text)!r}")
    print(f"strip: {strip(text)!r}")
    print(f"reverse: {reverse(text)!r}")
    print(f"word_count_wrap: {word_count_wrap(text)!r}")

    transforms = [
        Transform("strip", strip),
        Transform("upper", upper),
        Transform("word_count_wrap", word_count_wrap),
        Transform("reverse", reverse),
    ]
    result, errors = run_pipeline(text, transforms, collect_errors=True)
    print(f"pipeline result: {result!r}, errors: {errors}")

    # a failing transform gets skipped when errors are collected
    def failing(value):
        raise ValueError("boom")

    failing_transforms = [
        Transform("strip", strip),
        Transform("failing", failing),
        Transform("reverse", reverse),
    ]
    result2, errors2 = run_pipeline(text, failing_transforms, collect_errors=True)
    print(f"pipeline with failing transform: {result2!r}, errors: {errors2}")
