#!/usr/bin/env python3
"""A simple command-line TODO application.

Usage:
    python todo.py add <text>
    python todo.py list
    python todo.py done <number>
    python todo.py rm <number>

Items persist in a JSON file whose path comes from the TODO_FILE
environment variable (default: ./todos.json).
"""

import argparse
import json
import os
import sys


def todos_path() -> str:
    return os.environ.get("TODO_FILE", "./todos.json")


def load_todos(path: str) -> list:
    """Load the todo list from *path*; an absent or empty file means no items."""
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
    except OSError as exc:
        sys.stderr.write(f"error: cannot read {path}: {exc}\n")
        sys.exit(1)
    if not raw.strip():
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        sys.stderr.write(
            f"error: {path} does not contain valid JSON; refusing to overwrite it.\n"
        )
        sys.exit(1)
    except OSError as exc:
        sys.stderr.write(f"error: cannot read {path}: {exc}\n")
        sys.exit(1)
    if not isinstance(data, list):
        sys.stderr.write(f"error: {path} has unexpected format (expected a list).\n")
        sys.exit(1)
    return data


def save_todos(path: str, todos: list) -> None:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(todos, f, indent=2)
            f.write("\n")
    except OSError as exc:
        sys.stderr.write(f"error: cannot write {path}: {exc}\n")
        sys.exit(1)


def get_number(todos: list, num: int, command: str) -> int:
    """Validate a 1-based position; return its 0-based index."""
    if num < 1 or num > len(todos):
        total = len(todos)
        sys.stderr.write(
            f"error: no item {num} for '{command}' (list has {total} item"
            f"{'s' if total != 1 else ''}).\n"
        )
        sys.exit(1)
    return num - 1


def cmd_add(args, todos) -> None:
    text = " ".join(args.text).strip()
    if not text:
        sys.stderr.write("error: 'add' requires task text.\n")
        sys.exit(1)
    todos.append({"text": text, "done": False})
    save_todos(todos_path(), todos)
    print(f"Added: {text}")


def cmd_list(args, todos) -> None:
    if not todos:
        print("No tasks yet.")
        return
    for t in todos:
        mark = "x" if t.get("done") else " "
        print(f"[{mark}] {t['text']}")


def cmd_done(args, todos) -> None:
    idx = get_number(todos, args.number, "done")
    todos[idx]["done"] = True
    save_todos(todos_path(), todos)
    print(f"Marked done: {todos[idx]['text']}")


def cmd_rm(args, todos) -> None:
    idx = get_number(todos, args.number, "rm")
    removed = todos.pop(idx)
    save_todos(todos_path(), todos)
    print(f"Removed: {removed['text']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="todo.py",
        description="A simple command-line TODO app. Items persist in a JSON "
        "file taken from the TODO_FILE environment variable (default: "
        "./todos.json).",
    )
    sub = parser.add_subparsers(dest="command")

    p_add = sub.add_parser("add", help="add a new task")
    p_add.add_argument("text", nargs="+", help="task text (join words with spaces)")

    sub.add_parser("list", help="list all tasks")

    p_done = sub.add_parser("done", help="mark a task done (1-based position)")
    p_done.add_argument("number", type=int, help="1-based position in the list")

    p_rm = sub.add_parser("rm", help="remove a task (1-based position)")
    p_rm.add_argument("number", type=int, help="1-based position in the list")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command is None:
        parser.print_help(sys.stderr)
        sys.exit(1)

    handlers = {"add": cmd_add, "list": cmd_list, "done": cmd_done, "rm": cmd_rm}
    todos = load_todos(todos_path())
    handlers[args.command](args, todos)


if __name__ == "__main__":
    main()
