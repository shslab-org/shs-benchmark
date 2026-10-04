"""Money handling. Fixed: work in integer cents for exact precision."""

from decimal import Decimal, ROUND_HALF_UP

CENTS_IN_DOLLAR = 100


def _to_cents(x):
    """Convert a dollar value (float or Decimal) to exact integer cents (half-up)."""
    return int(Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) * 100)


def add_prices(a, b):
    """Add two prices given as floats of dollars. Exact cent precision."""
    return (_to_cents(a) + _to_cents(b)) / 100.0


def apply_tax(amount, rate):
    """amount: float dollars, rate: e.g. 0.0725. Exact cents, half-up rounding."""
    return _to_cents(amount * (1 + rate)) / 100.0


def total_price(prices):
    """Sum a list of float dollar prices with exact cent precision."""
    total_cents = 0
    for p in prices:
        total_cents += _to_cents(p)
    return total_cents / 100.0


def format_usd(amount):
    """Format as USD string with exactly 2 decimals, half-up rounding."""
    cents = _to_cents(amount)
    return f"${cents // 100}.{cents % 100:02d}"
