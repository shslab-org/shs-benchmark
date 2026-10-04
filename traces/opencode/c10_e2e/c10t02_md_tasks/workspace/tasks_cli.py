#!/usr/bin/env python3
import argparse
import os
import re
import sys
from pathlib import Path

DEFAULT_DIR = "./tasks"


def tasks_dir():
    p = Path(os.environ.get("TASKS_DIR", DEFAULT_DIR))
    p.mkdir(parents=True, exist_ok=True)
    return p


def file_for(task_id: int) -> Path:
    return tasks_dir() / f"task_{task_id:04d}.md"


def write_task(task_id: int, title: str, status: str, priority: str) -> None:
    lines = [
        f"# {title}",
        "",
        f"status: {status}",
        f"priority: {priority}",
        "",
    ]
    file_for(task_id).write_text("\n".join(lines))


def read_task(task_id: int) -> dict:
    path = file_for(task_id)
    if not path.exists():
        sys.exit(f"error: no task with id {task_id}")
    text = path.read_text()
    task = {"id": task_id, "status": "open", "priority": "med", "title": ""}
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("# "):
            task["title"] = s[2:]
        elif s.startswith("status:"):
            task["status"] = s.split(":", 1)[1].strip()
        elif s.startswith("priority:"):
            task["priority"] = s.split(":", 1)[1].strip()
    return task


def all_tasks():
    tasks = []
    for path in sorted(tasks_dir().glob("task_*.md")):
        m = re.match(r"task_(\d+)\.md$", path.name)
        if not m:
            continue
        tasks.append(read_task(int(m.group(1))))
    return tasks


def next_id() -> int:
    ids = [t["id"] for t in all_tasks()]
    return (max(ids) + 1) if ids else 1


def cmd_add(args):
    title = args.title
    task_id = next_id()
    write_task(task_id, title, "open", args.priority)
    print(f"added task {task_id}: {title} (priority {args.priority})")


def cmd_list(args):
    tasks = all_tasks()
    if not args.all:
        tasks = [t for t in tasks if t["status"] == "open"]
    if not tasks:
        print("(no tasks)")
        return
    rows = [
        ("id", "status", "priority", "title"),
    ] + [(str(t["id"]), t["status"], t["priority"], t["title"]) for t in tasks]
    widths = [max(len(r[i]) for r in rows) for i in range(4)]
    for j, row in enumerate(rows):
        print("  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)).rstrip())
        if j == 0:
            print("  ".join("-" * w for w in widths))


def cmd_done(args):
    task = read_task(args.id)
    task["status"] = "done"
    write_task(task["id"], task["title"], "done", task["priority"])
    print(f"task {task['id']} marked done")


def cmd_rm(args):
    path = file_for(args.id)
    if not path.exists():
        sys.exit(f"error: no task with id {args.id}")
    path.unlink()
    print(f"task {args.id} deleted")


def main():
    parser = argparse.ArgumentParser(prog="tasks_cli.py")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add")
    p_add.add_argument("title")
    p_add.add_argument("--priority", choices=["low", "med", "high"], default="med")
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list")
    p_list.add_argument("--all", action="store_true")
    p_list.set_defaults(func=cmd_list)

    p_done = sub.add_parser("done")
    p_done.add_argument("id", type=int)
    p_done.set_defaults(func=cmd_done)

    p_rm = sub.add_parser("rm")
    p_rm.add_argument("id", type=int)
    p_rm.set_defaults(func=cmd_rm)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
