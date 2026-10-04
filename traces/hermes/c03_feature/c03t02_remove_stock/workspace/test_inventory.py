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


def test_remove_stock_decrements_qty():
    inv = Inventory()
    inv.add_item("SKU1", "Apple", 0.5, 10)
    inv.remove_stock("SKU1", 4)
    assert inv.get_item("SKU1")["qty"] == 6


def test_remove_stock_unknown_sku_raises():
    inv = Inventory()
    inv.add_item("SKU1", "Apple", 0.5, 10)
    with pytest.raises(ValueError):
        inv.remove_stock("MISSING", 1)


def test_remove_stock_nonpositive_qty_raises():
    inv = Inventory()
    inv.add_item("SKU1", "Apple", 0.5, 10)
    with pytest.raises(ValueError):
        inv.remove_stock("SKU1", 0)
    with pytest.raises(ValueError):
        inv.remove_stock("SKU1", -3)


def test_remove_stock_exceeds_available_raises():
    inv = Inventory()
    inv.add_item("SKU1", "Apple", 0.5, 10)
    with pytest.raises(ValueError):
        inv.remove_stock("SKU1", 11)
    assert inv.get_item("SKU1")["qty"] == 10
