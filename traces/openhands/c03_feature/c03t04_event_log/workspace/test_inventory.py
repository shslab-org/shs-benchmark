import datetime

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


def test_events_start_empty_and_record_adds():
    inv = Inventory()
    assert inv.get_events() == []
    inv.add_item("SKU1", "Apple", 0.5, 10)
    inv.add_item("SKU1", "Apple", 0.5, 5)
    events = inv.get_events()
    assert len(events) == 2
    assert all(e["action"] == "add" and e["sku"] == "SKU1" for e in events)
    assert [e["qty"] for e in events] == [10, 5]
    for e in events:
        datetime.datetime.fromisoformat(e["timestamp"])  # valid ISO-8601


def test_events_record_removals_in_order():
    inv = Inventory()
    inv.add_item("A", "Apple", 0.5, 10)
    inv.remove_stock("A", 3)
    inv.add_item("B", "Banana", 1.0, 2)
    inv.remove_stock("B", 2)
    events = inv.get_events()
    assert [e["action"] for e in events] == ["add", "remove", "add", "remove"]
    assert [e["sku"] for e in events] == ["A", "A", "B", "B"]
    assert [e["qty"] for e in events] == [10, 3, 2, 2]
    timestamps = [e["timestamp"] for e in events]
    assert timestamps == sorted(timestamps)


def test_failed_removal_appends_no_event():
    inv = Inventory()
    inv.add_item("A", "Apple", 0.5, 4)
    for bad_qty in (0, -1, 5, 10**6):
        with pytest.raises(ValueError):
            inv.remove_stock("A", bad_qty)
    with pytest.raises(ValueError):
        inv.remove_stock("MISSING", 1)
    assert len(inv.get_events()) == 1
    assert inv.get_item("A")["qty"] == 4


def test_get_events_is_a_copy():
    inv = Inventory()
    inv.add_item("A", "Apple", 0.5, 1)
    inv.get_events().clear()
    assert len(inv.get_events()) == 1
