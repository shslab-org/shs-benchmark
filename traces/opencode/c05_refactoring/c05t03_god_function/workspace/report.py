"""Refactored order processing (split from god function)."""


def parse_line(line):
    """Parses a single order line 'sku,qty,unit_price'.
    Returns (sku, qty, price) or None if the line is invalid."""
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


def compute_line_total(qty, price):
    """Computes a line total with 5% bulk discount when qty >= 10."""
    line_total = qty * price
    if qty >= 10:
        line_total *= 0.95
    return line_total


def aggregate(valid_lines):
    """Aggregates totals and per-SKU sums for valid lines."""
    total = 0.0
    by_sku = {}
    for sku, q, p in valid_lines:
        line_total = compute_line_total(q, p)
        total += line_total
        by_sku[sku] = by_sku.get(sku, 0) + line_total
    return {"total": round(total, 2),
            "by_sku": {k: round(v, 2) for k, v in by_sku.items()}}


def process_orders(raw_lines):
    """Parses order lines 'sku,qty,unit_price', drops invalid lines,
    computes totals with 5% bulk discount when qty >= 10 per line,
    returns dict with keys: valid_count, invalid_count, total, by_sku."""
    valid = []
    invalid = 0
    for ln in raw_lines:
        parsed = parse_line(ln)
        if parsed is None:
            invalid += 1
            continue
        valid.append(parsed)
    result = aggregate(valid)
    result["valid_count"] = len(valid)
    result["invalid_count"] = invalid
    return result
