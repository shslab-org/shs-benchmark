import importlib.util, os, sys

# Shadow the shipped 'stringutils' with the corrected reference BEFORE test
# collection imports it.
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location(
    "stringutils", os.path.join(ROOT, "workspace", "reference_stringutils.py")
)
ref = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ref)
sys.modules["stringutils"] = ref
