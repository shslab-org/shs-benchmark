#!/usr/bin/env python3
"""Generate a revenue report from data/orders.csv.

Produces report.txt containing:
  - total revenue across all orders (sum of qty*unit_price, 2 decimals)
  - revenue by product, sorted descending (with amounts)
  - revenue by region (alphabetical)
  - number of unique orders
"""

import csv
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INPUT_CSV = BASE_DIR / "data" / "orders.csv"
OUTPUT_TXT = BASE_DIR / "report.txt"


def money(d: Decimal) -> str:
    """Format a Decimal as a 2-decimal money string."""
    return f"{d:.2f}"


def main() -> None:
    revenue_by_product: dict[str, Decimal] = defaultdict(lambda: Decimal(0))
    revenue_by_region: dict[str, Decimal] = defaultdict(lambda: Decimal(0))
    order_ids: set[str] = set()
    total_revenue = Decimal(0)

    with INPUT_CSV.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            qty = int(row["qty"])
            unit_price = Decimal(row["unit_price"])
            revenue = qty * unit_price

            total_revenue += revenue
            revenue_by_product[row["product"]] += revenue
            revenue_by_region[row["region"]] += revenue
            order_ids.add(row["order_id"])

    lines = []
    lines.append("=" * 40)
    lines.append("SALES REPORT")
    lines.append("=" * 40)
    lines.append("")
    lines.append(f"Total revenue: {money(total_revenue)}")
    lines.append(f"Unique orders: {len(order_ids)}")
    lines.append("")
    lines.append("-" * 40)
    lines.append("Revenue by product (descending)")
    lines.append("-" * 40)
    for product in sorted(revenue_by_product, key=revenue_by_product.get, reverse=True):
        lines.append(f"  {product:<12} {money(revenue_by_product[product])}")
    lines.append("")
    lines.append("-" * 40)
    lines.append("Revenue by region (alphabetical)")
    lines.append("-" * 40)
    for region in sorted(revenue_by_region):
        lines.append(f"  {region:<12} {money(revenue_by_region[region])}")
    lines.append("")

    OUTPUT_TXT.write_text("\n".join(lines))
    print(f"Wrote {OUTPUT_TXT}")


if __name__ == "__main__":
    main()
