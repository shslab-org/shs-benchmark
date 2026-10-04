#!/usr/bin/env python3
"""Data pipeline for data/sales_raw.csv.

Cleaning rules (per TASK.md):
  1. qty must be a positive integer (drop 0 / negative / non-integer)
  2. unit_price must be a parseable float (drop empty / non-float)
  3. region: strip whitespace + normalize to Title case
  4. duplicate order_id: keep first occurrence only

Output: report.json (repo root) with:
  total_sales, sales_by_region, sales_by_product,
  input_rows, cleaned_rows, dropped_rows
"""

import csv
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE, "data", "sales_raw.csv")
REPORT_PATH = os.path.join(BASE, "report.json")


def is_positive_int(s: str) -> bool:
    """True if s is a clean positive integer (no 0, no negatives, no floats)."""
    s = s.strip()
    if not s:
        return False
    # Must match an integer literal: optional sign, digits only.
    neg = s.startswith("-")
    digits = s.lstrip("-") if neg else s
    if not digits.isdigit():
        return False
    value = int(digits)
    return not neg and value > 0


def to_float(s: str):
    """Return float(s) or None if not parseable / empty."""
    s = s.strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def normalize_region(s: str) -> str:
    """Strip whitespace and Title-case the region (e.g. ' west ' -> 'West')."""
    return s.strip().title()


def clean(csv_path: str):
    input_rows = 0
    cleaned_rows = 0
    dropped_rows = 0
    seen_order_ids = set()

    total_sales = 0.0
    by_region = {}
    by_product = {}

    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            input_rows += 1

            oid = (row.get("order_id") or "").strip()
            region = normalize_region(row.get("region") or "")
            product = (row.get("product") or "").strip()
            qty_raw = row.get("qty") or ""
            price_raw = row.get("unit_price") or ""

            # Rule 1: qty must be a positive integer
            if not is_positive_int(qty_raw):
                dropped_rows += 1
                continue
            qty = int(qty_raw.strip())

            # Rule 2: unit_price must be a parseable float
            price = to_float(price_raw)
            if price is None:
                dropped_rows += 1
                continue

            # Rule 4: duplicate order_id -> keep first only
            if oid in seen_order_ids:
                dropped_rows += 1
                continue
            seen_order_ids.add(oid)

            # Row is clean: aggregate
            line = round(qty * price, 2)
            total_sales = round(total_sales + line, 2)
            by_region[region] = round(by_region.get(region, 0.0) + line, 2)
            by_product[product] = round(by_product.get(product, 0.0) + line, 2)
            cleaned_rows += 1

    report = {
        "total_sales": round(total_sales, 2),
        "sales_by_region": {k: round(v, 2) for k, v in sorted(by_region.items())},
        "sales_by_product": {k: round(v, 2) for k, v in sorted(by_product.items())},
        "input_rows": input_rows,
        "cleaned_rows": cleaned_rows,
        "dropped_rows": dropped_rows,
    }
    return report


def main():
    report = clean(CSV_PATH)
    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2)
    print("Wrote", REPORT_PATH)
    print(json.dumps(report, indent=2))
    # Sanity: cleaned + dropped == input
    assert report["cleaned_rows"] + report["dropped_rows"] == report["input_rows"], \
        "row counts do not add up"
    print("OK: cleaned_rows + dropped_rows == input_rows")


if __name__ == "__main__":
    main()
