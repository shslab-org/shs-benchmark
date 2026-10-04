"""Tiny inventory package. Extend it per task instructions."""


class Inventory:
    def __init__(self):
        self._items = {}      # sku -> dict(name, price, qty)
        self._discounts = {}  # sku -> discount percentage (0..100)

    def add_item(self, sku, name, price, qty):
        if sku in self._items:
            self._items[sku]["qty"] += qty
        else:
            self._items[sku] = {"name": name, "price": price, "qty": qty}
        return self._items[sku]

    def get_item(self, sku):
        return self._items.get(sku)

    def apply_discount(self, sku: str, pct: float) -> None:
        """Set a discount percentage (0 <= pct <= 100) for an existing sku.

        Raises ValueError if the sku is unknown or pct is outside 0..100.
        """
        if sku not in self._items:
            raise ValueError(f"Unknown sku: {sku}")
        if not 0 <= pct <= 100:
            raise ValueError(f"pct must be within 0..100, got {pct}")
        self._discounts[sku] = pct

    def price_with_discount(self, sku: str) -> float:
        """Unit price for the sku after its discount (no discount = full price)."""
        item = self._items.get(sku)
        if item is None:
            raise ValueError(f"Unknown sku: {sku}")
        price = item["price"]
        discount = self._discounts.get(sku, 0.0)
        return price * (1 - discount / 100.0)

    def list_items(self):
        return sorted(self._items.values(), key=lambda i: i["name"])
