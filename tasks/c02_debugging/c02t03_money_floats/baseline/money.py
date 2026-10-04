"""Money handling. BUG: binary float arithmetic corrupts currency totals."""

CENTS_IN_DOLLAR = 100


def add_prices(a, b):
    """Add two prices given as floats of dollars. BUG: naive float add."""
    return a + b


def apply_tax(amount, rate):
    """amount: float dollars, rate: e.g. 0.0725. BUG: loses cents precision."""
    return amount * (1 + rate)


def total_price(prices):
    """Sum a list of float dollar prices. BUG: accumulates float error."""
    total = 0.0
    for p in prices:
        total += p
    return total


def format_usd(amount):
    """Format as USD string with exactly 2 decimals, half-up rounding."""
    return f"${amount:.2f}"
