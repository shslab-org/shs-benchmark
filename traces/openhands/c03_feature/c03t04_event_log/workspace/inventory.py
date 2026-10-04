"""Tiny inventory package. Extend it per task instructions."""

from datetime import datetime, timezone


class Inventory:
    def __init__(self):
        self._items = {}   # sku -> dict(name, price, qty)
        self._events = []  # append-only event log

    def add_item(self, sku, name, price, qty):
        if sku in self._items:
            self._items[sku]["qty"] += qty
        else:
            self._items[sku] = {"name": name, "price": price, "qty": qty}
        self._events.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "add",
            "sku": sku,
            "qty": qty,
        })
        return self._items[sku]

    def remove_stock(self, sku, qty):
        item = self._items.get(sku)
        if item is None:
            raise ValueError(f"Unknown sku: {sku}")
        if qty <= 0:
            raise ValueError("qty must be positive")
        if qty > item["qty"]:
            raise ValueError("qty exceeds available stock")
        item["qty"] -= qty
        self._events.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "remove",
            "sku": sku,
            "qty": qty,
        })

    def get_item(self, sku):
        return self._items.get(sku)

    def list_items(self):
        return sorted(self._items.values(), key=lambda i: i["name"])

    def get_events(self):
        return list(self._events)
