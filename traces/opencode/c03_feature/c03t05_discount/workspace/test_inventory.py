import pytest
from inventory import Inventory


def test_add_and_get():
    inv = Inventory()
    inv.add_item("SKU1", "Apple", 0.5, 10)
    assert inv.get_item("SKU1") == {"name": "Apple", "price": 0.5, "qty": 10}


def test_add_same_sku_increments():
    inv = Inventory()
    inv.add_item("SKU1", "Apple", 0.5, 10)
    inv.add_item("SKU1", "Apple", 0.5, 5)
    assert inv.get_item("SKU1")["qty"] == 15


def test_list_sorted_by_name():
    inv = Inventory()
    inv.add_item("B", "Banana", 1.0, 2)
    inv.add_item("A", "Apple", 0.5, 1)
    names = [i["name"] for i in inv.list_items()]
    assert names == ["Apple", "Banana"]


def test_get_missing_returns_none():
    assert Inventory().get_item("NOPE") is None


def test_discount_reduces_price():
    inv = Inventory()
    inv.add_item("SKU1", "Apple", 0.5, 10)
    inv.apply_discount("SKU1", 20)
    assert inv.price_with_discount("SKU1") == pytest.approx(0.4)


def test_no_discount_returns_full_price():
    inv = Inventory()
    inv.add_item("SKU1", "Apple", 0.5, 10)
    assert inv.price_with_discount("SKU1") == 0.5


def test_apply_discount_unknown_sku_raises():
    inv = Inventory()
    with pytest.raises(ValueError):
        inv.apply_discount("NOPE", 10)


def test_apply_discount_out_of_range_raises():
    inv = Inventory()
    inv.add_item("SKU1", "Apple", 0.5, 10)
    with pytest.raises(ValueError):
        inv.apply_discount("SKU1", 101)
    with pytest.raises(ValueError):
        inv.apply_discount("SKU1", -1)
