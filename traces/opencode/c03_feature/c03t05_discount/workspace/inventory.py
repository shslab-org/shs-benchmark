"""Tiny inventory package. Extend it per task instructions."""


class Inventory:
    def __init__(self):
        self._items = {}   # sku -> dict(name, price, qty)
        self._discounts = {}  # sku -> discount pct

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

    def apply_discount(self, sku: str, pct: float) -> None:
        if sku not in self._items:
            raise ValueError(f"unknown sku: {sku}")
        if not (0 <= pct <= 100):
            raise ValueError("pct must be in 0..100")
        self._discounts[sku] = pct

    def price_with_discount(self, sku: str) -> float:
        if sku not in self._items:
            raise ValueError(f"unknown sku: {sku}")
        item = self._items[sku]
        pct = self._discounts.get(sku, 0)
        return item["price"] * (1 - pct / 100)
