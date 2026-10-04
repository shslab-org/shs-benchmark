from shop.cart import Cart


def test_cart_add_remove():
    c = Cart()
    c.add("apple", 2)
    c.add("pear", 1)
    c.remove("apple")
    assert c.items() == {"pear": 1}


def test_cart_quantity_update():
    c = Cart()
    c.add("apple", 2)
    c.add("apple", 3)
    assert c.items() == {"apple": 5}
