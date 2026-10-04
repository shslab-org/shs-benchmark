import csv
import os

BASE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE, "data", "orders.csv")
OUT_PATH = os.path.join(BASE, "report.txt")


def main():
    total_revenue = 0.0
    revenue_by_product = {}
    revenue_by_region = {}
    orders = set()

    with open(CSV_PATH, newline="") as f:
        for row in csv.DictReader(f):
            qty = float(row["qty"])
            price = float(row["unit_price"])
            revenue = qty * price
            total_revenue += revenue
            revenue_by_product[row["product"]] = revenue_by_product.get(row["product"], 0.0) + revenue
            revenue_by_region[row["region"]] = revenue_by_region.get(row["region"], 0.0) + revenue
            orders.add(row["order_id"])

    lines = []
    lines.append("=" * 40)
    lines.append("SALES REPORT")
    lines.append("=" * 40)
    lines.append("")
    lines.append(f"Total revenue: {total_revenue:.2f}")
    lines.append(f"Number of unique orders: {len(orders)}")
    lines.append("")
    lines.append("Revenue by product (descending):")
    for product, amount in sorted(revenue_by_product.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"  {product}: {amount:.2f}")
    lines.append("")
    lines.append("Revenue by region (alphabetical):")
    for region, amount in sorted(revenue_by_region.items()):
        lines.append(f"  {region}: {amount:.2f}")
    lines.append("")

    with open(OUT_PATH, "w") as f:
        f.write("\n".join(lines))

    print("\n".join(lines))
    print(f"Report written to {OUT_PATH}")


if __name__ == "__main__":
    main()
