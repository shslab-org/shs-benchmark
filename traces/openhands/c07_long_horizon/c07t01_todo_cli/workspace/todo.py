#!/usr/bin/env python3
"""Command-line TODO application.

Usage:
    python todo.py add <text>
    python todo.py list
    python todo.py done <number>
    python todo.py rm <number>

Items persist in a JSON file. The path is taken from the TODO_FILE
environment variable (default: ./todos.json).
"""

import argparse
import json
import os
import sys

DEFAULT_FILE = "./todos.json"


def err(message):
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def load_file(path):
    """Load a JSON list of items; empty list if file does not exist."""
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        err(f"could not read {path}: {e}")
    if not isinstance(data, list):
        err(f"corrupt data in {path}: expected a JSON list of items")
    return data


def save_file(path, items):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
            f.write("\n")
    except OSError as e:
        err(f"could not write {path}: {e}")


def position_to_index(pos_text, items):
    """Convert a 1-based position string to a 0-based index, or exit."""
    try:
        pos = int(pos_text)
    except ValueError:
        err(f"invalid number: {pos_text!r} (expected a positive integer)")
    if pos < 1 or pos > len(items):
        err(
            f"position {pos} is out of range "
            f"(store has {len(items)} item(s))"
        )
    return pos - 1


def normalize(items):
    """Ensure items are well-formed; tolerate legacy/corrupt entries."""
    normalized = []
    for i, item in enumerate(items):
        if isinstance(item, dict):
            text = item.get("text", "")
            done = bool(item.get("done", False))
        elif isinstance(item, str):
            text, done = item, False
        else:
            err(
                f"corrupt data in TODO file at position {i + 1}: "
                f"expected a string or object"
            )
        normalized.append({"text": text, "done": done})
    return normalized


def cmd_add(args, items):
    if not args.text.strip():
        err("todo text must not be empty")
    items.append({"text": args.text, "done": False})
    return items


def cmd_list(args, items):
    if not items:
        print("No todo items.")
        return items
    for item in items:
        mark = "x" if item["done"] else " "
        print(f"[{mark}] {item['text']}")
    return items


def mark_position(items, pos_text):
    idx = position_to_index(pos_text, items)
    return idx, items[idx]


def cmd_done(args, items):
    idx, item = mark_position(items, args.number)
    item["done"] = True
    print(f"Marked item {args.number} as done: {item['text']}")
    return items


def cmd_rm(args, items):
    idx, item = mark_position(items, args.number)
    del items[idx]
    print(f"Removed item {args.number}: {item['text']}")
    return items


def build_parser():
    parser = argparse.ArgumentParser(
        prog="todo.py",
        description="Command-line TODO application with JSON persistence.",
        epilog=(
            "Items are stored in the file given by the TODO_FILE "
            f"environment variable (default: {DEFAULT_FILE}). "
            "Numbers for done/rm are 1-based positions in the list."
        ),
    )
    sub = parser.add_subparsers(dest="command", metavar="command")

    p_add = sub.add_parser("add", help="add a new todo item")
    p_add.add_argument("text", help="text of the todo item")
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="list all todo items")
    p_list.set_defaults(func=cmd_list)

    p_done = sub.add_parser("done", help="mark an item as done")
    p_done.add_argument("number", help="1-based position of the item")
    p_done.set_defaults(func=cmd_done)

    p_rm = sub.add_parser("rm", help="remove an item")
    p_rm.add_argument("number", help="1-based position of the item")
    p_rm.set_defaults(func=cmd_rm)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help(sys.stderr)
        sys.exit(1)

    path = os.environ.get("TODO_FILE", DEFAULT_FILE)
    items = normalize(load_file(path))
    items = args.func(args, items)
    save_file(path, items)


if __name__ == "__main__":
    main()
