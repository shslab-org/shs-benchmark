#!/usr/bin/env python3
"""Generate a revenue report from data/orders.csv.

Writes report.txt with total revenue, revenue by product (desc),
revenue by region (alphabetical), and unique order count.
Reads the CSV; never modifies it.
"""
import csv
from pathlib import Path

BASE = Path(__file__).resolve().parent
ORDERS = BASE / "data" / "orders.csv"
REPORT = BASE / "report.txt"


def main() -> None:
    product_revenue: dict[str, float] = {}
    region_revenue: dict[str, float] = {}
    total = 0.0
    order_ids: set[str] = set()

    with ORDERS.open(newline="") as fh:
        for row in csv.DictReader(fh):
            qty = int(row["qty"])
            unit_price = float(row["unit_price"])
            revenue = qty * unit_price
            total += revenue
            order_ids.add(row["order_id"])
            product_revenue[row["product"]] = product_revenue.get(row["product"], 0.0) + revenue
            region_revenue[row["region"]] = region_revenue.get(row["region"], 0.0) + revenue

    products_sorted = sorted(product_revenue.items(), key=lambda kv: kv[1], reverse=True)
    regions_sorted = sorted(region_revenue.items())

    lines = [
        "=" * 60,
        "SALES REPORT",
        "=" * 60,
        "",
        f"Total revenue: {total:.2f}",
        "",
        "Revenue by product (descending):",
    ]
    for name, amount in products_sorted:
        lines.append(f"  {name:<12} {amount:,.2f}")

    lines += [
        "",
        "Revenue by region (alphabetical):",
    ]
    for name, amount in regions_sorted:
        lines.append(f"  {name:<12} {amount:,.2f}")

    lines += [
        "",
        f"Unique orders: {len(order_ids)}",
        "",
        "=" * 60,
    ]

    REPORT.write_text("\n".join(lines) + "\n")
    print(f"Wrote {REPORT}")


if __name__ == "__main__":
    main()
