# Sales Data Pipeline — Verification Notes

## Source
`data/sales_raw.csv` (13 data rows, unchanged — md5 836cc58094328ab03986e9cce2e3526a)

## Cleaning applied
1. **qty** must be a positive integer → dropped 1003 (0), 1005 (-2)
2. **unit_price** must parse as float → dropped 1007 ("not_a_price"), 1012 (empty)
3. **region** → strip + Title-case
4. **duplicate order_id** → keep first, dropped duplicate 1001

Result: 8 kept, 5 dropped, 13 input.

## Final numbers (report.json)
- total_sales: **142.44**
- sales_by_region: West 59.94, East 42.50, North 20.00, South 10.00, "" 10.00
- sales_by_product: Widget 77.94, Gadget 34.50, Gizmo 30.00

## Hand-check on a few rows
| order | region | product | qty | price | line | kept? |
|-------|--------|---------|----|-------|------|-------|
| 1001 | West | Widget | 2 | 9.99 | 19.98 | ✓ |
| 1006 | "west " | Widget | 4 | 9.99 | 39.96 | ✓ (→ West) |
| 1010 | East | Widget | 12 | 1.50 | 18.00 | ✓ |
| 1011 | (empty) | Gadget | 1 | 10.00 | 10.00 | ✓ (region not a drop rule) |

Widget total = 19.98 + 39.96 + 18.00 = **77.94** ✓
Gadget = 24.50 (1002) + 10.00 (1011) = **34.50** ✓
Gizmo = 15.00 (1004) + 10.00 (1008) + 5.00 (1009) = **30.00** ✓
Grand total = 77.94 + 34.50 + 30.00 = **142.44** ✓

Note: region "" (row 1011) is empty but NOT a listed drop condition, so it is
retained per spec. All three aggregation totals cross-sum to 142.44.

## Verification method
Independent re-implementation (no reuse of pipeline.py logic) reproduced
report.json exactly (JSON deep-equality = True). Pipeline self-asserts
cleaned_rows + dropped_rows == input_rows.
