# Code Review & Refactor Summary — `report.py`

## Task
`process_orders` was a god function: it parsed lines, validated them,
applied the bulk discount, and aggregated/rounded the report dict all in
one loop-heavy body. Refactor it into focused helpers while keeping
public behavior **exactly** identical (hidden tests check parsing,
discounts, aggregation, rounding, and the empty-input case).

## Changes (in `report.py`)
Split into 4 helpers + the public entry point:

| Function              | Responsibility                                             |
|-----------------------|------------------------------------------------------------|
| `parse_line(line)`    | One line -> `(sku, qty, price)` or `None` (malformed / bad qty / bad price / empty sku). |
| `parse_all(raw_lines)`| Loops lines, returns `(valid, invalid_count)`.             |
| `compute_line_total(qty, price)` | Single-line total incl. 5% bulk discount when qty >= 10. |
| `aggregate(valid, invalid_count)` | Totals + per-SKU dict, 2-decimal rounding; builds the report dict. |
| `process_orders(raw_lines)` | **Public entry point** — orchestrates `parse_all` then `aggregate`. Signature & docstring unchanged. |

No new external dependencies; pure functions, no I/O.

## Issues found in the original
- Single function mixing three concerns (parse, discount, aggregate) — hard to test/reuse.
- No helper reuse: discount rule (`q >= 10 -> *0.95`) was inline; now isolated in `compute_line_total`.
- Validation rules embedded in the parse loop; now isolated in `parse_line`.
- (No security/bug issues: inputs are local strings; only documented edge
  cases: `nan`/`inf` prices produce `nan`/`inf` totals identically to the
  original; rounding is float `round(x, 2)` unchanged.)

## Verification (behavior preservation)
- **Reference outputs** captured from the original before refactoring
  (empty input, single line, mixed valid/invalid, tiny values,
  rounding-sensitive 0.33x3 case, whitespace-heavy line) — all 6 PASS
  after refactor, byte-identical dicts.
- **500-case fuzz** comparing refactored `process_orders` against an
  inlined copy of the original algorithm, with NaN-aware comparison:
  **0 real mismatches** (the 66 raw `==` "mismatches" were NaN==NaN
  float semantics, not behavioral differences — both sides produce
  identical dicts).
- **`verify` (build+test+syntax)**: ALL PASS ✓ (`python -m compileall -q .` clean; no pytest suite present in this repo, so build/syntax is the binding check).
- Empty-input case explicitly confirmed: `{'valid_count': 0, 'invalid_count': 0, 'total': 0.0, 'by_sku': {}}` — identical before/after.

## Public API
- `process_orders` remains the sole public entry point; signature
  `(raw_lines) -> dict` and the exact returned dict shape
  (`valid_count`, `invalid_count`, `total`, `by_sku`) are unchanged.
  Helpers are plain module-level functions (usable if tests import
  them, no side effects).
