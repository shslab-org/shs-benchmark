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


def test_event_log_add_appends_event():
    inv = Inventory()
    inv.add_item("SKU1", "Apple", 0.5, 10)
    events = inv.get_events()
    assert len(events) == 1
    ev = events[0]
    assert ev["action"] == "add"
    assert ev["sku"] == "SKU1"
    from datetime import datetime
    assert datetime.fromisoformat(ev["timestamp"]).isoformat() == ev["timestamp"]


def test_event_log_remove_appends_event():
    inv = Inventory()
    inv.add_item("SKU1", "Apple", 0.5, 10)
    inv.remove_stock("SKU1", 3)
    events = inv.get_events()
    assert len(events) == 2
    assert [e["action"] for e in events] == ["add", "remove"]
    assert events[1]["sku"] == "SKU1"
    assert events[1]["qty"] == 3


def test_event_log_chronological_and_failed_removes_do_not_log():
    inv = Inventory()
    inv.add_item("A", "Apple", 0.5, 10)
    inv.add_item("B", "Banana", 1.0, 2)
    inv.remove_stock("A", 2)
    inv.remove_stock("B", 1)
    assert [e["sku"] for e in inv.get_events()] == ["A", "B", "A", "B"]
    for call in (
        lambda: inv.remove_stock("NOPE", 1),
        lambda: inv.remove_stock("A", 0),
        lambda: inv.remove_stock("A", 9999),
    ):
        with pytest.raises(ValueError):
            call()
    assert len(inv.get_events()) == 4
