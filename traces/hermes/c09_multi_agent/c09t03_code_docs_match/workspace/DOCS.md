# api.py — Task API Documentation

This document describes the in-memory task API provided by `api.py` in this directory.

## create_task

def create_task(title: str) -> dict:

Creates and stores a new task with the given title, returning its task record.

```python
t = create_task("Buy milk")  # -> {"id": 1, "title": "Buy milk", "done": False}
```

## list_tasks

def list_tasks() -> list[dict]:

Returns a list of all task records currently stored.

```python
list_tasks()  # -> [{"id": 1, "title": "Buy milk", "done": False}]
```

## complete_task

def complete_task(task_id: int) -> dict:

Marks the task with the given id as complete and returns its record; raises ValueError on unknown ids.

```python
complete_task(1)  # -> {"id": 1, "title": "Buy milk", "done": True}
```

## delete_task

def delete_task(task_id: int) -> None:

Removes the task with the given id; raises ValueError on unknown ids.

```python
delete_task(1)  # -> None
```
