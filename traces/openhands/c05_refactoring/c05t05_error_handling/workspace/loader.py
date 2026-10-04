"""Config loader with precise typed exception handling (refactored)."""

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
