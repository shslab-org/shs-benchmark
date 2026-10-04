"""Pricing helpers — shared rounding/tax logic extracted into helpers."""


def _subtotal(items):
    """Sum of price * qty over the given items."""
    total = 0
    for it in items:
        total += it["price"] * it["qty"]
    return total


def _apply_tax(amount):
    """Adds 10% sales tax."""
    return amount * 1.10


def _round_cents(x):
    """Round half-up to cents (works for negative values)."""
    scaled = x * 100
    return (scaled + 0.5) // 1 / 100 if scaled >= 0 else -((-scaled + 0.5) // 1) / 100


def retail_total(items):
    """items: list of dicts with 'price' and 'qty'. Adds 10% sales tax, rounds to 2 decimals."""
    return _round_cents(_apply_tax(_subtotal(items)))


def wholesale_total(items, min_qty=50):
    """Same math but 20% discount applied first, then 10% tax. Rounds half-up to cents."""
    subtotal = _subtotal(items)
    discounted = subtotal * 0.80 if sum(i["qty"] for i in items) >= min_qty else subtotal
    return _round_cents(_apply_tax(discounted))
