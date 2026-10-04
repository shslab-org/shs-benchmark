"""Shopping cart utilities. BUG: mutable default arguments accumulate state."""

import json


def add_item(item, cart=[]):          # BUG: shared mutable default
    cart.append(item)
    return cart


def add_tagged(item, tags=[], extra={}):   # BUG: two shared mutable defaults
    tags.append(item["sku"])
    extra["last"] = item["sku"]
    return {"sku": item["sku"], "tags": tags, "extra": extra}


def save(cart, path):
    with open(path, "w") as f:
        json.dump(cart, f)
