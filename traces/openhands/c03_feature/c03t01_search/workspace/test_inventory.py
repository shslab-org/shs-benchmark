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


def test_search_case_insensitive():
    inv = Inventory()
    inv.add_item("B", "Banana", 1.0, 2)
    inv.add_item("A", "Apple", 0.5, 1)
    inv.add_item("C", "cherry", 2.0, 3)
    names = [i["name"] for i in inv.search("APPLE")]
    assert names == ["Apple"]
    assert [i["name"] for i in inv.search("an")] == ["Banana"]


def test_search_sorted_and_no_match():
    inv = Inventory()
    inv.add_item("B", "Banana", 1.0, 2)
    inv.add_item("A", "Apple", 0.5, 1)
    inv.add_item("C", "Cherry", 2.0, 3)
    assert inv.search("zz") == []
    names = [i["name"] for i in inv.search("a")]
    assert names == ["Apple", "Banana"]


def test_search_multiple_keyword_occurrences():
    inv = Inventory()
    inv.add_item("L", "laptop", 999.0, 1)
    inv.add_item("N", "Notebook", 5.0, 3)
    inv.add_item("S", "Pen", 1.5, 10)
    names = [i["name"] for i in inv.search("te")]
    assert names == ["Notebook"]
    names = [i["name"] for i in inv.search("o")]
    assert names == ["Notebook", "laptop"]


def test_search_empty_keyword_matches_all_sorted():
    inv = Inventory()
    inv.add_item("X", "Zebra", 1.0, 1)
    inv.add_item("Y", "Apple", 2.0, 2)
    inv.add_item("Z", "Mango", 3.0, 3)
    names = [i["name"] for i in inv.search("")]
    assert names == ["Apple", "Mango", "Zebra"]
