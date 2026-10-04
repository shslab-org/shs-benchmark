def flatten(obj: dict, sep: str = ".") -> dict:
    """Flatten a nested dictionary into a single-level dict.

    Nested dicts are flattened by joining their keys with ``sep``
    (e.g. ``{"a": {"b": 1}}`` -> ``{"a.b": 1}``). Lists are indexed
    by position (e.g. ``{"a": [10]}`` -> ``{"a.0": 10}``). Empty
    dicts and empty lists are kept as leaf values. The input is not
    mutated.
    """
    result: dict = {}
    if not obj:
        return result

    def _flatten(prefix: str, value) -> None:
        if isinstance(value, dict) and value:
            for key, sub in value.items():
                _flatten(f"{prefix}{sep}{key}" if prefix else key, sub)
        elif isinstance(value, list) and value:
            for idx, sub in enumerate(value):
                _flatten(f"{prefix}{sep}{idx}", sub)
        else:
            # Scalars (str, int, float, bool, None) and empty dict/list
            # are kept as leaf values.
            result[prefix] = value

    _flatten("", obj)
    return result
