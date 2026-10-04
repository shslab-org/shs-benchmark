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


def test_search_case_insensitive_substring():
    inv = Inventory()
    inv.add_item("B", "Banana", 1.0, 2)
    inv.add_item("A", "Apple", 0.5, 1)
    inv.add_item("C", "Blueberry", 2.0, 3)
    results = inv.search("a")  # matches Apple, Banana (both contain 'a')
    assert [i["name"] for i in results] == ["Apple", "Banana"]


def test_search_sorted_by_name_like_list_items():
    inv = Inventory()
    inv.add_item("3", "Zebra", 5.0, 1)
    inv.add_item("1", "apple", 1.0, 1)
    inv.add_item("2", "MANGO", 2.0, 1)
    results = inv.search("a")  # apple, Mango, Zebra all contain 'a'
    assert [i["name"] for i in results] == ["MANGO", "Zebra", "apple"]
    # also verify same order as list_items() filtered
    assert [i for i in inv.list_items() if "a" in i["name"].lower()] == results
