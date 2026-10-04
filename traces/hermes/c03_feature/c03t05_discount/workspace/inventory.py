"""Tiny inventory package. Extend it per task instructions."""


class Inventory:
    def __init__(self):
        self._items = {}   # sku -> dict(name, price, qty)

    def add_item(self, sku, name, price, qty):
        if sku in self._items:
            self._items[sku]["qty"] += qty
        else:
            self._items[sku] = {"name": name, "price": price, "qty": qty}
        return self._items[sku]

    def get_item(self, sku):
        return self._items.get(sku)

    def list_items(self):
        return sorted(self._items.values(), key=lambda i: i["name"])

    def apply_discount(self, sku, pct):
        if sku not in self._items:
            raise ValueError(f"unknown sku: {sku}")
        if not (0 <= pct <= 100):
            raise ValueError(f"discount pct out of range: {pct}")
        self._items[sku]["discount"] = pct

    def price_with_discount(self, sku):
        if sku not in self._items:
            raise ValueError(f"unknown sku: {sku}")
        item = self._items[sku]
        pct = item.get("discount", 0)
        return item["price"] * (1 - pct / 100)
