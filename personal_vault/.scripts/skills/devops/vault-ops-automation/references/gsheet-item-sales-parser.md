# Item Sales (Star Horse) Parser — GSheet Structure & Parser Notes

**Source**: `LU_COL_ENGINE_V4` → tab `Star Horse` (GID: `72569880`)
**Output**: `10_OPERATION_DATA/11_Item_Sales_Weekly_Log_Star_Horse_Tracker.md`

---

## GSheet Structure (Actual)

| Col | Label | Notes |
|-----|-------|-------|
| 0 | `history_11_Item_Sales_Weekly_Log_Star_Horse Period: from 6/1/2026 to 6/7/2026 Outlet` | Contains **Outlet** (store code) |
| 1 | `Item group` | Category (e.g., "All-day Breakfast") |
| 2 | `Item` | Menu item name |
| 3 | `Measurement unit` | Unit (Phần, Ly, Chai, etc.) |
| 4 | `Grand Total Order items` | Qty sold |
| 5 | `Gross Sales (after discount), VND` | Revenue (gross) |
| 6 | `Cost per unit, VND` | Avg cost/unit |

---

## Key Observations

| Aspect | Detail |
|--------|--------|
| **Store names** | `LU3-LTT-Q1`, `LU5-CM-Q7`, `LU7-SC-Q1` (same format as Hourly Cover) |
| **No Date/Day columns** | Sheet is weekly summary per store per item |
| **Revenue** | Gross Sales (need ×0.882 for net if comparing with COL) |
| **Aggregation** | Per store per item per week |

---

## Parser Logic (v3.0)

```python
STORES = ["LU3-LTT-Q1", "LU5-CM-Q7", "LU7-SC-Q1"]
STORE_NORMALIZE = {
    "LU3-LTT-Q1": "LU3",
    "LU5-CM-Q7": "LU5",
    "LU7-SC-Q1": "LU7",
}

# Outlet column detection (fuzzy)
ci_outlet = None
for i, col in enumerate(cols):
    label = (col.get("label") or "").strip().lower()
    if "outlet" in label:
        ci_outlet = i
        break
if ci_outlet is None: ci_outlet = 0

ci_item_group = cm.get("Item group")
ci_item = cm.get("Item")
ci_qty = cm.get("Grand Total Order items")
ci_rev = cm.get("Gross Sales (after discount), VND")
ci_cost = cm.get("Cost per unit, VND")
```

### Filter Week
Since no date column, **all rows in sheet belong to current week**. Filter only by store name:

```python
for row in rows:
    store_raw = gviz_cell(row, ci_outlet)
    if store_raw and store_raw in STORES:
        result.append(row)
```

---

## Parsing

```python
def parse_row(row, col_indices):
    cm, ci_outlet, ci_item_group, ci_item, ci_unit, ci_qty, ci_rev, ci_cost = col_indices
    def get(idx): return gviz_cell(row, cm.get(idx)) if cm.get(idx) is not None else None
    
    store_raw = get(ci_outlet)
    return {
        "store_raw": store_raw,
        "store": STORE_NORMALIZE.get(store_raw, store_raw),
        "item_group": get(ci_item_group) or "",
        "item": get(ci_item) or "",
        "unit": get(ci_unit) or "",
        "qty": int(get(ci_qty)) if get(ci_qty) else 0,
        "revenue": float(get(ci_rev)) if get(ci_rev) else 0,
        "avg_price": float(get(ci_cost)) if get(ci_cost) else 0,
    }
```

---

## Aggregation

- Group by store
- Within store: group by (item_group, item)
- Top items by revenue
- Delta vs prev week: sum qty/rev per store

---

## Output Format

Follows standardized format: Executive Summary → Systemwide → Store-level with top items table.

| Store | Qty | Revenue | Top Items |
|-------|-----|---------|-----------|
| LU3   | 14  | 3.1tr   | Avocado Toast (14 qty, 3.1tr) |

---

## Notes

- No Date/Day columns → no daily breakdown possible
- Revenue is **Gross** (×0.882 for net if comparing with COL/Revenue logs)
- Prev week delta works via log file parsing (same pattern as other parsers)