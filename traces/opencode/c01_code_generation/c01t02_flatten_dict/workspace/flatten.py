def flatten(obj: dict, sep: str = ".") -> dict:
    """Flatten a nested dict, joining nested keys with sep and indexing lists by position."""
    out = {}
    def rec(value, prefix):
        if isinstance(value, dict):
            if not value:
                out[prefix] = {}
            else:
                for k, v in value.items():
                    rec(v, f"{prefix}{sep}{k}" if prefix else str(k))
        elif isinstance(value, list):
            if not value:
                out[prefix] = []
            else:
                for i, v in enumerate(value):
                    rec(v, f"{prefix}{sep}{i}")
        else:
            out[prefix] = value
    for k, v in obj.items():
        rec(v, str(k))
    return out
