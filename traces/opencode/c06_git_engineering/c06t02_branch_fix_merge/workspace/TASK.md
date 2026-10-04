Workflow task (do it with real git commands):

1. `git init`, commit everything on `main` as "Initial commit" - tests will
   FAIL, that is expected (bug present by design)
2. Create a branch named `fix/divide-by-zero`
3. On that branch: change divide() so that dividing by zero returns None
   (keep everything else), commit with message "Fix divide by zero"
4. Switch back to `main` and merge the branch into main
5. At the end: on `main`, `python -m pytest test_calc.py` must PASS, the
   branch `fix/divide-by-zero` must still exist, and the working tree clean.