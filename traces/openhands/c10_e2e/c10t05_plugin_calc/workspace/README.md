# Plugin Calculator

A minimal calculator **core** (`calculator.py`) that accepts **plugins**
(`plugins/*.py`) registering named operations.

## Layout

- `calculator.py` — the `Calculator` core: `register`, `calculate`, `operations`.
- `plugins/` — one module per operation, each exposing `register(calc)`.
- `main.py` — wires core + plugins and demos `2+2`, `10-4`, `3*3`, `9/2`.
- `tests/` — pytest suite for the core and the plugins.

## Running

```bash
python main.py
pytest
```

## How to add a new plugin (3 steps)

1. **Create the module**: add `plugins/mean.py` with the operation and a
   `register(calc)` hook:

   ```python
   """Plugin registering the "mean" operation."""


   def _mean(a, b):
       return (a + b) / 2


   def register(calc):
       calc.register("mean", _mean)
   ```

2. **Wire it up**: import the plugin in `main.py` and add it to `PLUGINS`:

   ```python
   from plugins import add, divide, mean, multiply, subtract

   PLUGINS = [add, subtract, multiply, divide, mean]
   ```

3. **Test it**: add a test in `tests/test_calculator.py` and include the
   plugin in the fixture, e.g. `assert calc.calculate("mean", 2, 4) == 3.0`.

That's it — the core needs no changes.
