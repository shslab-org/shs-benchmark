from cart import Cart


def test_add_with_explicit_qty():
    cart = Cart()
    cart.add("a", 3)
    assert cart.items() == {"a": 3}


def test_add_default_qty_is_one():
    cart = Cart()
    cart.add("a")
    assert cart.items() == {"a": 1}


def test_add_increments_existing():
    cart = Cart()
    cart.add("a")
    cart.add("a", 2)
    assert cart.items() == {"a": 3}


def test_items_is_snapshot():
    cart = Cart()
    cart.add("a")
    snapshot = cart.items()
    snapshot["a"] = 99
    snapshot["b"] = 1
    assert cart.items() == {"a": 1}
    assert "b" not in cart.items()


def test_remove_existing():
    cart = Cart()
    cart.add("a")
    cart.add("b")
    cart.remove("a")
    assert cart.items() == {"b": 1}


def test_remove_missing_raises_value_error():
    cart = Cart()
    cart.add("a")
    try:
        cart.remove("nope")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")


def test_total_sums_known_skus():
    cart = Cart()
    cart.add("a", 2)
    cart.add("b", 5)
    prices = {"a": 1.5, "b": 0.25}
    assert cart.total(prices) == 4.25


def test_total_with_empty_cart():
    assert Cart().total({"a": 1.0}) == 0.0


def test_total_unknown_sku_raises_key_error():
    cart = Cart()
    cart.add("a")
    cart.add("b")
    try:
        cart.total({"a": 1.0})
    except KeyError:
        pass
    else:
        raise AssertionError("expected KeyError")
