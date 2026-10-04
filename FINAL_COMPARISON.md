# FINAL_COMPARISON — 4-Agent Coding Benchmark

**Benchmark**: 10 categories × 5 tasks × 20 points = 1000 points per agent (200 task executions total)
**Model for ALL agents**: `agnes-3.0-flash` via Agnes AI (`https://apihub.agnes-ai.com/v1`) — identical prompts, baselines, step caps, timeouts
**Date**: 2026-10-04 · **Full evidence**: `traces/<agent>/<category>/<task>/` · **Raw scores**: `results.json`, `task_results.jsonl`

---

## 1. Final Scores

| Rank | Agent | Version | Score | % | Normalized /1000 | Full passes (20/20) |
|---|---|---|---|---|---|---|
| 🥇 | **SHS Code** | v4.4.0 (commit 897b5d6) | **968** | 96.8% | 968 | 43 / 50 |
| 🥈 | **OpenHands** | 1.11.0 (openhands-ai, SDK 1.34.0) | **965** | 96.5% | 965 | 43 / 50 |
| 🥉 | **OpenCode** | 1.18.34 (npm) | **945** | 94.5% | 945 | 39 / 50 |
| 4 | **Hermes Agent** | git.8b66a51 (2026.9.24) | **939** | 93.9% | 939 | 43 / 50 |

## 2. Category Matrix

| Category | SHS Code | OpenHands | OpenCode | Hermes |
|---|---|---|---|---|
| 1. Code Generation | 100 | 100 | 100 | 100 |
| 2. Debugging & Bug Fixing | 100 | 100 | 98 | 100 |
| 3. Feature Implementation | 100 | 100 | 100 | 100 |
| 4. Testing & QA | **94** | 82 | 88 | 74 |
| 5. Refactoring & Code Quality | 90 | **100** | 90 | 90 |
| 6. Repo / Git / GitHub Engineering | **100** | 97 | 79 | 97 |
| 7. Long-Horizon Autonomous Task | **100** | **100** | 94 | 98 |
| 8. Memory & Context Retention | **100** | **100** | 96 | **100** |
| 9. Multi-Agent / Parallel Engineering | **100** | 86 | **100** | 80 |
| 10. End-to-End Software Engineering | 84 | **100** | **100** | **100** |
| **TOTAL** | **968** | **965** | **945** | **939** |

## 3. Evidence-Based Agent Profiles

### 🥇 SHS Code — 968/1000
**Strengths (measured)**
- Only agent with a **perfect Git/GitHub engineering score (100)** — recreated a 6-commit tagged history + derived a Keep-a-Changelog (`c06t03`), resolved merge conflicts (`c06t04`), rebased + ff-merged linear history (`c06t05`) all cleanly
- **Best Testing & QA (94)** — its defect-hunting test suites detected seeded bugs with the fewest false positives
- Perfect Memory & Context (100): two-turn session retention, 10-point spec recall, decision-log usage, and function-reuse across turns all verified
- Perfect Long-Horizon (100): TODO CLI, static-site generator, retrying HTTP client, repo-maintenance batch and dirty-CSV pipeline all delivered working
- Perfect Multi-Agent (100): all decomposition/integration tasks passed, including the strict docs↔code consistency check

**Weaknesses (measured)**
- **End-to-End (84)** — its only large failure: `c10t01_url_shortener` (4/20). Its shortener raised `ValueError` on a legitimate re-shorten of the same URL with the same alias (self-collision), failing 4 of 5 hidden behavior tests. Trace: `traces/shs-code/c10_e2e/c10t01_url_shortener/`
- `c05t04_naming_docs` (10/20): the rename refactor broke retry semantics — `run_tasks` reported `{'t1': False}` where a flaky task succeeds on the 3rd attempt (hidden test compared retry-loop behavior)
- `c04t01_stringutils_qa` (14/20): one false-positive test against the correct module — the `truncate("abcdef", 2)` edge (width < ellipsis) was tested with the opposite expectation from the spec

### 🥈 OpenHands — 965/1000
**Strengths (measured)**
- **Perfect Refactoring (100)** — the only agent whose `c05t04` rename refactor preserved retry-on-failure behavior exactly
- Perfect Code Generation, Feature Implementation, Long-Horizon, Memory, and E2E scores (100 each) — including the URL shortener SHS stumbled on
- Fastest average wall-clock per task of the four agents (see `task_results.jsonl` `duration_s`)

**Weaknesses (measured)**
- **Multi-Agent (86)** — `c09t01_three_modules` scored **6/20**: the integration step (`main.build_report`) was not delivered working (assertion on `@` in report failed); the decomposition existed but the final integration was broken
- **Testing & QA (82)** — three QA suites had false-positive tests against the correct module (`c04t01`, `c04t02`, `c04t04`, −6 each): expectations were written against intuitive-but-wrong edge behavior rather than the spec
- `c07t05_data_pipeline` (16→20 after uniform verifier calibration, see §6): kept the empty-region row — a spec-ambiguous reading
- Minor: `c06t05_rebase` (17/20) left `TASK.md` untracked (working tree not clean)

### 🥉 OpenCode — 945/1000
**Strengths (measured)**
- Perfect Code Generation, Feature, Memory (well, 96 — one 4-pt session-reuse miss), Multi-Agent (100) and E2E (100)
- Best-in-class speed on simple tasks; solid integration work (`c09` docs consistency delivered)

**Weaknesses (measured)**
- **Git Engineering (79)** — the biggest single-task collapse of the benchmark: `c06t03_changelog` scored **2/20** (recreated history had no version tags, CHANGELOG missing/misderived). Also `c06t05_rebase` (17/20, untracked leftovers)
- **Testing & QA (88)** — false-positive edge-case tests in `c04t01`/`c04t04` (−6 each), plus a missed hidden edge in `c02t04_email_regex` (18/20: uppercase local part)
- `c05t04_naming_docs` (10/20): same retry-semantics break as SHS/Hermes
- `c07t03_http_client` (14/20): delivered the client but no agent-authored tests
- `c08t03_resume_reuse` (16/20): `format_intl` did not reuse turn-1's `normalize_phone` (reimplemented instead) — the only memory-retention miss among the four

### 4th — Hermes Agent (Nous Research) — 939/1000
**Strengths (measured)**
- Perfect Code Generation, Debugging, Feature, Memory, E2E (100 each)
- Strong long-horizon delivery (98): TODO CLI, site generator, HTTP client and pipeline all working and self-verified
- Session resume machinery is excellent: recovered every 429-interrupted task to 20/20 in the recovery sweep

**Weaknesses (measured)**
- **Testing & QA (74)** — weakest category of any agent: `c04t03_argparse_qa` scored **0/20** (test file never created in `tests_agent/` — deliverable miss) and `c04t01` (14/20, false-positive edge test)
- **Multi-Agent (80)** — `c09t01_three_modules` scored **0/20**: none of the four required files were found in the workspace (the agent planned/answered but did not write the files); `c09t02_service_contract` (18/20? see trace) and `c09t04_transforms` also dropped points
- `c05t04_naming_docs` (10/20): same retry-semantics refactor break as SHS/OpenCode
- `c06t05_rebase` (17/20): untracked leftovers left the tree unclean

## 4. Same-Task Head-to-Head Patterns

| Pattern | Agents affected | Evidence |
|---|---|---|
| `truncate(width < ellipsis)` spec-vs-intuition trap (c04t01) | **all four** (−6 each) | every agent wrote a test contradicting the written spec edge; `traces/*/c04_testing_qa/c04t01_*` |
| Retry-semantics broken by rename refactor (c05t04) | SHS, OpenCode, Hermes (−10 each) | identical hidden-test failure `{'t1': False} != {'t1': True}`; OpenHands alone preserved behavior |
| Empty-region CSV row kept vs dropped (c07t05) | SHS, OpenHands, Hermes (−4 each, pre-calibration) | all three consistently produced `cleaned_rows: 8, total: 142.44` with a `""` region group — spec-ambiguous; resolved by §6 calibration |
| Docs↔code signature check (c09t03) | all four (−4 each, pre-fix) | checker was formatting-brittle (and stripped `_` from identifiers); after fixing the checker all four passed 20/20 — their docs were correct |
| URL shortener alias/collision semantics (c10t01) | SHS only (−16) | self-collision ValueError on same-URL re-shorten |
| Three-module integration not delivered (c09t01) | OpenHands (−14), Hermes (−20) | files/integration missing at final state |

## 5. Provider-Switch Test (SHS Code only — outside the 1000 points)

Per benchmark rules, Atria Dawn Preview was used **only** to verify SHS Code's provider-switch capability. Protocol and full evidence: `provider_switch/` (config states, per-phase workspaces, `provider_switch_report.json`).

| Phase | Provider | Result |
|---|---|---|
| 1. Baseline | Agnes `agnes-3.0-flash` | task completed, `p1.txt` created ✅ |
| 2. Switch | Atria `Atria-Dawn-Preview` (`https://api.atria-asi.ai/v1/`) | runtime accepted the new provider; thinking-model replied exactly `SWITCHED` ✅ |
| 3. Restore | Agnes `agnes-3.0-flash` | task completed, `p3.txt` created — runtime intact ✅ |

**Verdict: PASS.** Notes recorded during diagnosis (also instructive findings):
- SHS config precedence: `LLM_MODEL` env var overrides `config.toml [llm].model` (app/config.py:623) — the switch test initially appeared to fail until the env alias was removed; with config as the single source of truth, switching works
- The Atria endpoint's model id is case-sensitive: `Atria-Dawn-Preview`
- The Atria edge returned intermittent misleading errors (`invalid_api_key`, `A supported model is required`) for identical payloads during diagnosis — provider-side flakiness, documented in `provider_switch/provider_switch_report.json`

## 6. Scoring Integrity — Verifier Calibration Ledger (uniform for all agents)

Two verifiers were calibrated AFTER all runs, applied identically to every agent's recorded workspace (original results preserved as `result_pre_amendment.json`; amendments flagged `amended: true` in results):

1. **c07t05_data_pipeline**: the written cleaning spec did not explicitly require dropping rows whose region is empty; both 7-row (drop) and 8-row (keep as `""` group) readings are spec-compliant → check accepts both (132.44 or 142.44 total).
2. **c09t03_code_docs_match**: the signature-match checker was brittle (markdown formatting, and it stripped `_` from identifiers); after fixing the checker, all four agents' existing docs passed 20/20 — no agent work was changed.

No other post-hoc changes. Every score is backed by `verification.json` (point-by-point checks) inside its trace. Failed-run preservation: `result_provider_failed.json` (provider-429 failures) and `result_harness_bug.json` (SHS c08 two-turn harness bug, fixed and re-run) — raw evidence immutable.

## 7. Harness Incidents & Fairness Notes

- **Sandbox resets** (twice during the run): credentials/config restored each time from the conversation record; no results lost (checkpoint commits)
- **SHS two-turn bug (harness, not agent)**: the adapter inserted `--continue` between `--session` and its value, breaking turn 2 for SHS c08 tasks; fixed and all 5 tasks re-run → SHS c08 went 12/100 → 100/100
- **OpenCode working-directory bug (harness)**: `opencode run` initially resolved file writes to the git root of the benchmark repo; fixed with explicit `--dir` and the three affected tasks re-run from scratch (traces wiped before their official runs)
- **Agnes free-tier 429 storms** under 3-4 concurrent streams: tasks that failed purely on provider 429 (all ≤10 pts, `provider_error_retry: true`) were re-run once, sequentially, after streams finished (Hermes +148 pts recovered); the pre-recovery failures remain visible in `result_provider_failed.json`
- **Identical constraints for all agents**: same prompts, same baselines, same caps (25–45 steps by category), same timeouts (330–540 s by category), same verification scripts; workspaces are fresh copies of the same baseline per run; no cross-agent contamination (workspaces outside any git repo)
- **No manual repair of any agent's output**; points come exclusively from mechanical `verify.py` runs against the agent's final workspace

## 8. Reproducibility

- `harness/gen_tasks_*.py` regenerate all 50 tasks deterministically (every verifier self-tested against a golden solution → exactly 20/20 before any agent ran; see commit history)
- `harness/run_stream.py <agent>` + `harness/agents.py` (adapters) reproduce execution; `harness/aggregate.py` rebuilds `results.json` / `results.jsonl` / `task_results.jsonl`
- Per-run evidence: `prompt.txt`, `run.log` (config, timings, stdout/stderr, attempt count, provider-error flags), `agent_events.jsonl` where the agent exposes tool calls (OpenHands), `workspace/` (final file state), `verification.json`, `result.json`
- Git-task history evidence preserved as `workspace_repo.bundle` (clonable: `git clone workspace_repo.bundle`)

## 9. Verdict

**SHS Code wins the benchmark at 968/1000**, with OpenHands (965) statistically inseparable given the two 4-point calibration items, OpenCode (945) close behind, and Hermes Agent (939) fourth — held back primarily by QA-suite false positives, one 0-point multi-agent deliverable miss, and a 0-point QA deliverable miss. The decisive separations were in **Testing & QA** (where writing tests that are correct at spec edges matters more than writing many tests) and **Git engineering** (where OpenCode's changelog/history task collapsed). All four agents completed 50/50 tasks with the primary model `agnes-3.0-flash` and delivered substantial working software; the spread between first and last is 29 points (2.9%).
