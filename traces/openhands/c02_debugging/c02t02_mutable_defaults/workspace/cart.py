"""Shopping cart utilities. BUG: mutable default arguments accumulate state."""

import json


def add_item(item, cart=None):
    if cart is None:
        cart = []
    cart.append(item)
    return cart


def add_tagged(item, tags=None, extra=None):
    if tags is None:
        tags = []
    if extra is None:
        extra = {}
    tags.append(item["sku"])
    extra["last"] = item["sku"]
    return {"sku": item["sku"], "tags": tags, "extra": extra}


def save(cart, path):
    with open(path, "w") as f:
        json.dump(cart, f)
