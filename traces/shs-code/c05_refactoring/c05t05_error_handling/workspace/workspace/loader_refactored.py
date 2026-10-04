"""Config loader with precise exception handling.

load(path): opens and parses JSON. Raises FileNotFoundError when the file is
    missing, json.JSONDecodeError when the content is not valid JSON, and
    returns the parsed dict otherwise. No other exceptions are swallowed.
get(data, path): walks a dotted path through nested dicts. Returns None on
    missing keys or wrong types — catches only (KeyError, TypeError).
save(path, data): writes JSON. Real OSError (disk full, permission denied,
    etc.) propagates. Returns True on success.
"""

import json


def load(path):
    with open(path) as f:
        return json.load(f)


def get(data, path):
    try:
        for k in path.split("."):
            data = data[k]
        return data
    except (KeyError, TypeError):
        return None


def save(path, data):
    with open(path, "w") as f:
        json.dump(data, f)
    return True
