from shop.pricing import final_price


def test_pricing_bulk():
    assert final_price(10, 1.0, bulk_threshold=10, bulk_discount=0.9) == 9.0


def test_pricing_normal():
    assert final_price(5, 2.0, bulk_threshold=10, bulk_discount=0.9) == 10.0
