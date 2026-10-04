#!/usr/bin/env python3
"""Data pipeline over data/sales_raw.csv.

Cleaning rules:
- drop rows where qty is not a positive integer (0/negative/non-integer)
- drop rows where unit_price is empty or not a float
- normalize region to Title case (strip, then .title())
- duplicate order_id: keep first occurrence only

Output: report.json with total_sales, sales_by_region, sales_by_product,
and row counts (input_rows, cleaned_rows, dropped_rows).
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data" / "sales_raw.csv"
OUTPUT = ROOT / "report.json"


def clean_qty(raw: str) -> int | None:
    """Return positive integer qty, or None if invalid."""
    s = raw.strip()
    try:
        val = int(s)
    except ValueError:
        return None
    if val <= 0:
        return None
    return val


def clean_price(raw: str) -> float | None:
    """Return unit_price as float, or None if empty/non-numeric."""
    s = raw.strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def main() -> None:
    input_rows = 0
    cleaned = []  # (order_id, region, product, qty, price)

    with INPUT.open(newline="") as f:
        for row in csv.DictReader(f):
            input_rows += 1
            qty = clean_qty(row.get("qty", ""))
            if qty is None:
                continue
            price = clean_price(row.get("unit_price", ""))
            if price is None:
                continue
            region = (row.get("region") or "").strip().title()
            product = (row.get("product") or "").strip()
            order_id = (row.get("order_id") or "").strip()
            cleaned.append((order_id, region, product, qty, price))

    # Deduplicate order_id: keep first occurrence only.
    seen = set()
    kept = []
    for rec in cleaned:
        if rec[0] in seen:
            continue
        seen.add(rec[0])
        kept.append(rec)

    total_sales = round(sum(q * p for _, _, _, q, p in kept), 2)

    by_region: dict[str, float] = {}
    by_product: dict[str, float] = {}
    for _, region, product, qty, price in kept:
        line = round(qty * price, 2)
        by_region[region] = round(by_region.get(region, 0.0) + line, 2)
        by_product[product] = round(by_product.get(product, 0.0) + line, 2)

    report = {
        "total_sales": total_sales,
        "sales_by_region": {k: by_region[k] for k in sorted(by_region)},
        "sales_by_product": {k: by_product[k] for k in sorted(by_product)},
        "input_rows": input_rows,
        "cleaned_rows": len(kept),
        "dropped_rows": input_rows - len(kept),
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
