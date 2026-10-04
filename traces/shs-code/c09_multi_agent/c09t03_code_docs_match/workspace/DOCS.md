# Task API Documentation

In-memory task store with four functions, all in `api.py`. State is kept in
module memory and resets on process restart.

## `create_task(title: str) -> dict`

Create a new task with a unique integer id and `done` initially `False`.

Example:

```python
from api import create_task

task = create_task("Buy groceries")
# -> {"id": 1, "title": "Buy groceries", "done": False}
```

## `list_tasks() -> list[dict]`

Return all stored tasks in creation order.

Example:

```python
from api import create_task, list_tasks

create_task("Write report")
create_task("Send emails")
print(list_tasks())
# -> [{"id": 1, "title": "Write report", "done": False},
#     {"id": 2, "title": "Send emails", "done": False}]
```

## `complete_task(task_id: int) -> dict`

Mark the task with the given id as `done=True` and return the updated task.

Raises `ValueError` if the id does not exist.

Example:

```python
from api import create_task, complete_task

task = create_task("File taxes")
print(complete_task(task["id"]))
# -> {"id": 1, "title": "File taxes", "done": True}
```

## `delete_task(task_id: int) -> None`

Remove the task with the given id. Returns nothing.

Raises `ValueError` if the id does not exist.

Example:

```python
from api import create_task, delete_task, list_tasks

task = create_task("Temp task")
delete_task(task["id"])
print(list_tasks())
# -> []
```
