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
    assert Inventory().get_events() == []


def test_events_recorded_chronologically():
    inv = Inventory()
    inv.add_item("A", "Apple", 0.5, 10)
    inv.add_item("B", "Banana", 1.0, 3)
    inv.remove_stock("A", 2)
    inv.add_item("A", "Apple", 0.5, 1)
    events = inv.get_events()
    assert [e["action"] for e in events] == ["add", "add", "remove", "add"]
    assert [e["sku"] for e in events] == ["A", "B", "A", "A"]


def test_event_timestamps_iso8601():
    inv = Inventory()
    inv.add_item("X", "Widget", 9.99, 1)
    from datetime import datetime
    ts = inv.get_events()[0]["timestamp"]
    parsed = datetime.fromisoformat(ts)
    assert parsed.tzinfo is not None


def test_remove_stock_errors():
    inv = Inventory()
    inv.add_item("S", "Soda", 1.5, 4)
    with pytest.raises(ValueError):
        inv.remove_stock("MISSING", 1)
    with pytest.raises(ValueError):
        inv.remove_stock("S", 0)
    with pytest.raises(ValueError):
        inv.remove_stock("S", -1)
    with pytest.raises(ValueError):
        inv.remove_stock("S", 5)
    assert inv.get_item("S")["qty"] == 4


def test_event_log_append_only():
    inv = Inventory()
    inv.add_item("K", "Kit", 2.0, 10)
    events = inv.get_events()
    assert len(events) == 1
    assert events[0]["sku"] == "K"
    assert "timestamp" in events[0]
    assert events[0]["action"] == "add"
