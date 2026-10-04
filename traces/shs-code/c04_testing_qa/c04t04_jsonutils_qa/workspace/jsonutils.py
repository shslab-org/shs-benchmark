"""JSON helpers — CONTAINS SEEDED BUGS for the QA benchmark."""
import json


def safe_get(obj, path, default=None):
    """path: dot-separated keys, e.g. 'a.b.0' for lists. Returns default on any miss."""
    try:
        cur = obj
        for part in path.split("."):
            if isinstance(cur, list):
                cur = cur[int(part)]
            else:
                cur = cur[part]
        return cur
    except (KeyError, IndexError, TypeError):
        return default                        # BUG 1: also swallows ValueError from bad int — acceptable; the seeded bug is deep_merge below


def deep_merge(a, b):
    """Recursive merge: values from b win; dicts merge recursively; returns new dict."""
    out = dict(a)
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)    # looks right...
        else:
            out[k] = v
    return out                                 # BUG 2: 'a' top-level mutated? no — dict(a) is shallow but nested dicts rebuilt. SEEDED BUG is below.


def dumps_compact(obj):
    return json.dumps(obj, separators=(",", ":"))   # correct on purpose


def parse_lenient(text):
    """Parse JSON; accepts single quotes by naive replacement."""
    if text.strip().startswith("'"):
        text = text.replace("'", '"')         # BUG 3: breaks apostrophes inside strings ("it's")
    return json.loads(text)
