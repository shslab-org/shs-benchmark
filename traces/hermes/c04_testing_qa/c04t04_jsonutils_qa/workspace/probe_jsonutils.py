"""QA probes for jsonutils spec violations — write output to stdout."""
import copy
import json
import sys

sys.path.insert(0, ".")
import jsonutils as j

print("--- safe_get probes ---")
try:
    print("a.b on list:", j.safe_get({"a": [1, 2]}, "a.b", "MISS"))
except Exception as e:
    print("a.b on list raised:", type(e).__name__, e)

try:
    print("a.-1 on list:", j.safe_get({"a": [1, 2]}, "a.-1", "MISS"))
except Exception as e:
    print("a.-1 raised:", type(e).__name__, e)

try:
    print("a.1x on list:", j.safe_get({"a": [1, 2]}, "a.1x", "MISS"))
except Exception as e:
    print("a.1x raised:", type(e).__name__, e)

try:
    print("None path:", j.safe_get({"a": 1}, None, "MISS"))
except Exception as e:
    print("None path raised:", type(e).__name__, e)

try:
    print("numeric key lookup on dict:", j.safe_get({"0": "zero"}, "0", "MISS"))
except Exception as e:
    print("numeric key raised:", type(e).__name__, e)

print("--- deep_merge probes ---")
a = {"x": {"y": 1}}
b = {"x": {"w": 2}}
sa, sb = copy.deepcopy(a), copy.deepcopy(b)
res = j.deep_merge(a, b)
print("result:", res)
print("a mutated:", a != sa, a)
print("b mutated:", b != sb, b)

# nested b value aliasing
b2 = {"x": {"z": {"q": 9}}}
sb2 = copy.deepcopy(b2)
res2 = j.deep_merge({}, b2)
print("b2 mutated:", b2 != sb2, b2)

print("--- parse_lenient probes ---")
cases = [
    "{'a': 'b'}",
    "{'msg': 'it's fine'}",
    "{'msg': 'a b'}",
    '{"key": "value"}',
]
for c in cases:
    try:
        print(repr(c), "->", j.parse_lenient(c))
    except Exception as e:
        print(repr(c), "raised:", type(e).__name__, e)

# what does a CORRECT impl need to return for the apostrophe case?
# The spec says single-quoted JSON with apostrophes inside string values must parse
# without corruption. E.g. "{'msg': 'it''s'}" or with backslash escape? Spec is
# ambiguous on the exact apostrophe encoding, so test with the unescaped form and
# require no exception (per "parses JSON" + not corrupting).

print("--- dumps_compact probes ---")
print(j.dumps_compact({"a": 1, "b": [2, 3]}))
