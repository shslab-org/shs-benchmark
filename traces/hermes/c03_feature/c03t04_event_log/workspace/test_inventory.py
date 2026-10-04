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


def test_events_empty_initially():
    inv = Inventory()
    assert inv.get_events() == []


def test_add_appends_event():
    inv = Inventory()
    inv.add_item("SKU1", "Apple", 0.5, 10)
    events = inv.get_events()
    assert len(events) == 1
    e = events[0]
    assert e["action"] == "add"
    assert e["sku"] == "SKU1"
    assert e["qty"] == 10
    # ISO-8601 timestamp parses back to a datetime
    from datetime import datetime
    assert datetime.fromisoformat(e["ts"])


def test_remove_stock_appends_event():
    inv = Inventory()
    inv.add_item("SKU1", "Apple", 0.5, 10)
    inv.remove_stock("SKU1", 3)
    events = inv.get_events()
    assert len(events) == 2
    assert [e["action"] for e in events] == ["add", "remove"]
    assert events[1]["sku"] == "SKU1"
    assert events[1]["qty"] == 3
    assert inv.get_item("SKU1")["qty"] == 7


def test_remove_stock_raises_no_event():
    inv = Inventory()
    inv.add_item("SKU1", "Apple", 0.5, 10)
    with pytest.raises(ValueError):
        inv.remove_stock("NOPE", 1)
    with pytest.raises(ValueError):
        inv.remove_stock("SKU1", 0)
    with pytest.raises(ValueError):
        inv.remove_stock("SKU1", 11)
    # failed removals don't log events
    assert len(inv.get_events()) == 1


def test_events_chronological_and_append_only():
    inv = Inventory()
    inv.add_item("A", "Apple", 0.5, 5)
    inv.add_item("B", "Banana", 1.0, 2)
    inv.remove_stock("A", 1)
    events = inv.get_events()
    assert [e["sku"] for e in events] == ["A", "B", "A"]
    # get_events returns a copy: mutating it doesn't touch the log
    events.append({"action": "tamper", "sku": "X", "ts": ""})
    assert len(inv.get_events()) == 3
