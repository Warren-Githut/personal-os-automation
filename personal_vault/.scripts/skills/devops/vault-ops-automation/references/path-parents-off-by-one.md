# `Path.parents` Off-by-One — Reference

## Pattern

When resolving paths relative to a file deep in the package tree, `Path.parents[n]` indexing is off-by-one if you forget `parents[0]` is the same as `.parent`.

### Symptom

```python
# File at: vault/scripts/lusine-ops/lusine_ops/telegram_bot.py
VAULT_SCRIPTS = Path(__file__).resolve().parents[1].parent / "scripts"
```

Intent: get `vault/scripts/`.  
Result: **`vault/scripts/scripts/`** → import fails with `ModuleNotFoundError`.

### Why

```
__file__ = .../vault/scripts/lusine-ops/lusine_ops/telegram_bot.py
.resolve() = .../vault/scripts/lusine-ops/lusine_ops/telegram_bot.py

.parent            = .../vault/scripts/lusine-ops/lusine_ops/
.parents[0]        = .../vault/scripts/lusine-ops/lusine_ops/    ← SAME as .parent
.parents[1]        = .../vault/scripts/lusine-ops/
.parents[1].parent = .../vault/scripts/
/ "scripts"        = .../vault/scripts/scripts/                  ← WRONG!
```

### Fix

```python
VAULT_SCRIPTS = Path(__file__).resolve().parents[2]  # → vault/scripts/  ✅
```

`.parents[n]` skips **n** ancestor directories from the file. For a file at depth D from target:
- **D = 2** (file is 2 dirs below target): use `parents[2]`
- **D = 3**: use `parents[3]`
- Never chain `.parent.parent[1].parent / "something"` — it's almost always wrong.

### Quick mental model

```
file:  a/b/c/d/e/f.py
.parent            → a/b/c/d/e/
.parents[0]        → a/b/c/d/e/     (same as .parent)
.parents[1]        → a/b/c/d/
.parents[2]        → a/b/c/
.parents[3]        → a/b/
```

To reach `a/b/` from `f.py`: `parents[3]` ✅ — because you skip 3 levels (e/, d/, c/).

## Detection

- Error: `ModuleNotFoundError: No module named 'xxx'` when the module clearly exists on disk
- The sys.path entry is `.../vault/scripts/scripts/` (doubled last segment)
- `print(sys.path)` at startup reveals the doubled segment

## Real occurrence

**File:** `vault/scripts/lusine-ops/lusine_ops/telegram_bot.py` (2026-06-29)

Original code (inherited from old skill location):
```python
VAULT_SCRIPTS = Path(__file__).resolve().parents[1].parent / "scripts"
```

Path resolution was `.../vault/scripts/scripts/` instead of `.../vault/scripts/`.

This was **masked** when the batch file set `PYTHONPATH` explicitly to `vault/scripts/` — the wrong sys.path entry was harmless because PYTHONPATH came first. After removing PYTHONPATH and switching to `pip install -e`, the wrong entry became the only entry → `ModuleNotFoundError`.

**Fix:** `Path(__file__).resolve().parents[2]`

## Prevention

1. Before deploying a `Path(__file__).resolve().parents[...]` expression, **run a quick debug print** to verify:
   ```python
   print(f"RESOLVED: {Path(__file__).resolve()}")
   print(f"TARGET:   {Path(__file__).resolve().parents[N]}")
   ```
2. Avoid chaining `.parent` and `.parents` in the same expression — use `parents[N]` consistently.
3. When a script uses `sys.path.insert(0, ...)` with a computed path, log the inserted path at startup for traceability.
