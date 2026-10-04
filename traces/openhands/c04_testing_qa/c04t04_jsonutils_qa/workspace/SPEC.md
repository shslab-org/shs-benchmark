SPEC for jsonutils.py:

- safe_get(obj, path, default=None): dot-path lookup supporting list indices;
  returns default on ANY miss (bad index, missing key, wrong types). No
  exception may ever escape.
- deep_merge(a, b): returns a NEW dict; nested dicts merge recursively; b
  wins on conflicts; neither a nor b may be mutated (not even nested!).
- dumps_compact(obj): compact JSON text (no spaces).
- parse_lenient(text): parses JSON; when the text is single-quoted JSON
  (keys and string values in single quotes), converts it correctly — WITHOUT
  corrupting apostrophes that appear inside string values.

Your job: write tests_agent/test_jsonutils.py that fails against any module
violating this spec and passes against a correct one. The shipped module
violates it (deep_merge mutates nested dicts of 'a'; parse_lenient corrupts
apostrophes; safe_get lets ValueError escape on paths like 'a.b' where b is a
non-numeric list index). Do NOT modify jsonutils.py.