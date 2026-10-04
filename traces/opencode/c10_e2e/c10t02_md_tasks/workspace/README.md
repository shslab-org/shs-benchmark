# Markdown Task Manager

Tasks are stored as human-editable markdown files in a tasks directory
(override with the `TASKS_DIR` env var, default `./tasks`).

Each task is one file: `task_NNNN.md` (id is a stable small integer).
File contents:

```markdown
# Title

status: open
priority: high
```

## Usage

```
python tasks_cli.py add <title> [--priority low|med|high]
python tasks_cli.py list [--all]
python tasks_cli.py done <id>
python tasks_cli.py rm <id>
```

- `add` creates a new task with a fresh id (next integer after the max existing).
- `list` prints open tasks as a table of id, status, priority, title; `--all` includes done ones.
- `done` flips a task's status to `done` (rewrites the markdown file).
- `rm` deletes the task file.

Example:

```sh
export TASKS_DIR=./tasks
python tasks_cli.py add "Write docs" --priority high
python tasks_cli.py list
python tasks_cli.py done 1
python tasks_cli.py list --all
```
