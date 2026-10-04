"""God function to split (refactor task)."""


def process_orders(raw_lines):
    """Parses order lines 'sku,qty,unit_price', drops invalid lines,
    computes totals with 5% bulk discount when qty >= 10 per line,
    returns dict with keys: valid_count, invalid_count, total, by_sku."""
    valid = []
    invalid = 0
    for ln in raw_lines:
        parts = ln.strip().split(",")
        if len(parts) != 3:
            invalid += 1
            continue
        sku, qty, price = parts[0].strip(), parts[1].strip(), parts[2].strip()
        try:
            q = int(qty)
            p = float(price)
        except ValueError:
            invalid += 1
            continue
        if q <= 0 or p < 0 or not sku:
            invalid += 1
            continue
        valid.append((sku, q, p))
    total = 0.0
    by_sku = {}
    for sku, q, p in valid:
        line_total = q * p
        if q >= 10:
            line_total *= 0.95
        total += line_total
        by_sku[sku] = by_sku.get(sku, 0) + line_total
    return {"valid_count": len(valid), "invalid_count": invalid,
            "total": round(total, 2),
            "by_sku": {k: round(v, 2) for k, v in by_sku.items()}}
