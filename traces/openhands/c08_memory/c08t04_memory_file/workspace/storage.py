import json
import os


def save_notes(notes: list, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(notes, f, indent=2)


def load_notes(path: str) -> list:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
