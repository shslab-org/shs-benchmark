"""Dictionary flattener.

Flattens arbitrarily nested dicts and lists into a single-level mapping
where nested keys are joined with a separator.
"""

from __future__ import annotations


def flatten(obj: dict, sep: str = ".") -> dict:
    """Flatten a nested dict into a single-level dict.

    Nested dicts are flattened by joining keys with ``sep``
    (e.g. ``{"a": {"b": 1}}`` -> ``{"a.b": 1}``). Lists are indexed
    by position (e.g. ``{"a": [10]}`` -> ``{"a.0": 10}``). Empty
    dicts and empty lists are kept as leaf values under their key.
    Scalars (str, int, float, bool, None) are leaf values. The
    input object is not mutated; a new dict is returned.

    Args:
        obj: The (possibly nested) dict to flatten.
        sep: Separator used to join nested keys (default ``"."``).

    Returns:
        A new flat dict mapping joined keys to leaf values.
    """
    result: dict = {}

    def _walk(value, key: str) -> None:
        if isinstance(value, dict) and value:
            for k, v in value.items():
                _walk(v, key + sep + str(k))
        elif isinstance(value, list) and value:
            for i, v in enumerate(value):
                _walk(v, key + sep + str(i))
        else:
            result[key] = value

    for k, v in obj.items():
        _walk(v, str(k))
    return result
