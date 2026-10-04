# Markdown-Backed Task Manager

A tiny task manager where every task is a plain, human-editable
markdown file. No database — just one `.md` file per task, so tasks
can be edited, versioned, and moved by hand.

## Layout

Tasks live in a directory taken from the `TASKS_DIR` environment
variable (default: `./tasks`). Each task is one file named
`<id>.md` with a 4-digit zero-padded id:

```
tasks/
  0001.md
  0002.md
```

Task 1's file (`tasks/0001.md`) looks like:

```markdown
# Buy groceries

- status: open
- priority: high
```

- **Title** — the `# ` heading.
- **Status** — a `- status: open|done` line.
- **Priority** — a `- priority: low|med|high` line.

IDs are stable small integers (1, 2, 3, …). A new task always gets
`max(existing id) + 1`, so ids are never reused after a delete.
The parser is tolerant of hand edits: missing fields fall back to
defaults (`open`, `med`) rather than crashing.

## Usage

```bash
python tasks_cli.py <command> [args]
```

Point the tasks directory somewhere else (optional):

```bash
export TASKS_DIR=/path/to/tasks
```

### `add` — create a task

```bash
python tasks_cli.py add "Buy groceries" --priority high
# added task 1: Buy groceries (high)

python tasks_cli.py add "Write report"
# added task 2: Write report (med)   # --priority defaults to med
```

Writes `<id>.md` into the tasks directory with the title as heading,
status `open`, and the chosen priority.

### `list` — show tasks

```bash
python tasks_cli.py list            # open tasks only
python tasks_cli.py list --all      # open + done
```

Prints a table with `id`, `status`, `priority`, `title` columns.
Prints `no tasks` when there is nothing to show.

### `done` — mark a task complete

```bash
python tasks_cli.py done 1
# task 1 marked done
```

Flips the `- status:` line in the task's markdown file to `done`
(all other lines are preserved). If the line was removed by hand
editing, a fresh `- status: done` line is appended.

### `rm` — delete a task

```bash
python tasks_cli.py rm 2
# deleted task 2
```

Deletes the task's markdown file. The id is not reused by later
`add` commands.

## Errors

Unknown task ids and other problems print an `error: ...` message to
stderr and exit non-zero, e.g.:

```bash
$ python tasks_cli.py done 99
error: task 99 not found
```

## Example session

```bash
export TASKS_DIR=~/demo-tasks

python tasks_cli.py add "Ship the demo" --priority high
python tasks_cli.py add "Write docs"
python tasks_cli.py list
# id  status  priority  title
# --  ------  --------  -----------
# 1   open    high      Ship the demo
# 2   open    med       Write docs

python tasks_cli.py done 1
python tasks_cli.py list
# 2   open    med       Write docs

python tasks_cli.py list --all
# 1   done    high      Ship the demo
# 2   open    med       Write docs

python tasks_cli.py rm 2
```
