"""Pytest suite for the shopping cart (:class:`cart.Cart`).

This is the TESTS workstream of a TDD task. The implementation lives in
``cart.py`` (the other workstream's job); this file only defines the contract
the implementation must satisfy, written first so the tests fail until the
implementation lands.

Contract under test
--------------------
- ``Cart()``            -> a new, empty cart
- ``add(sku, qty=1)``   -> adds ``qty`` units of ``sku``; repeated calls for
  the same sku ACCUMULATE
- ``remove(sku)``       -> removes ``sku``; raises ``ValueError`` when absent
- ``items()``           -> a SNAPSHOT (a copy) of the current ``{sku: qty}``
- ``total(price_map)``  -> ``sum(qty * price_map[sku])`` over every sku;
  raises ``KeyError`` when a cart sku is not a key in ``price_map``

Stdlib + pytest only. Run with::

    pytest
"""

import pytest

from cart import Cart


def test_new_cart_is_empty():
    """A fresh cart has no items and a zero (float) total."""
    cart = Cart()
    assert cart.items() == {}
    assert cart.total({}) == 0.0


def test_add_default_qty_is_one():
    """Adding a sku without an explicit quantity defaults to 1."""
    cart = Cart()
    cart.add("apple")
    assert cart.items() == {"apple": 1}


def test_add_with_explicit_qty():
    """Adding a sku with an explicit quantity stores exactly that quantity."""
    cart = Cart()
    cart.add("apple", 5)
    assert cart.items()["apple"] == 5


def test_add_accumulates_same_sku():
    """Repeated adds for the same sku accumulate their quantities."""
    cart = Cart()
    cart.add("apple")        # 1
    cart.add("apple", 3)     # +3
    assert cart.items()["apple"] == 4


def test_items_returns_snapshot():
    """items() returns a snapshot copy, not a live view of the cart.

    - The returned dict equals the current mapping.
    - Adding to the cart AFTER taking the snapshot does NOT change the
      already-returned snapshot.
    - Mutating the returned dict does NOT affect the cart.
    """
    cart = Cart()
    cart.add("apple", 3)
    cart.add("banana", 7)

    snap = cart.items()
    # 1) The snapshot equals the current mapping.
    assert snap == {"apple": 3, "banana": 7}

    # 2) A change to the cart AFTER the snapshot is taken must not leak
    #    back into the already-returned snapshot.
    cart.add("apple", 10)   # cart is now {"apple": 13, "banana": 7}
    assert snap == {"apple": 3, "banana": 7}   # snapshot is still the old view

    # 3) Mutating the returned snapshot must not affect the cart.
    snap["apple"] = 999
    snap["cherry"] = 42
    snap.pop("banana")
    assert cart.items() == {"apple": 13, "banana": 7}


def test_remove_existing_sku():
    """remove() drops the named sku; removing the only sku leaves an empty cart."""
    cart = Cart()
    cart.add("apple")
    cart.remove("apple")
    assert cart.items() == {}


def test_remove_missing_sku_raises_value_error():
    """Removing a sku that is not in the cart raises ValueError."""
    cart = Cart()
    cart.add("apple")
    with pytest.raises(ValueError):
        cart.remove("nope")

    # Also raises on a totally empty cart.
    empty = Cart()
    with pytest.raises(ValueError):
        empty.remove("nope")


def test_total_sums_qty_times_unit_price():
    """total() equals sum(qty * unit_price) over every sku in the cart."""
    cart = Cart()
    cart.add("apple", 2)
    cart.add("banana", 3)
    price_map = {"apple": 1.5, "banana": 0.5}
    # 2 * 1.5 + 3 * 0.5 == 3.0 + 1.5 == 4.5 (exactly representable float)
    assert cart.total(price_map) == 2 * 1.5 + 3 * 0.5
    assert cart.total(price_map) == 4.5


def test_total_unknown_sku_raises_key_error():
    """total() raises KeyError when a cart sku is absent from price_map."""
    cart = Cart()
    cart.add("apple")
    with pytest.raises(KeyError):
        cart.total({"banana": 1.0})
