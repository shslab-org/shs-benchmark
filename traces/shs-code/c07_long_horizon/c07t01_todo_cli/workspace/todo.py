#!/usr/bin/env python3
"""A simple command-line TODO application.

Commands:
  add <text>       Add a new pending TODO item.
  list             List all items, one per line: "[ ] text" or "[x] text".
  done <number>    Mark the item at 1-based position <number> as done.
  rm <number>      Remove the item at 1-based position <number>.

Persistence: items are stored as a JSON array in the file given by the
TODO_FILE environment variable (default: ./todos.json).
"""

import argparse
import json
import os
import sys

DEFAULT_FILE = "./todos.json"


def store_path() -> str:
    return os.environ.get("TODO_FILE") or DEFAULT_FILE


def load_items() -> list:
    """Load items from the JSON store, returning [] when absent/empty."""
    path = store_path()
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        die(f"could not read TODO file {path!r}: {exc}")
    if isinstance(data, dict):
        data = data.get("items", [])
    if not isinstance(data, list):
        die(f"TODO file {path!r} has an unexpected format; expected a JSON list of items")
    return data


def save_items(items: list) -> None:
    """Atomically write items to the JSON store."""
    path = store_path()
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2)
            f.write("\n")
        os.replace(tmp, path)
    except OSError as exc:
        die(f"could not write TODO file {path!r}: {exc}")


def die(message: str, code: int = 1) -> None:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(code)


def parse_position(raw: str) -> int:
    """Parse a 1-based item position from the user's argument."""
    try:
        pos = int(raw)
    except (TypeError, ValueError):
        die(f"invalid item number {raw!r}; expected a positive integer")
    if pos < 1:
        die(f"invalid item number {raw!r}; positions start at 1")
    return pos


def cmd_add(text: str) -> int:
    if not text.strip():
        die("nothing to add; provide non-empty text")
    items = load_items()
    items.append({"text": text, "done": False})
    save_items(items)
    print(f"added item {len(items)}: {text}")
    return 0


def cmd_list() -> int:
    items = load_items()
    if not items:
        print("No items yet. Add one with: python todo.py add <text>")
        return 0
    for i, item in enumerate(items, start=1):
        mark = "x" if item.get("done") else " "
        print(f"{i}. [{mark}] {item.get('text', '')}")
    return 0


def _target_index(items: list, pos: int) -> int:
    if pos > len(items):
        die(f"item {pos} does not exist (only {len(items)} item(s) present)")
    return pos - 1


def cmd_done(raw_pos: str) -> int:
    pos = parse_position(raw_pos)
    items = load_items()
    idx = _target_index(items, pos)
    items[idx]["done"] = True
    save_items(items)
    print(f"marked item {pos} as done: {items[idx].get('text', '')}")
    return 0


def cmd_rm(raw_pos: str) -> int:
    pos = parse_position(raw_pos)
    items = load_items()
    idx = _target_index(items, pos)
    removed = items.pop(idx)
    save_items(items)
    print(f"removed item {pos}: {removed.get('text', '')}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="todo.py",
        description="Simple CLI TODO app. Items persist in a JSON file "
        "(TODO_FILE env var, default: ./todos.json).",
    )
    sub = parser.add_subparsers(dest="command", metavar="<command>")

    p_add = sub.add_parser("add", help="add a new TODO item")
    p_add.add_argument("text", help="text of the new item")

    sub.add_parser("list", help="list all items with checkboxes")

    p_done = sub.add_parser("done", help="mark an item as done (1-based position)")
    p_done.add_argument("number", help="1-based position of the item")

    p_rm = sub.add_parser("rm", help="remove an item (1-based position)")
    p_rm.add_argument("number", help="1-based position of the item")

    return parser


def main(argv: list | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        print()
        die("no command given; use one of: add, list, done, rm (try --help)")

    if args.command == "add":
        return cmd_add(args.text)
    if args.command == "list":
        return cmd_list()
    if args.command == "done":
        return cmd_done(args.number)
    if args.command == "rm":
        return cmd_rm(args.number)

    die(f"unknown command {args.command!r}")
    return 1  # unreachable


if __name__ == "__main__":
    sys.exit(main())
