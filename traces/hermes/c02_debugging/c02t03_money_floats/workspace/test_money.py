from money import add_prices, apply_tax, total_price, format_usd


def test_add_cents():
    assert add_prices(0.1, 0.2) == 0.3


def test_total_accumulation():
    prices = [0.1] * 10
    assert total_price(prices) == 1.0


def test_tax_rounds_to_cents():
    # 19.99 with 7.25% tax = 21.439775 -> must round half-up to 21.44
    assert apply_tax(19.99, 0.0725) == 21.44


def test_format_two_decimals():
    assert format_usd(21.439775) == "$21.44"


def test_total_mixed_cents():
    assert total_price([1.99, 2.49, 0.02]) == 4.5
