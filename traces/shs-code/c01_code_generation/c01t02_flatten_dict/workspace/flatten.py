"""Utilities for flattening nested Python dictionaries.

The public entry point is :func:`flatten`, which recursively flattens a
nested ``dict`` structure into a single-level mapping. Key paths are
joined with a configurable separator (default ``"."``).

Rules
-----
* Nested dicts are flattened by joining keys with the separator.
* Lists are flattened by index: ``{"a": [1, 2]}`` becomes
  ``{"a.0": 1, "a.1": 2}``.
* Empty dicts and empty lists are treated as *leaf* values and kept
  under their key (e.g. ``{"a": {}}`` -> ``{"a": {}}``).
* Non-dict/list values (str, int, float, bool, None, …) are leaves.
* The input object is never mutated.

Example
-------
>>> flatten({"a": {"b": [1, 2], "c": {"d": None}}})
{'a.b.0': 1, 'a.b.1': 2, 'a.c.d': None}
"""

from typing import Any, Dict, List

__all__ = ["flatten"]


def _iter_leaf_items(obj: Any, prefix: str, sep: str):
    """Yield (flattened_key, leaf_value) pairs for a nested structure.

    Parameters
    ----------
    obj:
        The (possibly nested) structure to flatten.
    prefix:
        The key path accumulated so far (empty string for the root).
    sep:
        Separator used when joining key path components.
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            child = f"{prefix}{sep}{key}" if prefix else str(key)
            if isinstance(value, (dict, list)) and value:
                # Non-empty container: recurse deeper.
                yield from _iter_leaf_items(value, child, sep)
            else:
                # Empty container or scalar: leaf.
                yield child, value
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            child = f"{prefix}{sep}{i}" if prefix else str(i)
            if isinstance(value, (dict, list)) and value:
                yield from _iter_leaf_items(value, child, sep)
            else:
                yield child, value
    else:
        # Plain scalar — unreachable when called at the root, but kept
        # for completeness.
        yield prefix, obj


def flatten(obj: dict, sep: str = ".") -> Dict[str, Any]:
    """Flatten a nested dictionary into a single-level mapping.

    Nested dicts are flattened by joining their keys with ``sep``;
    lists are flattened by their integer index. Empty dicts/lists and
    scalar values (including ``None``) are kept as leaf values. The
    input structure is not mutated.

    Parameters
    ----------
    obj:
        The (possibly nested) dictionary to flatten.
    sep:
        Separator used to join key components in the flattened keys.
        Defaults to ``"."``.

    Returns
    -------
    dict
        A new, flat dictionary with dotted (or ``sep``-joined) keys
        and scalar / empty-container leaf values.

    Examples
    --------
    >>> flatten({"a": {"b": 1}})
    {'a.b': 1}
    >>> flatten({"a": [10, 20]})
    {'a.0': 10, 'a.1': 20}
    >>> flatten({"a": {}}, sep="_")
    {'a': {}}
    """
    return {key: value for key, value in _iter_leaf_items(obj, "", sep)}
