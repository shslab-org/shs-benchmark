"""Order report: parse, price, aggregate (refactored)."""


def parse_line(line):
    """Parse one 'sku,qty,unit_price' line.

    Returns (sku, qty, price) when the line is valid, else None.
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
    return sku, q, p


def parse_all(raw_lines):
    """Split raw lines into (valid_orders, invalid_count)."""
    valid = []
    invalid = 0
    for ln in raw_lines:
        order = parse_line(ln)
        if order is None:
            invalid += 1
        else:
            valid.append(order)
    return valid, invalid


def compute_line_total(qty, price):
    """Line total: qty * price, with a 5% bulk discount when qty >= 10."""
    line_total = qty * price
    if qty >= 10:
        line_total *= 0.95
    return line_total


def aggregate(valid_orders):
    """Aggregate line totals into (grand_total, by_sku)."""
    total = 0.0
    by_sku = {}
    for sku, q, p in valid_orders:
        line_total = compute_line_total(q, p)
        total += line_total
        by_sku[sku] = by_sku.get(sku, 0) + line_total
    return total, by_sku


def process_orders(raw_lines):
    """Parses order lines 'sku,qty,unit_price', drops invalid lines,
    computes totals with 5% bulk discount when qty >= 10 per line,
    returns dict with keys: valid_count, invalid_count, total, by_sku."""
    valid, invalid = parse_all(raw_lines)
    total, by_sku = aggregate(valid)
    return {"valid_count": len(valid), "invalid_count": invalid,
            "total": round(total, 2),
            "by_sku": {k: round(v, 2) for k, v in by_sku.items()}}
