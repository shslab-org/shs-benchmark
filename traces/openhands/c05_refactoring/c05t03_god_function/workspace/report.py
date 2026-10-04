"""Order line parsing and aggregation.

Public entry point: process_orders.
"""


def parse_line(line):
    """Parses one 'sku,qty,unit_price' line.

    Returns (sku, qty, price) for a valid line, or None if the line
    is invalid (wrong field count, bad numbers, qty <= 0, price < 0,
    or empty sku)."""
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


def parse_lines(raw_lines):
    """Parses every line; returns (valid_entries, invalid_count)."""
    valid = []
    invalid = 0
    for ln in raw_lines:
        parsed = parse_line(ln)
        if parsed is None:
            invalid += 1
        else:
            valid.append(parsed)
    return valid, invalid


def line_total(qty, price):
    """Total for one order line, with a 5% bulk discount when qty >= 10."""
    total = qty * price
    if qty >= 10:
        total *= 0.95
    return total


def aggregate(valid):
    """Aggregates parsed lines into (grand_total, by_sku totals)."""
    total = 0.0
    by_sku = {}
    for sku, q, p in valid:
        ltotal = line_total(q, p)
        total += ltotal
        by_sku[sku] = by_sku.get(sku, 0) + ltotal
    return total, by_sku


def process_orders(raw_lines):
    """Parses order lines 'sku,qty,unit_price', drops invalid lines,
    computes totals with 5% bulk discount when qty >= 10 per line,
    returns dict with keys: valid_count, invalid_count, total, by_sku."""
    valid, invalid = parse_lines(raw_lines)
    total, by_sku = aggregate(valid)
    return {"valid_count": len(valid), "invalid_count": invalid,
            "total": round(total, 2),
            "by_sku": {k: round(v, 2) for k, v in by_sku.items()}}
