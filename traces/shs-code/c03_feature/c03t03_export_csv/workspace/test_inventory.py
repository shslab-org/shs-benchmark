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
def test_export_csv_header_and_rows():
    inv = Inventory()
    inv.add_item("B", "Banana", 1.0, 2)
    inv.add_item("A", "Apple", 0.5, 1)
    out = inv.export_csv()
    lines = out.split("\n")
    assert lines[0] == "sku,name,price,qty"
    # order matches list_items() (sorted by name): Apple first
    assert lines[1] == "A,Apple,0.5,1"
    assert lines[2] == "B,Banana,1.0,2"
    assert len(lines) == 3


def test_export_csv_empty():
    inv = Inventory()
    assert inv.export_csv() == "sku,name,price,qty\n"

def test_export_csv_order_matches_list_items_for_many_items():
    inv = Inventory()
    inv.add_item("Z", "Zeta", 3.0, 1)
    inv.add_item("A", "Alpha", 1.0, 5)
    inv.add_item("M", "Mu", 2.0, 2)
    out = inv.export_csv()
    lines = out.split("\n")
    assert lines[0] == "sku,name,price,qty"
    # names in data rows must follow list_items() order (sorted by name)
    expected_names = [i["name"] for i in inv.list_items()]
    got_names = [line.split(",")[1] for line in lines[1:]]
    assert got_names == expected_names == ["Alpha", "Mu", "Zeta"]


def test_export_csv_row_values_match_list_items_values():
    inv = Inventory()
    inv.add_item("A", "Alpha", 1.5, 4)
    inv.add_item("B", "Beta", 2.5, 7)
    out = inv.export_csv()
    lines = out.split("\n")
    assert lines[0] == "sku,name,price,qty"
    data_rows = [line.split(",") for line in lines[1:]]
    list_items = inv.list_items()
    assert len(data_rows) == len(list_items) == 2
    for parts, item in zip(data_rows, list_items):
        assert parts[1] == item["name"]
        assert float(parts[2]) == item["price"]
        assert int(parts[3]) == item["qty"]

