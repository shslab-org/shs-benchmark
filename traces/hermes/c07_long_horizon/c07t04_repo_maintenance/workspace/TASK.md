Long-horizon maintenance task on this repository (a git repo with 1
commit; git identity is already configured in this environment). ALL of the
following must be done, verified, and committed:

1. Run the test suite (python -m pytest -q). Two areas fail.
2. FIX the remove() bug in shop/cart.py.
3. FIX the bulk-discount bug in shop/pricing.py: when qty >= bulk_threshold,
   total = qty * unit_price * bulk_discount.
4. NEW FEATURE: add `shop/backup.py` with `backup_json(cart, path)` that
   writes the cart's items to path as JSON (indent=2). Add tests for it in
   tests/test_backup.py.
5. Update README.md to document cart, pricing (including the bulk rule) and
   the backup feature.
6. Commit your work in at least 2 git commits with descriptive messages.
   Final state: the full test suite passes and git status is clean.