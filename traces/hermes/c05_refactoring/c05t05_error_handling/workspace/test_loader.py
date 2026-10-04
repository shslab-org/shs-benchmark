import json
import os
import tempfile

import loader

d = tempfile.mkdtemp()
ok = os.path.join(d, "ok.json")
with open(ok, "w") as f:
    json.dump({"a": {"b": 1}}, f)

assert loader.load(ok) == {"a": {"b": 1}}, "load valid"

try:
    loader.load(os.path.join(d, "nope.json"))
    raise AssertionError("load missing did not raise")
except FileNotFoundError:
    pass

bad = os.path.join(d, "bad.json")
with open(bad, "w") as f:
    f.write("{not json")
try:
    loader.load(bad)
    raise AssertionError("load bad did not raise")
except json.JSONDecodeError:
    pass

assert loader.get({"a": {"b": 1}}, "a.b") == 1
assert loader.get({"a": 1}, "a.b") is None
assert loader.get({}, "a") is None

out = os.path.join(d, "out.json")
assert loader.save(out, {"x": 2}) is True
assert json.load(open(out)) == {"x": 2}

try:
    loader.save(d, {"x": 2})
    raise AssertionError("save OSError did not propagate")
except OSError:
    pass

print("ALL TESTS PASSED")
