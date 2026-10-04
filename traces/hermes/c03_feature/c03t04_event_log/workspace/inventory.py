"""Tiny inventory package. Extend it per task instructions."""

import datetime


class Inventory:
    def __init__(self):
        self._items = {}   # sku -> dict(name, price, qty)
        self._events = []  # append-only chronological log

    @staticmethod
    def _make_event(action, sku, qty):
        return {
            "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "action": action,
            "sku": sku,
            "qty": qty,
        }

    def add_item(self, sku, name, price, qty):
        if sku in self._items:
            self._items[sku]["qty"] += qty
        else:
            self._items[sku] = {"name": name, "price": price, "qty": qty}
        self._events.append(self._make_event("add", sku, qty))
        return self._items[sku]

    def remove_stock(self, sku, qty):
        item = self._items.get(sku)
        if item is None:
            raise ValueError(f"unknown sku: {sku!r}")
        if qty <= 0:
            raise ValueError("qty must be > 0")
        if qty > item["qty"]:
            raise ValueError("qty exceeds available stock")
        item["qty"] -= qty
        self._events.append(self._make_event("remove", sku, qty))
        return item

    def get_events(self):
        return list(self._events)

    def get_item(self, sku):
        return self._items.get(sku)

    def list_items(self):
        return sorted(self._items.values(), key=lambda i: i["name"])
