"""Money handling. Currency arithmetic is done in exact integer cents."""

from decimal import Decimal, ROUND_HALF_UP

CENTS_IN_DOLLAR = 100


def _to_cents(value):
    """Convert a dollar amount (float) to exact integer cents, half-up."""
    return int(
        (Decimal(str(value)) * CENTS_IN_DOLLAR).to_integral_value(
            rounding=ROUND_HALF_UP
        )
    )


def add_prices(a, b):
    """Add two prices given as floats of dollars, exactly at cent precision."""
    return float(Decimal(_to_cents(a) + _to_cents(b)) / CENTS_IN_DOLLAR)


def apply_tax(amount, rate):
    """amount: float dollars, rate: e.g. 0.0725. Rounded half-up to the cent."""
    taxed = Decimal(str(amount)) * (Decimal(str(rate)) + 1)
    cents = taxed.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return float(cents)


def total_price(prices):
    """Sum a list of float dollar prices with exact cent precision."""
    return float(Decimal(sum(_to_cents(p) for p in prices)) / CENTS_IN_DOLLAR)


def format_usd(amount):
    """Format as USD string with exactly 2 decimals, half-up rounding."""
    cents = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"${cents:.2f}"
