"""Order reporting helpers.

`process_orders` is the public entry point; the parsing, discount,
and aggregation concerns are split into focused helpers so that the
public behavior stays exactly the same.
"""


def parse_line(line):
    """Parse one 'sku,qty,unit_price' line.

    Returns a (sku, qty, price) tuple for a valid line, or None if the
    line is malformed, has a non-positive quantity, a negative price,
    or an empty SKU.
    """
    parts = line.strip().split(",")
    if len(parts) != 3:
        return None
    sku, qty, price = parts[0].strip(), parts[1].strip(), parts[2].strip()
    try:
        q = int(qty)
        p = float(price)
    except ValueError:
        return None
    if q <= 0 or p < 0 or not sku:
        return None
    return (sku, q, p)


def parse_all(raw_lines):
    """Parse every line, splitting it into (valid, invalid_count)."""
    valid = []
    invalid = 0
    for line in raw_lines:
        parsed = parse_line(line)
        if parsed is None:
            invalid += 1
        else:
            valid.append(parsed)
    return valid, invalid


def compute_line_total(qty, price):
    """Total for one order line, applying a 5% bulk discount
    when qty >= 10."""
    line_total = qty * price
    if qty >= 10:
        line_total *= 0.95
    return line_total


def aggregate(valid, invalid_count):
    """Aggregate per-line totals into the report dict.

    Keeps the exact same key set and 2-decimal rounding as before.
    """
    total = 0.0
    by_sku = {}
    for sku, q, p in valid:
        line_total = compute_line_total(q, p)
        total += line_total
        by_sku[sku] = by_sku.get(sku, 0) + line_total
    return {"valid_count": len(valid), "invalid_count": invalid_count,
            "total": round(total, 2),
            "by_sku": {k: round(v, 2) for k, v in by_sku.items()}}


def process_orders(raw_lines):
    """Parses order lines 'sku,qty,unit_price', drops invalid lines,
    computes totals with 5% bulk discount when qty >= 10 per line,
    returns dict with keys: valid_count, invalid_count, total, by_sku."""
    valid, invalid = parse_all(raw_lines)
    return aggregate(valid, invalid)
