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

    def remove_stock(self, sku: str, qty: int) -> None:
        item = self._items.get(sku)
        if item is None:
            raise ValueError(f"unknown sku: {sku}")
        if qty <= 0:
            raise ValueError(f"qty must be positive, got {qty}")
        if qty > item["qty"]:
            raise ValueError(f"qty exceeds available stock for {sku}")
        item["qty"] -= qty

    def list_items(self):
        return sorted(self._items.values(), key=lambda i: i["name"])
