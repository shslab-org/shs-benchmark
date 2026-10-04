from cart import add_item, add_tagged


def test_add_item_isolated():
    c1 = add_item({"sku": "A", "price": 2})
    c2 = add_item({"sku": "B", "price": 3})
    assert c1 != c2, "separate calls must not share state"
    assert c1 == [{"sku": "A", "price": 2}]


def test_add_item_explicit_list_ok():
    mine = []
    add_item({"sku": "X"}, mine)
    add_item({"sku": "Y"}, mine)
    assert len(mine) == 2


def test_add_tagged_isolated():
    r1 = add_tagged({"sku": "A"})
    r2 = add_tagged({"sku": "B"})
    assert r1["tags"] == ["A"], "tags must not leak across calls"
    assert r2["tags"] == ["B"]
    assert r1["extra"] == {"last": "A"}
