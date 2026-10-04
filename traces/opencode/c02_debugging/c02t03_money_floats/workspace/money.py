"""Money handling using exact decimal cents."""

from decimal import Decimal, ROUND_HALF_UP

CENTS_IN_DOLLAR = 100


def _dollars_to_cents(value):
    return int((Decimal(str(value)) * CENTS_IN_DOLLAR).quantize(Decimal(1)))


def add_prices(a, b):
    """Add two prices given as floats of dollars with exact cent precision."""
    return (_dollars_to_cents(a) + _dollars_to_cents(b)) / CENTS_IN_DOLLAR


def apply_tax(amount, rate):
    """amount: float dollars, rate: e.g. 0.0725. Rounds half-up to the cent."""
    exact = Decimal(str(amount)) * (Decimal(1) + Decimal(str(rate)))
    rounded = exact.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return float(rounded)


def total_price(prices):
    """Sum a list of float dollar prices with exact cent precision."""
    cents = sum(_dollars_to_cents(p) for p in prices)
    return cents / CENTS_IN_DOLLAR


def format_usd(amount):
    """Format as USD string with exactly 2 decimals, half-up rounding."""
    rounded = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"${rounded:.2f}"
