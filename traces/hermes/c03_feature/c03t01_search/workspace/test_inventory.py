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


def test_search_finds_case_insensitive():
    inv = Inventory()
    inv.add_item("A", "apple juice", 2.0, 1)
    inv.add_item("B", "Banana", 1.0, 5)
    inv.add_item("C", "pineapple", 0.7, 3)
    names = [i["name"] for i in inv.search("apple")]
    assert names == ["apple juice", "pineapple"]


def test_search_uppercase_keyword_matches_mixed_case_names():
    inv = Inventory()
    inv.add_item("A", "apple juice", 2.0, 1)
    inv.add_item("B", "Banana", 1.0, 5)
    names = [i["name"] for i in inv.search("APPLE")]
    assert names == ["apple juice"]


def test_search_no_match_returns_empty():
    inv = Inventory()
    inv.add_item("A", "apple juice", 2.0, 1)
    assert inv.search("cherry") == []
