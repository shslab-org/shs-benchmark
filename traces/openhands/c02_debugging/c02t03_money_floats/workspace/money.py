"""Money handling using exact decimal arithmetic for currency precision."""

from decimal import Decimal, ROUND_HALF_UP

CENTS_IN_DOLLAR = 100


def _to_cents(value):
    """Convert a float/int/Decimal to an exact Decimal of cents.

    Floats are converted via repr to avoid binary representation errors
    (repr(0.1) -> '0.1', not 0.1000000000000000055...).
    """
    if isinstance(value, float):
        value = repr(value)
    return Decimal(value) * CENTS_IN_DOLLAR


def add_prices(a, b):
    """Add two prices given as floats of dollars, exact to the cent."""
    total_cents = int(_to_cents(a)) + int(_to_cents(b))
    return total_cents / CENTS_IN_DOLLAR


def apply_tax(amount, rate):
    """amount: float dollars, rate: e.g. 0.0725. Rounds half-up to the cent."""
    amount_cents = _to_cents(amount)
    rate_dec = Decimal(repr(rate)) if isinstance(rate, float) else Decimal(rate)
    exact = amount_cents * (1 + rate_dec)
    rounded = int(exact.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    return rounded / CENTS_IN_DOLLAR


def total_price(prices):
    """Sum a list of float dollar prices with exact cent precision."""
    total_cents = 0
    for p in prices:
        total_cents += int(_to_cents(p))
    return total_cents / CENTS_IN_DOLLAR


def format_usd(amount):
    """Format as USD string with exactly 2 decimals, half-up rounding."""
    exact = _to_cents(amount)
    rounded = int(exact.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    dollars = rounded // CENTS_IN_DOLLAR
    cents = rounded % CENTS_IN_DOLLAR
    return f"${dollars}.{cents:02d}"
