# Markdown Task Manager

A small task manager where every task is stored as a human-editable
markdown file.

## Setup

Tasks are stored in the directory given by the `TASKS_DIR` environment
variable (default: `./tasks`). Each task is one file named after its
stable integer id, e.g. `3.md`:

```markdown
# Buy milk

Status: open
Priority: high
```

You can edit these files directly; the CLI only cares about the
`Status:` and `Priority:` lines.

## Usage

```
python tasks_cli.py <command> [args]
```

### add

Create a new task:

```
python tasks_cli.py add "Buy milk" --priority high
```

- `--priority` accepts `low`, `med`, `high` (default: `med`).
- The id is assigned automatically as the next free small integer.

### list

Print open tasks as a table of `id`, `status`, `priority`, `title`:

```
python tasks_cli.py list          # open tasks only
python tasks_cli.py list --all    # open and done tasks
```

### done

Flip a task's status to `done` (updates its markdown file):

```
python tasks_cli.py done 3
```

### rm

Delete the task file entirely:

```
python tasks_cli.py rm 3
```

## Example session

```
$ export TASKS_DIR=./tasks
$ python tasks_cli.py add "Write report" --priority high
Added task 1: Write report
$ python tasks_cli.py add "Buy milk"
Added task 2: Buy milk
$ python tasks_cli.py list
id  status  priority  title
--  ------  --------  -------------
1   open    high      Write report
2   open    med       Buy milk
$ python tasks_cli.py done 2
Task 2 marked as done
$ python tasks_cli.py list --all
id  status  priority  title
--  -----   --------  -------------
1   open    high      Write report
2   done    med       Buy milk
$ python tasks_cli.py rm 1
Removed task 1
```
