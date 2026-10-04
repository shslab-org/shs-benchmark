"""Verify storage.py save/load round-trip and missing-file behavior.

Run:  python workspace/verify_storage.py   (from the project directory)
Exit code 0 = all checks passed.
"""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage import save_notes, load_notes  # noqa: E402


def main() -> int:
    # 1. Round-trip (nested + unicode, per the JSON-over-CSV decision)
    notes = [
        {"id": 1, "body": "hello", "tags": ["a", "b"]},
        {"id": 2, "body": "wörld", "tags": []},
    ]
    tmp = os.path.join(tempfile.gettempdir(), "notes_rt.json")
    save_notes(notes, tmp)
    loaded = load_notes(tmp)
    assert loaded == notes, f"round-trip mismatch: {loaded!r}"
    print("round-trip OK")

    # 2. Missing file -> []
    missing = os.path.join(tempfile.gettempdir(), "definitely_missing_notes_xyz.json")
    assert not os.path.exists(missing)
    assert load_notes(missing) == []
    print("missing-file OK -> []")

    os.unlink(tmp)
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
