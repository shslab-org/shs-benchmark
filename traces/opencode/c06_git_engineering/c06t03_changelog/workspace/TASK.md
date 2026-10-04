Changelog task:

1. `git init`; recreate the 6-commit history EXACTLY as described in
   HISTORY.md (6 commits, in that order, with those exact messages; add a
   small realistic change to service.py / README.md for each; tag the 1st,
   3rd and 5th commit as v0.1.0, v0.2.0, v0.3.0)
2. Then write CHANGELOG.md in Keep-a-Changelog style with one section per
   version tag (## [0.3.0] first):
   Each section must mention the actual changes contained in the commits
   that belong to that version (derive them from git log), and must include
   the tag name. End with git status clean.