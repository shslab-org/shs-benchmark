import sys, copy
sys.path.insert(0, ".")
import jsonutils as j

# deep_merge aliasing checks (shipped code)
a = {'x': {'y': 1}}
r = j.deep_merge(a, {})
print("r['x'] is a['x']:", r['x'] is a['x'])
r2 = j.deep_merge({}, {'x': {'y': 1}})
b = {'x': {'y': 1}}
r3 = j.deep_merge({}, b)
print("r3['x'] is b['x']:", r3['x'] is b['x'])
# mutate result, see if inputs move
r['x']['y'] = 999
print("a after mutating result:", a)
print("result r:", r)
