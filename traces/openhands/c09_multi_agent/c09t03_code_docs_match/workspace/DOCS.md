# Task API Documentation

## create_task

```python
create_task(title: str) -> dict
```

Creates a new in-memory task and returns `{"id": int, "title": str, "done": False}`.

Example:

```python
task = create_task("Buy milk")
```

## list_tasks

```python
list_tasks() -> list[dict]
```

Returns all tasks in creation order.

Example:

```python
tasks = list_tasks()
```

## complete_task

```python
complete_task(task_id: int) -> dict
```

Marks the given task as done (`done=True`) and returns the updated task; raises `ValueError` for an unknown `task_id`.

Example:

```python
task = complete_task(1)
```

## delete_task

```python
delete_task(task_id: int) -> None
```

Deletes the given task; raises `ValueError` for an unknown `task_id`.

Example:

```python
delete_task(1)
```
