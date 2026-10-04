import json

from shop.backup import backup_json
from shop.cart import Cart


def test_backup_json_writes_items(tmp_path):
    path = tmp_path / "cart.json"
    c = Cart()
    c.add("apple", 2)
    c.add("pear", 1)

    written = backup_json(c, path)

    assert written == {"apple": 2, "pear": 1}
    data = json.loads(path.read_text())
    assert data == {"apple": 2, "pear": 1}


def test_backup_json_empty_cart(tmp_path):
    path = tmp_path / "empty.json"
    c = Cart()

    written = backup_json(c, path)

    assert written == {}
    data = json.loads(path.read_text())
    assert data == {}


def test_backup_json_indentation(tmp_path):
    path = tmp_path / "cart.json"
    c = Cart()
    c.add("apple", 1)

    backup_json(c, path)

    text = path.read_text()
    # indent=2 produces two leading spaces before each key
    assert '\n  "apple": 1\n' in text


def test_backup_does_not_mutate_cart(tmp_path):
    path = tmp_path / "cart.json"
    c = Cart()
    c.add("apple", 1)

    backup_json(c, path)

    assert c.items() == {"apple": 1}
