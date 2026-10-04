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


def test_export_csv_empty():
    assert Inventory().export_csv() == "sku,name,price,qty"


def test_export_csv_rows():
    inv = Inventory()
    inv.add_item("SKU2", "Banana", 1.0, 2)
    inv.add_item("SKU1", "Apple", 0.5, 10)
    expected = (
        "sku,name,price,qty\n"
        "SKU1,Apple,0.5,10\n"
        "SKU2,Banana,1.0,2"
    )
    assert inv.export_csv() == expected
