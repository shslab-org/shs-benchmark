# Plugin-Style Calculator

Minimal CORE + independent PLUGINS architecture.

## Layout

- `calculator.py` - core `Calculator` class
- `plugins/` - one module per operation (add, subtract, multiply, divide)
- `main.py` - wires core + plugins, demonstrates usage
- `tests/test_calculator.py` - pytest suite

## Run

```bash
python main.py
python -m pytest
```

## How to add a new plugin (3 steps)

1. Create `plugins/your_op.py` with an operation function and a
   `register(calc)` function that calls `calc.register("your_op", your_op)`.

   ```python
   def pow(a, b):
       return a ** b

   def register(calc):
       calc.register("pow", pow)
   ```

2. Wire it in `main.py` (or wherever plugins are loaded):

   ```python
   from plugins import your_op
   your_op.register(calc)
   ```

3. Use it:

   ```python
   calc.calculate("pow", 2, 8)  # 256
   ```
