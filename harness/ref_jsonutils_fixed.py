"""JSON helpers - reference fixed version (c04t04)."""
import json


def safe_get(obj, path, default=None):
    try:
        cur = obj
        for part in path.split("."):
            if isinstance(cur, list):
                cur = cur[int(part)]
            else:
                cur = cur[part]
        return cur
    except Exception:
        return default


def _clone(v):
    if isinstance(v, dict):
        return {k: _clone(x) for k, x in v.items()}
    if isinstance(v, list):
        return [_clone(x) for x in v]
    return v


def deep_merge(a, b):
    out = {k: _clone(v) for k, v in a.items()}
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        elif isinstance(v, dict):
            out[k] = _clone(v)
        else:
            out[k] = v
    return out


def dumps_compact(obj):
    return json.dumps(obj, separators=(",", ":"))


def parse_lenient(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    DQ = chr(34)
    SQ = chr(39)
    BS = chr(92)
    out = []
    in_str = False
    quote = ""
    i = 0
    while i < len(text):
        ch = text[i]
        if not in_str:
            if ch in (DQ, SQ):
                in_str = True
                quote = ch
                out.append(DQ)
            else:
                out.append(ch)
        else:
            if ch == BS and i + 1 < len(text):
                out.append(ch)
                out.append(text[i + 1])
                i += 2
                continue
            if ch == quote:
                in_str = False
                out.append(DQ)
            elif ch == DQ:
                out.append(BS + DQ)
            else:
                out.append(ch)
        i += 1
    return json.loads("".join(out))
