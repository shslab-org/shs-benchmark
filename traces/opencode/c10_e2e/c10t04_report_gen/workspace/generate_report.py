import csv
from collections import defaultdict

CSV_PATH = "data/orders.csv"
REPORT_PATH = "report.txt"


def main():
    total_revenue = 0.0
    product_revenue = defaultdict(float)
    region_revenue = defaultdict(float)
    order_ids = set()

    with open(CSV_PATH, newline="") as f:
        for row in csv.DictReader(f):
            qty = float(row["qty"])
            price = float(row["unit_price"])
            revenue = qty * price
            total_revenue += revenue
            product_revenue[row["product"]] += revenue
            region_revenue[row["region"]] += revenue
            order_ids.add(row["order_id"])

    lines = []
    lines.append("=" * 40)
    lines.append("SALES REPORT")
    lines.append("=" * 40)
    lines.append("")
    lines.append("Total revenue: %.2f" % total_revenue)
    lines.append("")
    lines.append("Revenue by product (descending):")
    for product, amount in sorted(product_revenue.items(), key=lambda x: -x[1]):
        lines.append("  %-15s %.2f" % (product, amount))
    lines.append("")
    lines.append("Revenue by region (alphabetical):")
    for region in sorted(region_revenue):
        lines.append("  %-15s %.2f" % (region, region_revenue[region]))
    lines.append("")
    lines.append("Number of unique orders: %d" % len(order_ids))
    lines.append("")

    with open(REPORT_PATH, "w") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
