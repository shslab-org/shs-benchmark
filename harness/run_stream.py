#!/usr/bin/env python3
"""Stream runner: executes every task of the benchmark for ONE agent.

Usage: run_stream.py <agent> [category_filter]

For each task (categories c01..c10, tasks 1..5):
  1. skip if result already exists (immutability — raw results never rewritten)
  2. fresh workspace: delete + copy baseline
  3. write prompt1.txt (+prompt2.txt for memory tasks)
  4. launch agent via agents.py adapter (timeout + step caps identical across agents)
  5. run task verify.py -> verification.json
  6. write result.json into traces/<agent>/<task>/ and append to logs/<agent>.jsonl

Provider errors (429/5xx/timeouts) are flagged provider_error=true and the task
is retried ONCE; agent failures are never retried.
"""
import datetime, json, os, shutil, subprocess, sys, time, traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WS_ROOT = "/home/z/my-project/bench_ws"  # OUTSIDE the git repo (agent tools resolve to git roots)
sys.path.insert(0, os.path.join(ROOT, "harness"))
import agents as A

AGENT = sys.argv[1]
ONLY_CAT = sys.argv[2] if len(sys.argv) > 2 else None
TASKS = os.path.join(ROOT, "tasks")
TRACES = os.path.join(ROOT, "traces", AGENT)
LOGFILE = os.path.join(ROOT, "logs", f"stream_{AGENT}.log")


def log(msg):
    line = f"[{datetime.datetime.now().isoformat(timespec='seconds')}] {msg}"
    os.makedirs(os.path.dirname(LOGFILE), exist_ok=True)
    with open(LOGFILE, "a") as f:
        f.write(line + "\n")
    print(line, flush=True)


def list_tasks():
    out = []
    for cat in sorted(os.listdir(TASKS)):
        cdir = os.path.join(TASKS, cat)
        if not os.path.isdir(cdir):
            continue
        for tid in sorted(os.listdir(cdir)):
            tdir = os.path.join(cdir, tid)
            if os.path.isdir(tdir) and os.path.exists(os.path.join(tdir, "task.json")):
                out.append((cat, tid, tdir))
    return out


def run_task(cat, tid, tdir):
    spec = json.load(open(os.path.join(tdir, "task.json")))
    trace = os.path.join(TRACES, cat, tid)
    if os.path.exists(os.path.join(trace, "result.json")):
        log(f"SKIP {tid} (already has result.json — immutability)")
        return json.load(open(os.path.join(trace, "result.json")))

    ws = os.path.join(WS_ROOT, AGENT, cat, tid)
    shutil.rmtree(ws, ignore_errors=True)
    os.makedirs(trace, exist_ok=True)
    os.makedirs(ws, exist_ok=True)
    baseline = os.path.join(tdir, "baseline")
    if os.path.isdir(baseline):
        shutil.copytree(baseline, ws, dirs_exist_ok=True)
    if spec.get("git_baseline"):
        env = dict(os.environ)
        for k, v in (("GIT_AUTHOR_NAME", "baseline"), ("GIT_AUTHOR_EMAIL", "baseline@bench"),
                     ("GIT_COMMITTER_NAME", "baseline"), ("GIT_COMMITTER_EMAIL", "baseline@bench")):
            env.setdefault(k, v)
        subprocess.run(["git", "init", "-q"], cwd=ws, check=True)
        subprocess.run(["git", "add", "-A"], cwd=ws, check=True)
        subprocess.run(["git", "commit", "-qm", "Initial commit"], cwd=ws, check=True, env=env)

    with open(os.path.join(trace, "prompt1.txt"), "w") as f:
        f.write(spec["prompt"])
    with open(os.path.join(os.path.dirname(ws), "prompt1.txt"), "w") as f:
        f.write(spec["prompt"])
    prompts = [spec["prompt"]]
    if spec.get("prompt2"):
        with open(os.path.join(trace, "prompt2.txt"), "w") as f:
            f.write(spec["prompt2"])
        with open(os.path.join(os.path.dirname(ws), "prompt2.txt"), "w") as f:
            f.write(spec["prompt2"])
        prompts.append(spec["prompt2"])

    steps, timeout = A.caps_for(cat)
    started = datetime.datetime.now()
    log(f"RUN {tid} agent={AGENT} steps={steps} timeout={timeout}s turns={len(prompts)}")
    attempt, meta, provider_error = 0, None, False
    while attempt < 3:
        attempt += 1
        try:
            meta = A.RUNNERS[AGENT](ws, prompts, steps, timeout)
        except subprocess.TimeoutExpired:
            meta = {"rc": 124, "stdout": "", "stderr": f"agent timeout after {timeout}s",
                    "duration_s": timeout, "session_id": "", "version": "?"}
        except Exception as e:
            meta = {"rc": 1, "stdout": "", "stderr": f"runner crash: {e}\n{traceback.format_exc()[-1500:]}",
                    "duration_s": 0, "session_id": "", "version": "?"}
        blob = json.dumps(meta)
        provider_error = ("429" in blob or "rate limit" in blob.lower() or "RateLimit" in blob
                          or meta.get("rc") == 124 or "overloaded" in blob.lower()
                          or "LAUNCH_ERROR" in blob or "Connection" in blob)
        if not provider_error or attempt >= 3:
            break
        log(f"RETRY {tid} (provider/timeout issue, attempt {attempt})")
        time.sleep(30 * attempt)

    with open(os.path.join(trace, "run.log"), "w") as f:
        f.write(f"agent: {AGENT}\ncategory: {cat}\ntask: {tid}\nstarted: {started.isoformat()}\n"
                f"model: agnes-3.0-flash\nprovider: Agnes AI (https://apihub.agnes-ai.com/v1)\n"
                f"version: {meta.get('version','?')}\nsession_id: {meta.get('session_id','')}\n"
                f"rc: {meta.get('rc')}\nduration_s: {meta.get('duration_s')}\n"
                f"steps_cap: {steps}\ntimeout_cap: {timeout}\nattempts: {attempt}\n"
                f"provider_error_flag: {provider_error}\n\n=== STDOUT ===\n{meta.get('stdout','')}\n\n=== STDERR ===\n{meta.get('stderr','')}\n")
    shutil.copy(os.path.join(trace, "prompt1.txt"), os.path.join(trace, "prompt.txt"))

    # ---- verification (identical script for every agent) ----
    verify = os.path.join(tdir, "verify.py")
    ver = {"points": 0, "max_points": 20, "passed": False, "checks": [], "error": None}
    try:
        r = subprocess.run([sys.executable, verify, ws, AGENT], capture_output=True, text=True, timeout=300, cwd=tdir)
        vout = r.stdout or ""
        try:
            ver = json.loads(vout[vout.index("{"):vout.rindex("}") + 1])
        except Exception:
            ver = {"points": 0, "max_points": 20, "passed": False, "checks": [],
                   "error": f"verify crash rc={r.returncode}: {(r.stderr or vout)[-800:]}"}
    except subprocess.TimeoutExpired:
        ver = {"points": 0, "max_points": 20, "passed": False, "checks": [], "error": "verify timeout"}

    result = {
        "agent": AGENT, "category": cat, "task": tid,
        "title": spec.get("title", tid),
        "started": started.isoformat(),
        "duration_s": meta.get("duration_s"),
        "model": "agnes-3.0-flash", "provider": "agnes-ai",
        "agent_version": meta.get("version", "?"),
        "session_id": meta.get("session_id", ""),
        "rc": meta.get("rc"),
        "provider_error_retry": provider_error and attempt > 1,
        "points": ver.get("points", 0), "max_points": ver.get("max_points", 20),
        "passed": ver.get("passed", False), "checks": ver.get("checks", []),
        "verify_error": ver.get("error"),
        "timestamp": datetime.datetime.now().isoformat(),
    }
    with open(os.path.join(trace, "verification.json"), "w") as f:
        json.dump(ver, f, indent=2)
    with open(os.path.join(trace, "result.json"), "w") as f:
        json.dump(result, f, indent=2)
    shutil.copytree(ws, os.path.join(trace, "workspace"), dirs_exist_ok=True)
    # git-task evidence: bundle full history into one file, then strip .git
    # (nested repos cannot be committed to the benchmark repo)
    gitdir = os.path.join(trace, "workspace", ".git")
    if os.path.exists(gitdir):
        subprocess.run(["git", "-C", os.path.join(trace, "workspace"), "bundle",
                        "create", os.path.join(trace, "workspace_repo.bundle"), "--all"],
                       capture_output=True, timeout=60)
        shutil.rmtree(gitdir, ignore_errors=True)
    with open(os.path.join(ROOT, "logs", f"{AGENT}.jsonl"), "a") as f:
        f.write(json.dumps(result) + "\n")
    log(f"DONE {tid} score={result['points']}/{result['max_points']} passed={result['passed']} dur={result['duration_s']}s")
    return result


def main():
    tasks = list_tasks()
    if ONLY_CAT:
        tasks = [t for t in tasks if t[0] == ONLY_CAT]
    log(f"=== stream start agent={AGENT} tasks={len(tasks)} ===")
    scores = []
    for cat, tid, tdir in tasks:
        try:
            scores.append(run_task(cat, tid, tdir))
        except Exception as e:
            log(f"FATAL {tid}: {e}\n{traceback.format_exc()[-1200:]}")
    total = sum(s["points"] for s in scores)
    log(f"=== stream end agent={AGENT} subtotal={total}/{len(scores)*20} ===")


if __name__ == "__main__":
    main()
