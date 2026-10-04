# SHS Benchmark — 4-Agent Coding Benchmark

Structured, reproducible benchmark of four coding agents on the same 50 tasks, all powered by **Agnes AI `agnes-3.0-flash`** (OpenAI-compatible endpoint).

## Agents under test

| Agent | Version | Headless mode |
|---|---|---|
| SHS Code | v4.4.0 (commit 897b5d6, shslab-org/shs-code) | `SHSCode --max-steps N "<prompt>"` |
| OpenHands | 1.11.0 (openhands-ai, SDK 1.34.0) | SDK runner `harness/oh_run.py` |
| OpenCode | 1.18.34 (npm opencode-ai) | `opencode run -m agnes/agnes-3.0-flash` |
| Hermes Agent | git.8b66a51 (NousResearch/hermes-agent, 2026.9.24) | `hermes chat -q "<p>" -Q --max-turns N` |

## Structure

- `tasks/` — 10 categories × 5 tasks; each has `task.json` (prompt), `verify.py` (objective scorer, 20 pts), `baseline/` (fixture copied into each agent's workspace)
- `traces/<agent>/<category>/<task>/` — full per-run evidence: `prompt.txt`, `run.log` (stdout/stderr, timings, config), `workspace/` (agent's actual output files), `verification.json` (point-by-point checks), `result.json` (score)
- `harness/` — generators (recreate every task), adapters, stream runner, daemonizer
- `logs/` — stream logs + per-agent `*.jsonl` result streams
- `results.json`, `results.jsonl`, `task_results.jsonl` — machine-readable aggregates
- `FINAL_COMPARISON.md` — evidence-based final report
- `provider_switch/` — SHS Code Atria Dawn Preview provider-switch test (recorded separately, not part of the 1000 points)

## Scoring

Every task is scored 0–20 by its `verify.py` against the agent's workspace — objective checks only (hidden tests, behavioral contracts, structural requirements, git state). Identical prompts, baselines, step caps, and timeouts for all four agents. Raw traces are immutable: `result.json` is written once and never overwritten. Maximum: 1000 points per agent.

## Reproducibility

`harness/gen_tasks_*.py` regenerate all 50 tasks deterministically. Every verifier was self-tested against a golden solution and yields exactly 20/20 (see commit history).
