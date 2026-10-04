class Cart:
    """Shopping cart."""

    def __init__(self):
        self._items = {}

    def add(self, sku, qty=1):
        self._items[sku] = self._items.get(sku, 0) + qty

    def remove(self, sku):
        self._items.pop(sku, None)

    def items(self):
        return dict(self._items)
