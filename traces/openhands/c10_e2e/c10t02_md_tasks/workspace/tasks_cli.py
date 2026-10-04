#!/usr/bin/env python3
"""Markdown-backed task manager CLI."""

import argparse
import os
import re
import sys

TASKS_DIR = os.environ.get("TASKS_DIR", "./tasks")

PRIORITIES = ("low", "med", "high")
STATUS_RE = re.compile(r"^Status:\s*(\w+)")
PRIORITY_RE = re.compile(r"^Priority:\s*(\w+)")


def tasks_dir():
    return TASKS_DIR


def ensure_dir():
    os.makedirs(tasks_dir(), exist_ok=True)


def task_file(task_id):
    return os.path.join(tasks_dir(), f"{task_id}.md")


def list_task_ids():
    ids = []
    if os.path.isdir(tasks_dir()):
        for name in os.listdir(tasks_dir()):
            if name.endswith(".md"):
                stem = name[:-3]
                if stem.isdigit():
                    ids.append(int(stem))
    return sorted(ids)


def next_id():
    ids = list_task_ids()
    return (max(ids) + 1) if ids else 1


def read_task(task_id):
    path = task_file(task_id)
    if not os.path.isfile(path):
        sys.exit(f"Error: task {task_id} not found")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    title = ""
    status = "open"
    priority = "med"
    for line in text.splitlines():
        if line.startswith("# ") and not title:
            title = line[2:].strip()
        m = STATUS_RE.match(line)
        if m:
            status = m.group(1).lower()
        m = PRIORITY_RE.match(line)
        if m:
            priority = m.group(1).lower()
    return {"id": task_id, "title": title, "status": status, "priority": priority}


def cmd_add(args):
    ensure_dir()
    task_id = next_id()
    content = (
        f"# {args.title}\n"
        f"\n"
        f"Status: open\n"
        f"Priority: {args.priority}\n"
    )
    with open(task_file(task_id), "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Added task {task_id}: {args.title}")


def cmd_list(args):
    rows = []
    for task_id in list_task_ids():
        task = read_task(task_id)
        if task["status"] != "open" and not args.all:
            continue
        rows.append((task["id"], task["status"], task["priority"], task["title"]))
    if not rows:
        print("No tasks found.")
        return
    headers = ("id", "status", "priority", "title")
    widths = [max(len(str(h)), max(len(str(r[i])) for r in rows))
              for i, h in enumerate(headers)]
    fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    print(fmt.format(*headers))
    print(fmt.format(*("-" * w for w in widths)))
    for row in rows:
        print(fmt.format(*row))


def cmd_done(args):
    path = task_file(args.id)
    if not os.path.isfile(path):
        sys.exit(f"Error: task {args.id} not found")
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    found = False
    new_lines = []
    for line in lines:
        if line.startswith("Status:"):
            new_lines.append("Status: done\n")
            found = True
        else:
            new_lines.append(line)
    if not found:
        new_lines.append("Status: done\n")
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print(f"Task {args.id} marked as done")


def cmd_rm(args):
    path = task_file(args.id)
    if not os.path.isfile(path):
        sys.exit(f"Error: task {args.id} not found")
    os.remove(path)
    print(f"Removed task {args.id}")


def build_parser():
    parser = argparse.ArgumentParser(prog="tasks_cli.py",
                                    description="Markdown-backed task manager")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="add a new task")
    p_add.add_argument("title", help="task title")
    p_add.add_argument("--priority", choices=PRIORITIES, default="med",
                       help="task priority (default: med)")
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="list tasks")
    p_list.add_argument("--all", action="store_true",
                       help="include done tasks")
    p_list.set_defaults(func=cmd_list)

    p_done = sub.add_parser("done", help="mark a task as done")
    p_done.add_argument("id", type=int, help="task id")
    p_done.set_defaults(func=cmd_done)

    p_rm = sub.add_parser("rm", help="delete a task")
    p_rm.add_argument("id", type=int, help="task id")
    p_rm.set_defaults(func=cmd_rm)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
