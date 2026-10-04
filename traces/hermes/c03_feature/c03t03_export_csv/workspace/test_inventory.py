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


def test_export_csv_single_item():
    inv = Inventory()
    inv.add_item("SKU1", "Apple", 0.5, 10)
    assert inv.export_csv() == "sku,name,price,qty\r\nSKU1,Apple,0.5,10\r\n"


def test_export_csv_empty_inventory():
    assert Inventory().export_csv() == "sku,name,price,qty\r\n"


def test_export_csv_order_matches_list_items():
    inv = Inventory()
    inv.add_item("B", "Banana", 1.0, 2)
    inv.add_item("A", "Apple", 0.5, 1)
    rows = inv.export_csv().strip().splitlines()
    assert rows[0] == "sku,name,price,qty"
    assert rows[1].startswith("A,Apple")
    assert rows[2].startswith("B,Banana")
    # same order as list_items()
    assert [r.split(",")[1] for r in rows[1:]] == [i["name"] for i in inv.list_items()]
