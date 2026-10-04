#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID="c01t05"
checks = []
sol = os.path.join(ws, "matrix.py")
ok = os.path.exists(sol)
checks.append({"name": "matrix.py exists", "ok": ok, "points": 2})
if ok:
    rc, out = vlib.write_and_run_pytest(ws, '''
from matrix import rotate_90, spiral_traverse

def test_rotate_3x3():
    m = [[1,2,3],[4,5,6],[7,8,9]]
    assert rotate_90(m) == [[7,4,1],[8,5,2],[9,6,3]]

def test_rotate_2x2():
    assert rotate_90([[1,2],[3,4]]) == [[3,1],[4,2]]

def test_rotate_1x1_and_4x4():
    assert rotate_90([[5]]) == [[5]]
    m = [[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]]
    assert rotate_90(m) == [[13,9,5,1],[14,10,6,2],[15,11,7,3],[16,12,8,4]]

def test_input_not_mutated():
    m = [[1,2],[3,4]]
    rotate_90(m)
    assert m == [[1,2],[3,4]]

def test_spiral_3x3():
    m = [[1,2,3],[4,5,6],[7,8,9]]
    assert spiral_traverse(m) == [1,2,3,6,9,8,7,4,5]

def test_spiral_rect():
    m = [[1,2,3],[4,5,6]]
    assert spiral_traverse(m) == [1,2,3,6,5,4]

def test_spiral_single():
    assert spiral_traverse([[7]]) == [7]
''')
    checks.append({"name": "hidden pytest suite", "ok": rc == 0, "points": 18,
                   "detail": out[-400:] if rc != 0 else "passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
