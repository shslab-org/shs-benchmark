Merge-conflict resolution task:

1. `git init`; commit all files as "Initial commit" on `main`
2. Create branch `feature/b-casual-greeting`; there, change greeting() to
   return f"Hey {APP_NAME} fan!" - commit "Casual greeting"
3. Back on `main`, change greeting() to return
   f"Hello, valued user of {APP_NAME} (v2)" - commit "Formal greeting v2"
4. Merge `feature/b-casual-greeting` into `main` - you WILL hit a conflict in
   greeting(); resolve it so the final greeting is the COMBINED style:
       return f"Hey there, valued user of {APP_NAME} (v2)!"
5. Commit the resolution ("Merge feature/b-casual-greeting"). At the end the
   suite must pass with this additional test present in test_config.py:

       def test_greeting_combined():
           assert greeting() == "Hey there, valued user of DemoApp (v2)!"

   (append that test to test_config.py). No conflict markers left anywhere,
   working tree clean, and `git log --merges` shows a merge commit.