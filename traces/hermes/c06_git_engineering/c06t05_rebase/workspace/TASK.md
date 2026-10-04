Rebase task (do it with real git):

1. `git init`; create `main.txt` containing the single line "one"; commit "Add one" on main
2. Create branch `feature`; on it, create `feature.txt` containing "feature work";
   commit "Add feature"
3. Back on main: append "two" on a new line of main.txt; commit "Add two"
4. Still on main: append "three" on a new line of main.txt; commit "Add three"
5. Switch to feature; REBASE feature onto main (no merge commits!)
6. On feature, append a new line "feature-continued" to feature.txt;
   commit "Continue feature"
7. Finally merge feature into main USING --ff-only (fast-forward only).

Final state on main:
- main.txt has one/two/three (three lines), feature.txt has "feature work" +
  "feature-continued"
- `git log --merges main` is EMPTY (linear history)
- `git log --oneline main` contains all 5 commits in order
- working tree clean