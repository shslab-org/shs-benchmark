#!/usr/bin/env python3
"""Clean dirty sales CSV and emit report.json.

Rules:
- drop rows whose qty is 0/negative or not an integer
- drop rows whose unit_price is empty or not a float
- normalize region to Title-case
- keep only the first occurrence of a duplicate order_id
"""

import csv
import json

INPUT = "data/sales_raw.csv"
OUTPUT = "report.json"


def main():
    input_rows = 0
    seen_orders = set()
    total_sales = 0.0
    by_region = {}
    by_product = {}
    cleaned_rows = 0

    with open(INPUT, newline="") as f:
        for row in csv.DictReader(f):
            input_rows += 1
            order_id = row["order_id"].strip()

            qty_raw = (row.get("qty") or "").strip()
            price_raw = (row.get("unit_price") or "").strip()

            # qty must be a positive integer
            try:
                qty = int(qty_raw)
            except ValueError:
                continue
            if qty <= 0:
                continue

            # price must be a float
            try:
                price = float(price_raw)
            except ValueError:
                continue

            # duplicate order_id -> keep first
            if order_id in seen_orders:
                continue
            seen_orders.add(order_id)

            region = (row.get("region") or "").strip().title()
            product = (row.get("product") or "").strip()
            amount = qty * price

            cleaned_rows += 1
            total_sales += amount
            by_region[region] = by_region.get(region, 0.0) + amount
            by_product[product] = by_product.get(product, 0.0) + amount

    report = {
        "total_sales": round(total_sales, 2),
        "sales_by_region": {k: round(v, 2) for k, v in sorted(by_region.items())},
        "sales_by_product": {k: round(v, 2) for k, v in sorted(by_product.items())},
        "input_rows": input_rows,
        "cleaned_rows": cleaned_rows,
        "dropped_rows": input_rows - cleaned_rows,
    }

    with open(OUTPUT, "w") as f:
        json.dump(report, f, indent=2)

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
