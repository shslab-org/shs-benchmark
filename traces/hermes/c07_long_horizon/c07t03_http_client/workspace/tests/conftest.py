import pathlib
import sys

# Make the project root (where httpclient.py lives) importable no matter
# which directory pytest is launched from.
ROOT = str(pathlib.Path(__file__).resolve().parent.parent)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
