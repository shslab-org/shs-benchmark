"""Pricing helpers — shared rounding/tax helpers, public functions below."""


def _round_cents(x):
    """Round x to the nearest cent (2 decimal places, half-up in magnitude)."""
    scaled = x * 100
    rounded = (scaled + 0.5) // 1 / 100 if scaled >= 0 else -((-scaled + 0.5) // 1) / 100
    return rounded


def _apply_tax(subtotal):
    """Add 10% sales tax to subtotal, then round half-up to cents."""
    return _round_cents(subtotal * 1.10)


def retail_total(items):
    """items: list of dicts with 'price' and 'qty'. Adds 10% sales tax, rounds to 2 decimals."""
    subtotal = 0
    for it in items:
        subtotal += it["price"] * it["qty"]
    return _apply_tax(subtotal)


def wholesale_total(items, min_qty=50):
    """Same math but 20% discount applied first, then 10% tax. Rounds half-up to cents."""
    subtotal = 0
    for it in items:
        subtotal += it["price"] * it["qty"]
    discounted = subtotal * 0.80 if sum(i["qty"] for i in items) >= min_qty else subtotal
    return _apply_tax(discounted)
