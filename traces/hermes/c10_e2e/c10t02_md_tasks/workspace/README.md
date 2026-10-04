# tasks_cli.py — markdown-backed task manager

Tasks live as human-editable markdown files, one per task, in a tasks
directory chosen by the `TASKS_DIR` environment variable (default: `./tasks`).

Each task file is named `<id>.md` and looks like:

    # Buy groceries
    Status: open
    Priority: med

IDs are stable small integers assigned in creation order (1, 2, 3, ...).
The next id is always `max(existing) + 1`, so a deleted id is never reused
(its slot stays open).

## Usage

```
python tasks_cli.py add <title> [--priority low|med|high]
python tasks_cli.py list [--all]
python tasks_cli.py done <id>
python tasks_cli.py rm <id>
```

- `add` creates a new task file with the title as a markdown heading, a
  `Status: open` line, and a `Priority:` line (default priority: `med`).
- `list` prints open tasks as a table (`ID | STATUS | PRIORITY | TITLE`);
  `--all` includes done tasks.
- `done <id>` flips the task's status to `done` in its markdown file.
- `rm <id>` deletes the task file.

## Examples

```sh
export TASKS_DIR=$HOME/tasks   # or leave unset to use ./tasks

python tasks_cli.py add "Write report" --priority high
python tasks_cli.py add "Buy milk"
python tasks_cli.py list        # open tasks only
python tasks_cli.py done 2      # mark "Buy milk" done
python tasks_cli.py list --all  # open + done
python tasks_cli.py rm 1        # delete "Write report"
```

## File format

The CLI is line-oriented and tolerant: it reads the first `# ` line as the
title and the `Status:` / `Priority:` lines wherever they appear. If you edit
a file by hand (rename the task, change the priority, flip `Status:` to
`done`), `list` reflects your edits on the next run. If a `Status:` line is
missing, `done` adds one just below the title heading.

Files that don't match the `<digits>.md` pattern are ignored by `list`.
