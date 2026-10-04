"""Pricing helpers — duplication to be removed (refactor task)."""


def retail_total(items):
    """items: list of dicts with 'price' and 'qty'. Adds 10% sales tax, rounds to 2 decimals."""
    subtotal = 0
    for it in items:
        subtotal += it["price"] * it["qty"]
    with_tax = subtotal * 1.10
    # round half-up to cents
    scaled = with_tax * 100
    rounded = (scaled + 0.5) // 1 / 100 if scaled >= 0 else -((-scaled + 0.5) // 1) / 100
    return rounded


def wholesale_total(items, min_qty=50):
    """Same math but 20% discount applied first, then 10% tax. Rounds half-up to cents."""
    subtotal = 0
    for it in items:
        subtotal += it["price"] * it["qty"]
    discounted = subtotal * 0.80 if sum(i["qty"] for i in items) >= min_qty else subtotal
    with_tax = discounted * 1.10
    scaled = with_tax * 100
    rounded = (scaled + 0.5) // 1 / 100 if scaled >= 0 else -((-scaled + 0.5) // 1) / 100
    return rounded
