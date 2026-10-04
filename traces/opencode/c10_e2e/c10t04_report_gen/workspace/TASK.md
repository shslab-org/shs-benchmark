Build a report generator and RUN it.

Input: data/orders.csv (columns: order_id,customer,product,qty,unit_price,region)

Deliverables:
1. `generate_report.py` producing `report.txt` containing:
   - total revenue across all orders (sum qty*unit_price, 2 decimals)
   - revenue by product, sorted descending (with amounts)
   - revenue by region (alphabetical)
   - number of unique orders
   - a clearly readable layout with headers
2. Run it and verify the numbers by hand:
   expected total revenue = 3*25 + 10*4.5 + 2*4.5 + 5*12 + 1*25 + 4*12 + 6*4.5 + 2*12
3. Do not modify data/orders.csv.