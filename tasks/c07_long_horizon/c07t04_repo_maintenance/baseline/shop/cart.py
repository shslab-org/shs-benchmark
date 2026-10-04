class Cart:
    """Shopping cart. BUG: remove() does nothing (tests fail)."""

    def __init__(self):
        self._items = {}

    def add(self, sku, qty=1):
        self._items[sku] = self._items.get(sku, 0) + qty

    def remove(self, sku):
        pass  # TODO broken

    def items(self):
        return dict(self._items)
