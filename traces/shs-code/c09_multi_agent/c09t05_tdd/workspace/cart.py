"""Shopping cart implementation satisfying test_cart.py (TDD)."""


class Cart:
    """A simple shopping cart keyed by SKU.

    Attributes:
        _items: dict mapping sku -> quantity
    """

    def __init__(self):
        self._items = {}

    def add(self, sku, qty=1):
        """Add `qty` units of `sku` to the cart (default qty is 1)."""
        if qty < 0:
            raise ValueError("qty must be non-negative")
        self._items[sku] = self._items.get(sku, 0) + qty

    def remove(self, sku):
        """Remove `sku` from the cart.

        Raises:
            ValueError: if `sku` is not present in the cart.
        """
        if sku not in self._items:
            raise ValueError(f"sku not in cart: {sku!r}")
        del self._items[sku]

    def items(self):
        """Return a snapshot (copy) of the cart as {sku: qty}."""
        return dict(self._items)

    def total(self, price_map):
        """Return the total cost: sum of qty * unit_price for each sku.

        Args:
            price_map: dict mapping sku -> unit price.

        Raises:
            KeyError: if a sku in the cart has no entry in price_map.
        """
        total = 0.0
        for sku, qty in self._items.items():
            total += qty * price_map[sku]  # KeyError for unknown sku
        return total
