import csv
import json
import os
from collections import defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(ROOT, "data", "sales_raw.csv")


def normalize_region(value):
    region = value.strip()
    if not region:
        return ""
    return region.title()


def parse_qty(value):
    value = value.strip()
    if not value:
        return None
    try:
        f = float(value)
    except ValueError:
        return None
    if f != int(f) or f <= 0:
        return None
    return int(f)


def parse_price(value):
    value = value.strip()
    if not value:
        return None
    try:
        f = float(value)
    except ValueError:
        return None
    return f


def main():
    input_rows = 0
    cleaned_rows = 0
    dropped_rows = 0
    seen_order_ids = set()
    total_sales = 0.0
    sales_by_region = defaultdict(float)
    sales_by_product = defaultdict(float)

    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            input_rows += 1

            order_id = row["order_id"].strip()
            if order_id in seen_order_ids:
                dropped_rows += 1
                continue
            seen_order_ids.add(order_id)

            qty = parse_qty(row["qty"])
            price = parse_price(row["unit_price"])
            if qty is None or price is None:
                dropped_rows += 1
                continue

            region = normalize_region(row["region"])
            product = row["product"].strip()
            amount = qty * price
            total_sales += amount
            sales_by_region[region] += amount
            sales_by_product[product] += amount
            cleaned_rows += 1

    report = {
        "total_sales": round(total_sales, 2),
        "sales_by_region": {k: round(v, 2) for k, v in sorted(sales_by_region.items())},
        "sales_by_product": {k: round(v, 2) for k, v in sorted(sales_by_product.items())},
        "input_rows": input_rows,
        "cleaned_rows": cleaned_rows,
        "dropped_rows": dropped_rows,
    }

    out_path = os.path.join(ROOT, "report.json")
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)
        f.write("\n")

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
