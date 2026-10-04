# Task API Documentation

In-memory task management API. All data is held in process memory and is not persisted.

---

## create_task(title: str) -> dict

Creates a new task with the given title, assigns it a unique integer id, and marks it as not done.

Returns a dict with keys `"id"` (int), `"title"` (str), and `"done"` (False).

**Example:**

```python
>>> create_task("Buy groceries")
{"id": 1, "title": "Buy groceries", "done": False}
```

---

## list_tasks() -> list[dict]

Returns a copy of the list of all tasks currently in memory.

Each element is a task dict as returned by `create_task`.

**Example:**

```python
>>> create_task("Buy groceries")
{"id": 1, "title": "Buy groceries", "done": False}
>>> list_tasks()
[{"id": 1, "title": "Buy groceries", "done": False}]
```

---

## complete_task(task_id: int) -> dict

Marks the task with the given id as done (`done=True`) and returns the updated task dict.

Raises `ValueError` if no task has the given id.

**Example:**

```python
>>> complete_task(1)
{"id": 1, "title": "Buy groceries", "done": True}
```

---

## delete_task(task_id: int) -> None

Removes the task with the given id from the in-memory store.

Raises `ValueError` if no task has the given id.

**Example:**

```python
>>> delete_task(1)
>>> list_tasks()
[]
```
