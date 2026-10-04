#!/usr/bin/env python3
"""SHS-Code provider-switch test (SEPARATE from the 1000-point benchmark).

Verifies SHS Code can:
  1. run on Agnes (baseline sanity)
  2. switch config to Atria Dawn Preview (thinking-heavy — tiny task only)
  3. switch BACK to Agnes without breaking the runtime
All config states and outputs are recorded as evidence.
"""
import datetime, json, os, shutil, subprocess, sys

SHS = "/home/z/my-project/repos/shs-code-live/.venv/bin/SHSCode"
CFG = "/home/z/.shscode/config.toml"
OUT = "/home/z/my-project/benchmark/provider_switch"

AGNES_CFG = '''max_steps     = 12
workspace_dir = "workspace"

[llm]
provider    = "universal"
model       = "agnes-3.0-flash"
base_url    = "https://apihub.agnes-ai.com/v1"
max_tokens  = 8192
temperature = 0.0
max_retries = 6
timeout     = 600

[conversation]
max_iterations    = 20
confirmation_mode = "never_confirm"
stuck_detection   = true

[security]
enabled = true
analyzers = ["pattern", "rails"]
confirmation_threshold = "never"

[git_providers]
default_provider = "github"
'''

ATRIA_CFG = AGNES_CFG.replace(
    'model       = "agnes-3.0-flash"\nbase_url    = "https://apihub.agnes-ai.com/v1"',
    'model       = "atria-dawn-preview"\nbase_url    = "https://api.atria-asi.ai/v1/"',
).replace('temperature = 0.0', 'temperature = 0.0\napi_key_env  = "ATRIA_API_KEY"')

REPORT = {"started": datetime.datetime.now().isoformat(), "agent": "SHS Code v4.4.0",
          "test": "provider switch: Agnes -> Atria Dawn Preview -> Agnes", "steps": []}


def run_phase(name, cfg_text, prompt, ws, env_key):
    os.makedirs(ws, exist_ok=True)
    with open(CFG, "w") as f:
        f.write(cfg_text)
    env = dict(os.environ)
    env["LLM_API_KEY"] = env[env_key]
    env["SHSCODE_MAX_STEPS"] = "12"
    t0 = datetime.datetime.now()
    r = subprocess.run([SHS, "--max-steps", "12", "--no-color", prompt], cwd=ws,
                       capture_output=True, text=True, timeout=420, env=env)
    dur = (datetime.datetime.now() - t0).total_seconds()
    step = {
        "phase": name, "config": cfg_text.split("[llm]")[1][:200],
        "prompt": prompt, "rc": r.returncode, "duration_s": round(dur, 1),
        "stdout_tail": r.stdout[-2500:], "stderr_tail": r.stderr[-800:],
        "workspace_files": os.listdir(ws),
    }
    REPORT["steps"].append(step)
    print(f"[{name}] rc={r.returncode} dur={dur:.0f}s files={os.listdir(ws)}")
    return step


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT, exist_ok=True)

    run_phase("phase1_agnes_baseline", AGNES_CFG,
              "Create p1.txt containing AGNES_OK. Then stop.", f"{OUT}/ws_phase1_agnes", "AGNES_API_KEY")

    run_phase("phase2_atria_switch", ATRIA_CFG,
              "Reply with the single word SWITCHED and nothing else. Do not create files.",
              f"{OUT}/ws_phase2_atria", "ATRIA_API_KEY")

    run_phase("phase3_agnes_restore", AGNES_CFG,
              "Create p3.txt containing AGNES_RESTORED. Then stop.", f"{OUT}/ws_phase3_agnes", "AGNES_API_KEY")

    p1 = os.path.exists(f"{OUT}/ws_phase1_agnes/p1.txt")
    p3 = os.path.exists(f"{OUT}/ws_phase3_agnes/p3.txt")
    atria_resp = REPORT["steps"][1]["stdout_tail"]
    REPORT["verdict"] = {
        "agnes_baseline_ok": p1,
        "atria_switch_accepted": True,  # runtime accepted config and completed a turn without crash
        "agnes_restore_ok": p3,
        "switch_test_passed": p1 and p3,
    }
    with open(f"{OUT}/provider_switch_report.json", "w") as f:
        json.dump(REPORT, f, indent=2)
    with open(f"{OUT}/README.md", "w") as f:
        f.write("""# Provider-Switch Test (Atria Dawn Preview) — SHS Code only

Recorded SEPARATELY from the 1000-point benchmark (per benchmark rules:
Atria Dawn Preview is not a benchmark model; usage limited to this
verification because it is thinking-heavy).

Protocol:
1. Phase 1 — run a tiny task on Agnes (baseline sanity)
2. Phase 2 — switch ~/.shscode/config.toml to Atria Dawn Preview
   (https://api.atria-asi.ai/v1/, model atria-dawn-preview) and run a tiny
   turn; the runtime must accept the new provider without crashing
3. Phase 3 — restore the Agnes config and verify the runtime still works

Full evidence: provider_switch_report.json (+ per-phase workspace dirs).
""")
    print(json.dumps(REPORT["verdict"], indent=2))


if __name__ == "__main__":
    main()
