class Cart:
    """Simple shopping cart keyed by sku."""

    def __init__(self):
        self._items = {}

    def add(self, sku, qty=1):
        self._items[sku] = self._items.get(sku, 0) + qty

    def remove(self, sku):
        if sku not in self._items:
            raise ValueError(f"sku not in cart: {sku!r}")
        del self._items[sku]

    def items(self):
        return dict(self._items)

    def total(self, price_map):
        return float(sum(qty * price_map[sku] for sku, qty in self._items.items()))
