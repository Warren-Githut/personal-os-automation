# VAULT_ROOT Double-`vault/` Path Bug — Reference

## Pattern
Multiple scripts in Warren_OS_Local define:
```python
VAULT_ROOT = Path(__file__).parent.parent  # → resolves to .../Warren_OS_Local/vault/
```
Then incorrectly append `"vault/"` again:
```python
path = VAULT_ROOT / "vault" / "10_OPERATION_DATA" / src  # WRONG → vault/vault/10_OPERATION_DATA/
```

## Affected Scripts (fixed in this session)
| Script | Bug | Fix |
|--------|-----|-----|
| `regenerate_today.py` | `VAULT_ROOT / "vault" / "scripts" / "generate_today_revenue.py"` | `VAULT_ROOT / "scripts" / "generate_today_revenue.py"` |
| `regenerate_today.py` | `VAULT_ROOT / "vault" / "00_CORE_LOGIC" / "TODAY.md"` | `VAULT_ROOT / "00_CORE_LOGIC" / "TODAY.md"` |
| `auto_process_logs_gsheet.py` | `VAULT_ROOT / "vault" / "10_OPERATION_DATA" / src` | `VAULT_ROOT / "10_OPERATION_DATA" / src` |

## Root Cause
`__file__` = `.../Warren_OS_Local/vault/scripts/<script>.py`
`Path(__file__).parent.parent` = `.../Warren_OS_Local/vault/` ← already the vault root

## Detection
- Script prints `[ERROR] ... not found` for files that exist
- `ls` shows file at `vault/10_OPERATION_DATA/` but script checks `vault/vault/10_OPERATION_DATA/`

## Prevention
1. When writing new scripts using `VAULT_ROOT`, **log the resolved path** on startup:
   ```python
   print(f"VAULT_ROOT = {VAULT_ROOT}")
   ```
2. Run a quick existence check before assuming path structure.
3. Use `VAULT_ROOT / "10_OPERATION_DATA"` directly — no intermediate `"vault/"`.

## Session Evidence
- 2026-06-15: Fixed both `regenerate_today.py` and `auto_process_logs_gsheet.py` in same session
- Both had identical pattern: `VAULT_ROOT` already vault/, appended "vault/" again
- Fix verified by re-running scripts → all ✅ EXISTS