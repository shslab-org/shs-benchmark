#!/usr/bin/env python3
"""Recovery sweep: re-run tasks whose failure was provider-caused (429/timeout),
after stream contention has ended. Original failed result is preserved as
result_provider_failed.json (raw traces stay immutable); the task is then
re-executed normally (fresh run, new result.json).

Usage: recovery_sweep.py <agent> [min_points_threshold=10]
"""
import json, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS = os.path.join(ROOT, "logs")

agent = sys.argv[1]
thresh = int(sys.argv[2]) if len(sys.argv) > 2 else 10

logf = os.path.join(LOGS, f"{agent}.jsonl")
seen, requeue = set(), []
for line in open(logf):
    try:
        d = json.loads(line)
    except Exception:
        continue
    key = d["task"] + "|" + d["category"]
    if key in seen:
        continue
    seen.add(key)
    if d.get("provider_error_retry") and d["points"] <= thresh:
        requeue.append(d)

print(f"[sweep] {agent}: {len(requeue)} provider-errored tasks to re-run")
for d in requeue:
    trace = os.path.join(ROOT, "traces", agent, d["category"], d["task"])
    rp = os.path.join(trace, "result.json")
    if os.path.exists(rp):
        shutil.copy(rp, os.path.join(trace, "result_provider_failed.json"))
        os.remove(rp)
    print(f"[sweep] requeue {d['task']} (was {d['points']}/20, rc={d.get('rc')})")

# re-run sequentially via the normal stream (skips tasks with existing results)
subprocess.run([sys.executable, os.path.join(ROOT, "harness", "run_stream.py"), agent], check=False)
