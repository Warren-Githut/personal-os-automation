# GSheet Column Detection Debug Pattern

## Problem
GSheet tabs have varying column labels. Parsers need to map semantic columns (Date, Store, Hour, etc.) to actual column indices.

## Solution: Auto-detection + Fallback

```python
def filter_week(cols, rows, week_start, week_end):
    cm = build_col_map(cols)
    
    # Debug: print ALL columns with indices
    print(f"🔍 Columns ({len(cols)}):")
    for i, col in enumerate(cols):
        label = col.get("label", f"col_{i}")
        print(f"  [{i}] {label}")
    
    # Auto-detect by label keywords
    def find_col(keywords):
        for i, col in enumerate(cols):
            label = (col.get("label") or "").strip().lower()
            if any(kw in label for kw in keywords):
                return i
        return None
    
    ci_outlet = find_col(["outlet", "store"])
    ci_date = find_col(["date"])
    ci_hour = find_col(["hour", "opening"])
    # ... etc
    
    # Fallback: positional (if known structure)
    if ci_outlet is None:
        ci_outlet = 0  # first column often store/outlet
```

## Keywords by Semantic Type

| Semantic | Keywords |
|----------|----------|
| Store/Outlet | `outlet`, `store`, `branch` |
| Date | `date`, `ngày` |
| Hour | `hour`, `opening hour`, `giờ` |
| Covers/Guests | `guest`, `cover`, `khách`, `number of guests` |
| Revenue/Sales | `sales`, `revenue`, `gross sales`, `doanh thu`, `vnd` |
| Item/Product | `item`, `product`, `dish`, `menu` |
| Quantity | `qty`, `quantity`, `số lượng`, `order items` |
| Category | `category`, `group`, `item group`, `type` |

## Debug Output Example

```
🔍 Columns (7):
  [0] history_11_Item_Sales_Weekly_Log_Star_Horse Period: from 6/1/2026 to 6/7/2026 Outlet
  [1] Item group
  [2] Item
  [3] Measurement unit
  [4] Grand Total Order items
  [5] Gross Sales (after discount), VND
  [6] Cost per unit, VND
   Outlet=0, Item_group=1, Item=2, Qty=4, Rev=5, Cost=6
```