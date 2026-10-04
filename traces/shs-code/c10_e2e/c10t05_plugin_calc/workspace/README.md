# Plugin-Style Calculator

A minimal **core + plugins** architecture.

The core (`calculator.py`) knows nothing about arithmetic — it only
stores and dispatches named operations. All concrete math lives in
independent plugins under `plugins/`.

## Files

```
calculator.py        # Core: Calculator (register, calculate, operations)
plugins/
  __init__.py
  add.py             # registers "add"
  subtract.py        # registers "subtract"
  multiply.py        # registers "multiply"
  divide.py          # registers "divide" (raises ZeroDivisionError on 0)
main.py              # Wires core + plugins, prints four examples
tests/
  test_calculator.py # pytest suite
```

## Quick start

```bash
python main.py
```

Expected output:

```
Registered operations: ['add', 'divide', 'multiply', 'subtract']

2 + 2 = 4
10 - 4 = 6
3 * 3 = 9
9 / 2 = 4.5
```

## Adding a new plugin (3 steps)

1. **Create a module** `plugins/your_op.py` that exposes a private
   function and a `register(calc)` factory:

   ```python
   def _your_op(a, b):
       return a % b          # example: modulo

   def register(calc):
       calc.register("your_op", _your_op)
   ```

2. **Import and wire it in `main.py`**:

   ```python
   from plugins import your_op
   your_op.register(calc)
   ```

3. **Add a test** in `tests/test_calculator.py` under a new
   `TestYourOpPlugin` class, following the existing pattern.

That's it — the core never changes.

## Running the tests

```bash
python -m pytest tests/ -v
```
