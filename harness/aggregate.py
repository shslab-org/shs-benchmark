#!/usr/bin/env python3
"""Aggregate all task results into results.json / results.jsonl / task_results.jsonl
and print category tables. Run after all streams finish."""
import json, os
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS = os.path.join(ROOT, "logs")
AGENTS = ["shs-code", "openhands", "opencode", "hermes"]
CATS = ["c01_code_generation", "c02_debugging", "c03_feature", "c04_testing_qa",
        "c05_refactoring", "c06_git_engineering", "c07_long_horizon", "c08_memory",
        "c09_multi_agent", "c10_e2e"]
TITLES = {
    "c01_code_generation": "Code Generation",
    "c02_debugging": "Debugging & Bug Fixing",
    "c03_feature": "Feature Implementation",
    "c04_testing_qa": "Testing & QA",
    "c05_refactoring": "Refactoring & Code Quality",
    "c06_git_engineering": "Repository / Git / GitHub Engineering",
    "c07_long_horizon": "Long-Horizon Autonomous Task",
    "c08_memory": "Memory & Context Retention",
    "c09_multi_agent": "Multi-Agent / Parallel Engineering",
    "c10_e2e": "End-to-End Software Engineering",
}

results = defaultdict(dict)   # agent -> task -> result
for a in AGENTS:
    p = os.path.join(LOGS, f"{a}.jsonl")
    if not os.path.exists(p):
        continue
    for line in open(p):
        try:
            d = json.loads(line)
            results[a][d["task"]] = d
        except Exception:
            pass

# task_results.jsonl — one line per task execution
with open(os.path.join(ROOT, "task_results.jsonl"), "w") as f:
    for a in AGENTS:
        for cat in CATS:
            for tid, r in sorted(results[a].items()):
                if r["category"] == cat:
                    f.write(json.dumps(r) + "\n")

# results.jsonl — one line per agent summary
agent_summaries = {}
for a in AGENTS:
    per_cat = {}
    for cat in CATS:
        pts = sum(r["points"] for tid, r in results[a].items() if r["category"] == cat)
        done = sum(1 for tid, r in results[a].items() if r["category"] == cat)
        per_cat[cat] = {"points": pts, "max": done * 20, "tasks_done": done}
    total = sum(v["points"] for v in per_cat.values())
    done_all = sum(v["tasks_done"] for v in per_cat.values())
    passed = sum(1 for r in results[a].values() if r.get("passed"))
    agent_summaries[a] = {
        "agent": a,
        "total_points": total, "max_points": done_all * 20,
        "percentage": round(100 * total / (done_all * 20), 1) if done_all else 0.0,
        "normalized_out_of_1000": round(1000 * total / (done_all * 20)) if done_all else 0,
        "tasks_completed": done_all, "tasks_total": 50,
        "tasks_passed_full": passed,
        "completion_rate": round(100 * done_all / 50, 1),
        "per_category": per_cat,
    }
    with open(os.path.join(ROOT, "results.jsonl"), "a") as f:
        f.write(json.dumps(agent_summaries[a]) + "\n")

with open(os.path.join(ROOT, "results.json"), "w") as f:
    json.dump({
        "benchmark": "shs-benchmark (4 agents x 10 categories x 5 tasks x 20 pts)",
        "model": "agnes-3.0-flash via Agnes AI",
        "generated": __import__("datetime").datetime.now().isoformat(),
        "agents": agent_summaries,
    }, f, indent=2)

# console table
print(f"{'Category':<42}" + "".join(f"{a[:14]:>16}" for a in AGENTS))
for cat in CATS:
    row = f"{TITLES[cat]:<42}"
    for a in AGENTS:
        v = agent_summaries[a]["per_category"].get(cat, {"points": 0, "max": 0})
        row += f"{v['points']:>6}/{v['max']:<4}" + " " * 6
    print(row)
print("-" * 100)
row = f"{'TOTAL (normalized /1000)':<42}"
for a in AGENTS:
    s = agent_summaries[a]
    row += f"{s['total_points']:>6}/{s['max_points']:<4} ({s['normalized_out_of_1000']})"
print(row)
