"""Shopping cart.

Provides :class:`Cart`, a simple shopping cart keyed by SKU.

Contract
--------
- ``Cart()``        -> a new, empty cart.
- ``add(sku, qty=1)`` -> adds ``qty`` units of ``sku`` (default 1); repeated
  adds for the same sku accumulate.
- ``remove(sku)``   -> removes ``sku`` entirely; raises ``ValueError`` when
  the sku is not present in the cart.
- ``items()``       -> returns a snapshot dict ``{sku: qty}`` (a copy; mutating
  it does not affect the cart).
- ``total(price_map)`` -> returns ``sum(qty * price_map[sku])`` as a ``float``;
  raises ``KeyError`` when a cart sku is missing from ``price_map``; returns
  ``0.0`` for an empty cart.
"""

from __future__ import annotations

import typing


class Cart:
    """A shopping cart mapping SKU -> accumulated quantity."""

    def __init__(self) -> None:
        # Internal state: {sku: total_quantity}
        self._items: dict[str, int] = {}

    def add(self, sku: str, qty: int = 1) -> None:
        """Add ``qty`` units of ``sku`` (default 1), accumulating totals.

        Repeated calls for the same sku add to the existing quantity.
        """
        self._items[sku] = self._items.get(sku, 0) + qty

    def remove(self, sku: str) -> None:
        """Remove ``sku`` entirely from the cart.

        Raises:
            ValueError: if ``sku`` is not present in the cart.
        """
        if sku not in self._items:
            raise ValueError(f"cannot remove SKU {sku!r}: not in cart")
        del self._items[sku]

    def items(self) -> dict[str, int]:
        """Return a snapshot ``{sku: qty}``.

        The returned dict is a copy; mutating it does not affect the cart.
        """
        return dict(self._items)

    def total(self, price_map: dict[str, typing.Union[int, float]]) -> float:
        """Return the total cost as a ``float``.

        Computes ``sum(qty * price_map[sku])`` over every sku in the cart.

        Raises:
            KeyError: if a sku in the cart is absent from ``price_map``.

        Returns:
            0.0 for an empty cart; otherwise the float total.
        """
        total = 0.0
        for sku, qty in self._items.items():
            total += qty * price_map[sku]
        return total
