"""Unit tests for the in-memory task API in api.py.

Run with:  pytest test_api.py   (or)   python -m unittest test_api.py
"""

import importlib.util
import pathlib
import unittest


def _load_api():
    """Load api.py fresh so module-level state starts clean each test."""
    base = pathlib.Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location("api", base / "api.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod._tasks.clear()
    mod._next_id = 1
    return mod


class TestCreateTask(unittest.TestCase):
    def setUp(self):
        self.api = _load_api()

    def test_returns_expected_shape(self):
        t = self.api.create_task("Buy groceries")
        self.assertEqual(t, {"id": 1, "title": "Buy groceries", "done": False})

    def test_ids_increment(self):
        t1 = self.api.create_task("a")
        t2 = self.api.create_task("b")
        self.assertEqual(t2["id"], t1["id"] + 1)


class TestListTasks(unittest.TestCase):
    def setUp(self):
        self.api = _load_api()

    def test_empty_by_default(self):
        self.assertEqual(self.api.list_tasks(), [])

    def test_creation_order(self):
        self.api.create_task("a")
        self.api.create_task("b")
        self.api.create_task("c")
        self.assertEqual([t["id"] for t in self.api.list_tasks()], [1, 2, 3])

    def test_reflects_mutation_of_store(self):
        t = self.api.create_task("a")
        self.api.complete_task(t["id"])
        self.assertIs(self.api.list_tasks()[0]["done"], True)


class TestCompleteTask(unittest.TestCase):
    def setUp(self):
        self.api = _load_api()

    def test_marks_done_and_returns_task(self):
        t = self.api.create_task("a")
        out = self.api.complete_task(t["id"])
        self.assertIs(out["done"], True)
        self.assertEqual(out, {"id": 1, "title": "a", "done": True})

    def test_unknown_id_raises(self):
        with self.assertRaises(ValueError):
            self.api.complete_task(999)


class TestDeleteTask(unittest.TestCase):
    def setUp(self):
        self.api = _load_api()

    def test_returns_none_and_removes(self):
        t = self.api.create_task("a")
        self.assertIsNone(self.api.delete_task(t["id"]))
        self.assertEqual(self.api.list_tasks(), [])

    def test_unknown_id_raises(self):
        with self.assertRaises(ValueError):
            self.api.delete_task(999)


if __name__ == "__main__":
    unittest.main()
