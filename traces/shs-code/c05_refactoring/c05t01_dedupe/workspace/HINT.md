Refactor task: the rounding + tax block is duplicated in
retail_total and wholesale_total. Extract the shared logic into a single
helper (e.g. _round_cents(x) and/or _apply_tax(x)) and have both public
functions use it. Public API (retail_total, wholesale_total) and behavior
must remain IDENTICAL.