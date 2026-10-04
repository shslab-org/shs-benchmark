#!/usr/bin/env python3
"""tasks_cli.py - markdown-backed task manager.

Tasks live as human-editable markdown files, one per task, inside a
tasks directory (path taken from the TASKS_DIR environment variable,
defaulting to ./tasks).

Each task file is named ``<id>.md`` (e.g. ``0001.md``) and contains::

    # Buy groceries

    - status: open
    - priority: med

Commands:
    add <title> [--priority low|med|high]
    list [--all]
    done <id>
    rm <id>
"""

from __future__ import annotations

import argparse
import os
import re
import sys

# Bookkeeping file: records every id ever assigned so ids stay stable and
# are never reused after a task is deleted (tasks/1..n.md are the only
# files the CLI writes).
IDS_FILE = ".ids"

PRIORITIES = ("low", "med", "high")
STATUSES = ("open", "done")

# --- file layout -----------------------------------------------------------

TASK_FILE_RE = re.compile(r"^(\d+)\.md$")


def tasks_dir() -> str:
    """Return the tasks directory (TASKS_DIR env var, default ./tasks)."""
    return os.environ.get("TASKS_DIR", "./tasks")


def ensure_tasks_dir() -> str:
    """Return the tasks directory, creating it if it does not exist."""
    d = tasks_dir()
    os.makedirs(d, exist_ok=True)
    return d


def id_filename(task_id: int) -> str:
    """Canonical filename for a task id: 4-digit zero-padded + .md."""
    return f"{task_id:04d}.md"


def id_path(task_id: int) -> str:
    return os.path.join(tasks_dir(), id_filename(task_id))


def ids_file_path() -> str:
    return os.path.join(tasks_dir(), IDS_FILE)


def read_used_ids() -> set[int]:
    """Ids ever assigned (from the .ids bookkeeping file)."""
    used: set[int] = set()
    path = ids_file_path()
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.isdigit():
                    used.add(int(line))
    return used


def record_id(task_id: int) -> None:
    """Remember an assigned id in the .ids bookkeeping file."""
    path = ids_file_path()
    used = read_used_ids()
    if task_id in used:
        return
    used.add(task_id)
    with open(path, "w", encoding="utf-8") as f:
        for tid in sorted(used):
            f.write(f"{tid}\n")


def list_task_ids() -> list[int]:
    """All existing task ids in the tasks directory, ascending."""
    d = tasks_dir()
    ids: set[int] = read_used_ids()
    if os.path.isdir(d):
        for name in os.listdir(d):
            m = TASK_FILE_RE.match(name)
            if m:
                ids.add(int(m.group(1)))
    return sorted(ids)


def next_id() -> int:
    """Stable ids: 1, 2, 3, ... never reused (max ever-assigned + 1).

    Deletion does not recycle ids: the .ids bookkeeping file keeps every
    id that has ever been handed out.
    """
    used = read_used_ids()
    return (max(used) + 1) if used else 1


# --- markdown parsing / writing --------------------------------------------

_HEADING_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
# group(1) = the field value (rest of the line after the key)
_STATUS_RE = re.compile(r"^\s*-\s*status:\s*(\S+)\s*$", re.MULTILINE)
_PRIORITY_RE = re.compile(r"^\s*-\s*priority:\s*(\S+)\s*$", re.MULTILINE)


def render_task(title: str, status: str, priority: str) -> str:
    """Render a task markdown file's full content."""
    return (
        f"# {title}\n\n"
        f"- status: {status}\n"
        f"- priority: {priority}\n"
    )


def parse_task_file(path: str) -> dict:
    """Parse a task markdown file into {title, status, priority}.

    Tolerant of human edits: missing fields fall back to defaults so a
    hand-edited file does not crash the CLI.
    """
    with open(path, encoding="utf-8") as f:
        text = f.read()
    m = _HEADING_RE.search(text)
    title = m.group(1) if m else "(untitled)"
    m = _STATUS_RE.search(text)
    status = m.group(1).strip() if m else "open"
    m = _PRIORITY_RE.search(text)
    priority = m.group(1).strip() if m else "med"
    return {"title": title, "status": status, "priority": priority}


def load_tasks() -> list[dict]:
    """All tasks as [{id, title, status, priority}, ...] ascending by id.

    Ids whose .md file is missing (deleted but remembered in .ids) are
    skipped.
    """
    out: list[dict] = []
    for tid in list_task_ids():
        path = id_path(tid)
        if not os.path.isfile(path):
            continue
        rec = parse_task_file(path)
        rec["id"] = tid
        out.append(rec)
    return out


def require_task_id(task_id: int) -> str:
    """Validate that a task id exists; return its file path or exit(1)."""
    if task_id not in list_task_ids():
        print(f"error: task {task_id} not found", file=sys.stderr)
        sys.exit(1)
    return id_path(task_id)


# --- commands ----------------------------------------------------------------


def cmd_add(args: argparse.Namespace) -> None:
    ensure_tasks_dir()
    tid = next_id()
    record_id(tid)
    path = id_path(tid)
    with open(path, "w", encoding="utf-8") as f:
        f.write(render_task(args.title, "open", args.priority))
    print(f"added task {tid}: {args.title} ({args.priority})")


def cmd_list(args: argparse.Namespace) -> None:
    tasks = load_tasks()
    if not args.all:
        tasks = [t for t in tasks if t["status"] != "done"]
    if not tasks:
        print("no tasks")
        return
    headers = ("id", "status", "priority", "title")
    rows = [
        (str(t["id"]), t["status"], t["priority"], t["title"]) for t in tasks
    ]
    widths = [max(len(h), *(len(r[i]) for r in rows)) for i, h in enumerate(headers)]
    line = "  ".join(h.ljust(w) for h, w in zip(headers, widths)).rstrip()
    print(line)
    print("  ".join("-" * w for w in widths))
    for r in rows:
        print("  ".join(v.ljust(w) for v, w in zip(r, widths)).rstrip())


def cmd_done(args: argparse.Namespace) -> None:
    path = require_task_id(args.id)
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if _STATUS_RE.search(text):
        # Replace the value (group 1) with "done"; group 0 contains the
        # full line, so we rebuild it.
        text = re.sub(
            r"(^\s*-\s*status:\s*)\S+",
            r"\1done",
            text,
            count=1,
            flags=re.MULTILINE,
        )
    else:
        # Human edited the file and dropped the status line: append one.
        if not text.endswith("\n"):
            text += "\n"
        text += "- status: done\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"task {args.id} marked done")


def cmd_rm(args: argparse.Namespace) -> None:
    path = require_task_id(args.id)
    os.remove(path)
    print(f"deleted task {args.id}")
    # Id is intentionally NOT removed from the .ids bookkeeping file:
    # ids stay stable and are never reused.


# --- CLI ----------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="tasks_cli.py",
        description="Markdown-backed task manager "
        "(tasks dir: $TASKS_DIR, default ./tasks)",
    )
    sub = p.add_subparsers(dest="command", required=True)

    pa = sub.add_parser("add", help="add a new task")
    pa.add_argument("title", help="task title")
    pa.add_argument(
        "--priority",
        choices=PRIORITIES,
        default="med",
        help="task priority (default: med)",
    )
    pa.set_defaults(func=cmd_add)

    pl = sub.add_parser("list", help="list open tasks (or all with --all)")
    pl.add_argument("--all", action="store_true", help="include done tasks")
    pl.set_defaults(func=cmd_list)

    pd = sub.add_parser("done", help="mark a task as done")
    pd.add_argument("id", type=int, help="task id")
    pd.set_defaults(func=cmd_done)

    pr = sub.add_parser("rm", help="delete a task")
    pr.add_argument("id", type=int, help="task id")
    pr.set_defaults(func=cmd_rm)
    return p


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
