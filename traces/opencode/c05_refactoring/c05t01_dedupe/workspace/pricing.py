"""Pricing helpers — shared rounding/tax logic extracted into helpers."""


def _subtotal(items):
    subtotal = 0
    for it in items:
        subtotal += it["price"] * it["qty"]
    return subtotal


def _round_half_up_cents(x):
    # round half-up to cents
    scaled = x * 100
    return (scaled + 0.5) // 1 / 100 if scaled >= 0 else -((-scaled + 0.5) // 1) / 100


def _apply_tax(base):
    return _round_half_up_cents(base * 1.10)


def retail_total(items):
    """items: list of dicts with 'price' and 'qty'. Adds 10% sales tax, rounds to 2 decimals."""
    return _apply_tax(_subtotal(items))


def wholesale_total(items, min_qty=50):
    """Same math but 20% discount applied first, then 10% tax. Rounds half-up to cents."""
    base = _subtotal(items)
    discounted = base * 0.80 if sum(i["qty"] for i in items) >= min_qty else base
    return _apply_tax(discounted)
