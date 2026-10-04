"""Refactor task: cryptic names, missing docstrings."""

import time


def go(l, n=3, w=0.5):
    """run l? n? w?"""
    r = {}
    for x in l:
        for _ in range(n):
            time.sleep(w)
            try:
                x["fn"]()
                ok = True
            except Exception:
                ok = False
            if not ok:
                break
        r[x["id"]] = ok
    return r
