#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c10t04"
checks = []
gen = vlib.find_file(ws, "generate_report.py") or vlib.find_file(ws, "report_gen.py") or vlib.find_file(ws, "generate.py")
checks.append({"name": "report generator exists", "ok": bool(gen), "points": 4, "detail": str(gen)})
rep = None
for cand in ("report.txt", "out/report.txt", "output/report.txt"):
    p = os.path.join(ws, cand)
    if os.path.exists(p):
        rep = p
        break
checks.append({"name": "report.txt produced", "ok": bool(rep), "points": 4, "detail": str(rep)})
if rep:
    txt = open(rep).read()
    low = txt.lower()
    import re as _re
    m = _re.search(r"total revenue[^\d]*(\d+[.,]\d+)", txt, _re.I)
    ok_total = bool(m) and abs(float(m.group(1).replace(",", ".")) - 313.00) < 0.05
    checks.append({"name": "total revenue == 313.00 (+-0.05)", "ok": ok_total,
                   "points": 5, "detail": (m.group(1) if m else txt[:120])})
    checks.append({"name": "top product by revenue named (Gadget)", "ok": "gadget" in low, "points": 3})
    checks.append({"name": "region breakdown present (north/south/east/west)", "ok": all(r in low for r in ("north", "south", "east", "west")), "points": 3})
    checks.append({"name": "order count = 8", "ok": "8" in txt, "points": 1})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
