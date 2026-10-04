#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c07t05"
checks = []
pipe = vlib.find_file(ws, "pipeline.py") or vlib.find_file(ws, "run_pipeline.py")
checks.append({"name": "pipeline.py exists", "ok": bool(pipe), "points": 2, "detail": str(pipe)})
rep = None
for cand in ("report.json", "out/report.json", "output/report.json", "data/report.json"):
    p = os.path.join(ws, cand)
    if os.path.exists(p):
        rep = p
        break
checks.append({"name": "report.json produced", "ok": bool(rep), "points": 4, "detail": str(rep)})
if rep:
    try:
        r = json.load(open(rep))
        blob = json.dumps(r).lower()
        has_counts = ("input_rows" in blob or "cleaned_rows" in blob or "dropped_rows" in blob
                      or ("input" in blob and "cleaned" in blob))
        checks.append({"name": "row counts present (input/cleaned/dropped)", "ok": has_counts, "points": 4,
                       "detail": blob[:200]})
        checks.append({"name": "aggregates present (total + by_region + by_product)",
                       "ok": "total" in blob and "region" in blob and "product" in blob, "points": 5})
        # expected cleaned rows: 1001,1002,1004,1006,1008,1009,1010 = 7 rows (1011 has no region, 1012 no price)
        n_cleaned = r.get("cleaned_rows") or (r.get("row_counts") or {}).get("cleaned_rows")
        # AMENDED (uniform for all agents): spec did not explicitly require
        # dropping rows with an EMPTY region; both 7 (drop) and 8 (keep, as
        # its own "" region group) are spec-compliant readings.
        checks.append({"name": "cleaned_rows == 7 or 8 (exact computation)", "ok": n_cleaned in (7, 8),
                       "points": 2, "detail": "got: " + str(n_cleaned)})
        # total: 2*9.99 + 1*24.50 + 3*5.00 + 4*9.99 + 2*5.00 + 1*5.00 + 12*1.50 = 19.98+24.5+15+39.96+10+5+18 = 132.44
        total = r.get("total_sales")
        ok_total = isinstance(total, (int, float)) and min(abs(total - 132.44), abs(total - 142.44)) < 0.05
        checks.append({"name": "total_sales == 132.44 or 142.44 (+-0.05)", "ok": ok_total, "points": 2,
                       "detail": "got: " + str(total)})
    except Exception as e:
        checks.append({"name": "report parseable JSON", "ok": False, "points": 15, "detail": str(e)[:150]})
src_dirty = os.path.join(ws, "data", "sales_raw.csv")
ok_untouched = os.path.exists(src_dirty) and "not_a_price" in open(src_dirty).read()
checks.append({"name": "input data untouched", "ok": ok_untouched, "points": 1})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
