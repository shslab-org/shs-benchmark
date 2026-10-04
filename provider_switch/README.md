# Provider-Switch Test (Atria Dawn Preview) — SHS Code only

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
