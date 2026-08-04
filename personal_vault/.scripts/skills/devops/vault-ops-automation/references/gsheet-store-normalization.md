# GSheet Store Name Normalization

## Problem
GSheet store names include location codes: `LU3-LTT-Q1`, `LU5-CM-Q7`, `LU7-SC-Q1`
Internal codebase uses: `LU3`, `LU5`, `LU7`

## Solution: Prefix-based Fuzzy Match + Explicit Map

```python
STORES = ["LU3-LTT-Q1", "LU5-CM-Q7", "LU7-SC-Q1"]

STORE_NORMALIZE = {
    "LU3-LTT-Q1": "LU3",
    "LU5-CM-Q7": "LU5",
    "LU7-SC-Q1": "LU7",
}

# In parser: accept any store starting with LU3/LU5/LU7
if store_raw and (store_raw.startswith("LU3") or store_raw.startswith("LU5") or store_raw.startswith("LU7")):
    result.append(row)

# Normalize for internal use
store = STORE_NORMALIZE.get(store_raw, store_raw)
```

## Pattern: Prefix Match for Future-Proofing

```python
# Instead of exact match, use prefix
if any(s in store_raw for s in ["LU3", "LU5", "LU7"]):
    # Accept LU3-LTT-Q1, LU3-NewLocation, etc.
    store = next(s for s in ["LU3", "LU5", "LU7"] if s in store_raw)
```

## Where Applied

| Parser | Store Column | Normalization |
|--------|--------------|---------------|
| Hourly Cover | `Outlet` (LU3-LTT-Q1) | Exact map + prefix fallback |
| Item Sales | `Outlet` (LU3-LTT-Q1) | Exact map + prefix fallback |
| LTO | `Store` (LU3, LU5, LU7) | Prefix match (already short) |
| COL Weekly | `Store` (LU3, LU5, LU7) | Exact match |
| Reviews/GrabFood | `Store` (LU3, LU5, LU7) | Exact map |

## Key Insight

GSheet store names are **longer** (include location code) while internal names are **short**.
Always normalize at parse time, store internal codes in logs.