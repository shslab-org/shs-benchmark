"""Test suite for the Cart class (test-first / TDD).

Covers:
  - add with default qty 1
  - add with explicit qty (including qty accumulation on re-add)
  - items() returning a snapshot dict
  - remove of existing sku
  - remove of missing sku raising ValueError
  - total(price_map) summing qty * unit_price for known skus
  - total raising KeyError for an unknown sku in the cart
"""

import pytest

from cart import Cart


# --- add -------------------------------------------------------------------

def test_add_default_qty_is_one():
    cart = Cart()
    cart.add("sku-a")
    assert cart.items() == {"sku-a": 1}


def test_add_explicit_qty():
    cart = Cart()
    cart.add("sku-b", qty=3)
    assert cart.items() == {"sku-b": 3}


def test_add_accumulates_qty_on_repeat():
    cart = Cart()
    cart.add("sku-a")
    cart.add("sku-a", qty=2)
    assert cart.items() == {"sku-a": 3}


# --- items -----------------------------------------------------------------

def test_items_empty_cart():
    assert Cart().items() == {}


def test_items_is_snapshot_not_live_view():
    cart = Cart()
    cart.add("sku-a")
    snapshot = cart.items()
    cart.add("sku-b")
    # mutating the cart afterwards must not alter the returned dict
    assert snapshot == {"sku-a": 1}


def test_items_multiple_skus():
    cart = Cart()
    cart.add("sku-a")
    cart.add("sku-b", qty=4)
    assert cart.items() == {"sku-a": 1, "sku-b": 4}


# --- remove ----------------------------------------------------------------

def test_remove_existing_sku():
    cart = Cart()
    cart.add("sku-a")
    cart.add("sku-b", qty=2)
    cart.remove("sku-a")
    assert cart.items() == {"sku-b": 2}


def test_remove_missing_sku_raises_value_error():
    cart = Cart()
    cart.add("sku-a")
    with pytest.raises(ValueError):
        cart.remove("never-added")


# --- total -----------------------------------------------------------------

def test_total_empty_cart_is_zero():
    assert Cart().total({"sku-a": 10.0}) == 0.0


def test_total_sums_qty_times_unit_price():
    cart = Cart()
    cart.add("sku-a")          # 1 * 10.0
    cart.add("sku-b", qty=3)   # 3 * 4.5
    price_map = {"sku-a": 10.0, "sku-b": 4.5}
    assert cart.total(price_map) == pytest.approx(10.0 + 3 * 4.5)


def test_total_ignores_prices_for_skus_not_in_cart():
    cart = Cart()
    cart.add("sku-a", qty=2)
    price_map = {"sku-a": 5.0, "other": 100.0}
    assert cart.total(price_map) == pytest.approx(10.0)


def test_total_unknown_sku_raises_key_error():
    cart = Cart()
    cart.add("sku-missing")
    with pytest.raises(KeyError):
        cart.total({"sku-other": 1.0})
