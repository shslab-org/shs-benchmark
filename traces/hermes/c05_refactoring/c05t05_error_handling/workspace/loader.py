"""Config loader with precise typed exception handling."""

import json


def load(path):
    # Let FileNotFoundError (missing file) and json.JSONDecodeError
    # (invalid JSON) propagate to the caller — no blanket catch.
    with open(path) as f:
        return json.load(f)


def get(data, path):
    try:
        for k in path.split("."):
            data = data[k]
    except (KeyError, TypeError):
        # Missing keys / wrong intermediate types are intentional
        # "not found" cases — return None.
        return None
    return data


def save(path, data):
    # Do not catch OSError: disk full, permission denied, etc. must
    # propagate. True is returned only on success.
    with open(path, "w") as f:
        json.dump(data, f)
    return True
