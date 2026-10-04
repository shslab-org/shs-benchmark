"""Backup utilities: persist a cart's items as JSON."""

import json


def backup_json(cart, path):
    """Write the cart's items to *path* as JSON (indent=2).

    Returns the dict of items that was written.
    """
    items = cart.items()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)
        f.write("\n")
    return items
