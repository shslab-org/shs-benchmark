"""Agent adapters: launch each coding agent headlessly for one task.

Every adapter receives: workspace dir, prompt text (or two prompts for
memory tasks), step cap, timeout. It must return a dict:
  {rc, stdout, stderr, duration_s, session_id, extra}
No adapter may modify prompts or fix outputs — pure pass-through.
"""
import json, os, re, subprocess, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHS = "/home/z/my-project/repos/shs-code-live/.venv/bin/SHSCode"
OH_PY = "/home/z/my-project/repos/openhands-venv/bin/python"
OH_RUN = os.path.join(ROOT, "harness", "oh_run.py")
OPENCODE = "/home/z/.npm-global/bin/opencode"
HERMES = "/home/z/my-project/repos/hermes-agent/.venv/bin/hermes"

AGENTS = ["shs-code", "openhands", "opencode", "hermes"]


def _caps(category):
    """Iteration cap + timeout per category (identical for all agents)."""
    big = category in ("c07_long_horizon", "c10_e2e")
    steps = 45 if big else (25 if category == "c08_memory" else 30)
    timeout = 540 if big else (330 if category == "c08_memory" else 420)
    return steps, timeout


def run_shs_code(ws, prompts, steps, timeout):
    sid = "bench-" + os.path.basename(ws)
    outs = []
    t0 = time.time()
    for i, p in enumerate(prompts):
        cmd = [SHS, "--session", sid, "--max-steps", str(steps), "--no-color", p]
        if i > 0:
            cmd.insert(2, "--continue")
        r = subprocess.run(cmd, cwd=ws, capture_output=True, text=True, timeout=timeout)
        outs.append(f"--- TURN {i+1} rc={r.returncode} ---\n{r.stdout[-6000:]}\n[stderr]\n{r.stderr[-2000:]}")
    return {"rc": 0, "stdout": "\n".join(outs), "stderr": "", "duration_s": round(time.time() - t0, 1),
            "session_id": sid, "version": "v4.4.0 (897b5d6)"}


def run_openhands(ws, prompts, steps, timeout):
    t0 = time.time()
    p1 = os.path.join(ws, "..", "prompt1.txt")
    with open(p1, "w") as f:
        f.write(prompts[0])
    cmd = [OH_PY, OH_RUN, "--task-dir", ws, "--prompt-file", p1, "--max-iterations", str(steps)]
    if len(prompts) > 1:
        p2 = os.path.join(ws, "..", "prompt2.txt")
        with open(p2, "w") as f:
            f.write(prompts[1])
        cmd += ["--prompt-file2", p2]
    r = subprocess.run(cmd, cwd=ws, capture_output=True, text=True, timeout=timeout)
    meta = {}
    mp = os.path.join(ws, "agent_meta.json")
    if os.path.exists(mp):
        meta = json.load(open(mp))
    out = open(os.path.join(ws, "agent_output.txt")).read() if os.path.exists(os.path.join(ws, "agent_output.txt")) else ""
    return {"rc": r.returncode, "stdout": (out or "")[-6000:], "stderr": r.stderr[-2000:],
            "duration_s": meta.get("duration_s", round(time.time() - t0, 1)),
            "session_id": meta.get("conversation_id", ""), "version": "1.11.0 (sdk 1.34.0)",
            "tokens": meta.get("tokens"), "status": meta.get("status")}


def run_opencode(ws, prompts, steps, timeout):
    outs, session_id = [], None
    t0 = time.time()
    for i, p in enumerate(prompts):
        if i == 0:
            cmd = [OPENCODE, "run", "-m", "agnes/agnes-3.0-flash", "--format", "json", p]
        else:
            cmd = [OPENCODE, "run", "-m", "agnes/agnes-3.0-flash", "-s", session_id, p]
        try:
            r = subprocess.run(cmd, cwd=ws, capture_output=True, text=True, timeout=timeout)
            raw = r.stdout
            if i == 0:
                # extract sessionID from first JSON event line
                m = re.search(r'"sessionID":"([0-9a-f-]+)"', raw)
                session_id = m.group(1) if m else None
                # also grab human-readable text parts
                texts = re.findall(r'"type":"text","text":"((?:[^"\\]|\\.)*)"', raw)
                outs.append("--- TURN 1 ---\n" + (json.loads('"' + texts[-1] + '"') if texts else raw[-3000:]))
            else:
                outs.append(f"--- TURN {i+1} ---\n" + raw[-3000:])
        except subprocess.TimeoutExpired:
            outs.append(f"--- TURN {i+1} TIMEOUT after {timeout}s ---")
            return {"rc": 124, "stdout": "\n".join(outs), "stderr": "timeout", "duration_s": round(time.time() - t0, 1),
                    "session_id": session_id, "version": "1.18.34"}
    return {"rc": 0, "stdout": "\n".join(outs), "stderr": "", "duration_s": round(time.time() - t0, 1),
            "session_id": session_id, "version": "1.18.34"}


def run_hermes(ws, prompts, steps, timeout):
    outs, session_id = [], None
    t0 = time.time()
    for i, p in enumerate(prompts):
        cmd = [HERMES, "chat", "-q", p, "-Q", "--max-turns", str(steps), "--in", ws]
        if i > 0 and session_id:
            cmd += ["--resume", session_id, "--no-restore-cwd"]
        try:
            r = subprocess.run(cmd, cwd=ws, capture_output=True, text=True, timeout=timeout)
            combined = (r.stdout or "") + "\n" + (r.stderr or "")
            m = re.search(r"session_id:\s*(\S+)", combined)
            if m and not session_id:
                session_id = m.group(1)
            outs.append(f"--- TURN {i+1} ---\n{combined[-5000:]}")
        except subprocess.TimeoutExpired:
            outs.append(f"--- TURN {i+1} TIMEOUT after {timeout}s ---")
            return {"rc": 124, "stdout": "\n".join(outs), "stderr": "timeout", "duration_s": round(time.time() - t0, 1),
                    "session_id": session_id, "version": "git.8b66a51"}
    return {"rc": 0, "stdout": "\n".join(outs), "stderr": "", "duration_s": round(time.time() - t0, 1),
            "session_id": session_id, "version": "git.8b66a51 (2026.9.24)"}


RUNNERS = {
    "shs-code": run_shs_code,
    "openhands": run_openhands,
    "opencode": run_opencode,
    "hermes": run_hermes,
}


def caps_for(category):
    return _caps(category)
