#!/usr/bin/env python3
"""Markdown-backed task manager.

Each task is a human-editable markdown file <TASKS_DIR>/<id>.md:

    # Task title
    Status: open
    Priority: med

TASKS_DIR is an env var (default ./tasks).
"""
import argparse
import os
import re
import sys

DEFAULT_TASKS_DIR = "./tasks"
VALID_PRIORITIES = ("low", "med", "high")
STATUS_OPEN = "open"
STATUS_DONE = "done"

TITLE_RE = re.compile(r"^#\s+(.*)$")
STATUS_RE = re.compile(r"^Status:\s*(.*)$")
PRIORITY_RE = re.compile(r"^Priority:\s*(.*)$")


def tasks_dir():
    d = os.environ.get("TASKS_DIR", DEFAULT_TASKS_DIR)
    return d


def task_path(task_id):
    return os.path.join(tasks_dir(), f"{task_id}.md")


def parse_task_file(path):
    """Parse a task markdown file -> dict with title, status, priority."""
    title, status, priority = None, None, None
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            m = TITLE_RE.match(line)
            if m and title is None:
                title = m.group(1).strip()
                continue
            m = STATUS_RE.match(line)
            if m:
                status = m.group(1).strip()
                continue
            m = PRIORITY_RE.match(line)
            if m:
                priority = m.group(1).strip()
    return {"title": title or "(untitled)", "status": status, "priority": priority}


def load_tasks(include_all=True):
    """Return list of {id, title, status, priority} sorted by id."""
    d = tasks_dir()
    tasks = []
    if os.path.isdir(d):
        names = sorted(
            os.listdir(d),
            key=lambda n: int(n[:-3]) if n.endswith(".md") and n[:-3].isdigit() else 10**9,
        )
        for name in names:
            if not name.endswith(".md"):
                continue
            base = name[:-3]
            if not base.isdigit():
                continue
            t = parse_task_file(os.path.join(d, name))
            t["id"] = int(base)
            tasks.append(t)
    tasks.sort(key=lambda t: t["id"])
    return tasks


def next_id():
    ids = [t["id"] for t in load_tasks()]
    return max(ids) + 1 if ids else 1


def cmd_add(args):
    d = tasks_dir()
    os.makedirs(d, exist_ok=True)
    task_id = next_id()
    lines = [
        f"# {args.title}",
        f"Status: {STATUS_OPEN}",
        f"Priority: {args.priority}",
    ]
    with open(task_path(task_id), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"added task {task_id}: {args.title}")


def cmd_list(args):
    tasks = load_tasks()
    if not args.all:
        tasks = [t for t in tasks if t["status"] != STATUS_DONE]
    if not tasks:
        print("no tasks")
        return
    headers = ("ID", "STATUS", "PRIORITY", "TITLE")
    rows = [(str(t["id"]), t["status"] or "-", t["priority"] or "-", t["title"]) for t in tasks]
    widths = [max(len(h), *(len(r[i]) for r in rows)) if rows else len(h) for i, h in enumerate(headers)]
    print(" | ".join(h.ljust(w) for h, w in zip(headers, widths)))
    print("-+-".join("-" * w for w in widths))
    for r in rows:
        print(" | ".join(c.ljust(w) for c, w in zip(r, widths)))


def _find_task(task_id):
    if not os.path.isfile(task_path(task_id)):
        sys.exit(f"error: task {task_id} not found")
    return task_id


def cmd_done(args):
    _find_task(args.id)
    path = task_path(args.id)
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    found = False
    for i, line in enumerate(lines):
        m = STATUS_RE.match(line)
        if m:
            lines[i] = f"Status: {STATUS_DONE}"
            found = True
    if not found:
        insert_at = 0
        for i, line in enumerate(lines):
            if line.startswith("#"):
                insert_at = i + 1
                break
        lines.insert(insert_at, f"Status: {STATUS_DONE}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"task {args.id} marked done")


def cmd_rm(args):
    _find_task(args.id)
    os.remove(task_path(args.id))
    print(f"task {args.id} deleted")


def build_parser():
    p = argparse.ArgumentParser(prog="tasks_cli.py", description="Markdown-backed task manager")
    sub = p.add_subparsers(dest="command", required=True)

    add_p = sub.add_parser("add", help="add a task")
    add_p.add_argument("title")
    add_p.add_argument("--priority", choices=VALID_PRIORITIES, default="med")
    add_p.set_defaults(func=cmd_add)

    list_p = sub.add_parser("list", help="list tasks")
    list_p.add_argument("--all", action="store_true", help="include done tasks")
    list_p.set_defaults(func=cmd_list)

    done_p = sub.add_parser("done", help="mark a task done")
    done_p.add_argument("id", type=int)
    done_p.set_defaults(func=cmd_done)

    rm_p = sub.add_parser("rm", help="delete a task")
    rm_p.add_argument("id", type=int)
    rm_p.set_defaults(func=cmd_rm)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
