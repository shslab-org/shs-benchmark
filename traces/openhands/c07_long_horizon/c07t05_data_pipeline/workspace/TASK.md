Build and RUN a data pipeline over the dirty CSV in data/sales_raw.csv.

Columns: order_id,region,product,qty,unit_price
Known problems in the data:
- some qty values are 0/negative or not integers  -> drop those rows
- some unit_price values are empty or not floats  -> drop those rows
- region values are inconsistent case (e.g. " west", "WEST", "East") -> normalize to Title-case ("West")
- duplicate order_id rows -> keep the first occurrence only

Deliverables:
1. pipeline.py: reads the CSV, applies ALL cleaning rules, computes:
   - total_sales (sum of qty*unit_price over cleaned rows, rounded to 2)
   - sales_by_region (same rounding, per region)
   - sales_by_product
   - row counts: input_rows, cleaned_rows, dropped_rows
2. Run it: write report.json (this exact name, repo root or out/)
3. Do NOT modify data/sales_raw.csv
4. Verify your numbers by hand on a few rows before finishing.