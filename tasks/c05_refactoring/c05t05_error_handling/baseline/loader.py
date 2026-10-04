"""Config loader with unacceptable error handling (refactor task)."""

import json


def load(path):
    try:
        with open(path) as f:
            return json.load(f)
    except:                                    # BUG: bare except swallows everything
        return {}


def get(data, path):
    try:
        for k in path.split("."):
            data = data[k]
        return data
    except:                                    # BUG: bare except
        return None


def save(path, data):
    try:
        with open(path, "w") as f:
            json.dump(data, f)
    except:                                    # BUG: bare except hides real IO errors
        return False
    return True
