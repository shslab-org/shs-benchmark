import pytest

from cart import Cart


class TestAdd:
    def test_add_default_qty(self):
        cart = Cart()
        cart.add("sku-1")
        assert cart.items() == {"sku-1": 1}

    def test_add_explicit_qty(self):
        cart = Cart()
        cart.add("sku-1", 5)
        assert cart.items() == {"sku-1": 5}

    def test_add_same_sku_twice_accumulates(self):
        cart = Cart()
        cart.add("sku-1")
        cart.add("sku-1", 4)
        assert cart.items() == {"sku-1": 5}

    def test_add_multiple_skus(self):
        cart = Cart()
        cart.add("sku-1", 2)
        cart.add("sku-2", 3)
        assert cart.items() == {"sku-1": 2, "sku-2": 3}


class TestItems:
    def test_items_empty_cart(self):
        assert Cart().items() == {}

    def test_items_returns_snapshot(self):
        cart = Cart()
        cart.add("sku-1", 2)
        snapshot = cart.items()
        snapshot["sku-1"] = 99
        assert cart.items() == {"sku-1": 2}

    def test_items_multiple_adds_reflect_state(self):
        cart = Cart()
        cart.add("sku-1")
        cart.add("sku-2")
        assert cart.items() == {"sku-1": 1, "sku-2": 1}


class TestRemove:
    def test_remove_existing_sku(self):
        cart = Cart()
        cart.add("sku-1", 3)
        cart.remove("sku-1")
        assert cart.items() == {}

    def test_remove_one_of_multiple_skus(self):
        cart = Cart()
        cart.add("sku-1")
        cart.add("sku-2")
        cart.remove("sku-1")
        assert cart.items() == {"sku-2": 1}

    def test_remove_missing_sku_raises_value_error(self):
        cart = Cart()
        with pytest.raises(ValueError):
            cart.remove("never-added")

    def test_remove_from_empty_cart_raises_value_error(self):
        cart = Cart()
        with pytest.raises(ValueError):
            cart.remove("sku-1")


class TestTotal:
    def test_total_empty_cart(self):
        assert Cart().total({"sku-1": 10.0}) == 0.0

    def test_total_single_sku(self):
        cart = Cart()
        cart.add("sku-1", 3)
        assert cart.total({"sku-1": 2.5}) == 7.5

    def test_total_multiple_skus(self):
        cart = Cart()
        cart.add("sku-1", 2)
        cart.add("sku-2", 4)
        total = cart.total({"sku-1": 1.0, "sku-2": 3.0})
        assert total == pytest.approx(14.0)

    def test_total_ignores_skus_not_in_cart(self):
        cart = Cart()
        cart.add("sku-1", 2)
        assert cart.total({"sku-1": 1.0, "sku-2": 99.0}) == 2.0

    def test_total_unknown_sku_in_cart_raises_key_error(self):
        cart = Cart()
        cart.add("sku-1")
        with pytest.raises(KeyError):
            cart.total({"other": 1.0})
