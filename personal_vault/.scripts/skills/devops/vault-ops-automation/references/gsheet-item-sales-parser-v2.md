# Item Sales (Star Horse) Parser Pattern

## Source
- **Sheet**: LU_COL_ENGINE_V4
- **Tab**: "Star Horse" / Item Sales (GID: 72569880)
- **Format**: Row per item per store per week (summary, no Date/Store columns per row)

## Actual Columns
| Index | Label | Description |
|-------|-------|-------------|
| 0 | Outlet | Store identifier (LU3-LTT-Q1, LU5-CM-Q7, LU7-SC-Q1) |
| 1 | Item group | Category in Ikko POS (All-day Breakfast, Mains, Coffee, etc.) |
| 2 | Item | Menu item name |
| 3 | Measurement unit | Phần/Ly/Chai/Lon/serv |
| 4 | Grand Total Order items | Qty sold per store per week |
| 5 | Gross Sales (after discount), VND | Revenue (VND) |
| 6 | Cost per unit, VND | Avg ingredient cost per unit |

## Parser Logic

```python
def parse_item_sales(rows):
    by_store = {"LU3": [], "LU5": [], "LU7": []}
    STORES = ["LU3-LTT-Q1", "LU5-CM-Q7", "LU7-SC-Q1"]
    STORE_NORMALIZE = {s: s.split("-")[0] for s in STORES}
    
    for row in rows:
        cells = row.get("c", [])
        if len(cells) < 7: continue
        
        # Outlet column has "Outlet" in label (not "Store")
        outlet_idx = find_column_by_label(cols, "outlet")
        store_raw = gviz_cell(row, outlet_idx)
        if not store_raw or store_raw not in STORES:
            continue
        
        by_store[STORE_NORMALIZE[store_raw]].append({
            "item_group": gviz_cell(row, ci_item_group),
            "item": gviz_cell(row, ci_item),
            "unit": gviz_cell(row, ci_unit),
            "qty": int(float(gviz_cell(row, ci_qty) or 0)),
            "revenue": float(gviz_cell(row, ci_rev) or 0),
            "cost": float(gviz_cell(row, ci_cost) or 0),
        })
    
    # Aggregate by item per store
    # Build entry with Executive Summary → Systemwide → Store breakdown
```

## Key Differences from Other Parsers

| Aspect | Standard Weekly Logs | Star Horse (Item Sales) |
|--------|---------------------|------------------------|
| Date column | Yes (per row) | No (weekly summary) |
| Store column | Yes (per row) | Yes (Outlet) |
| Granularity | Daily per store | Weekly per item per store |
| Delta calc | vs prev week | vs prev week (from log) |

## Store Normalization

```python
STORES = ["LU3-LTT-Q1", "LU5-CM-Q7", "LU7-SC-Q1"]
STORE_NORMALIZE = {
    "LU3-LTT-Q1": "LU3",
    "LU5-CM-Q7": "LU5", 
    "LU7-SC-Q1": "LU7",
}
```

## Output Format (Standardized)

```markdown
## 2026-W24 | 08/06–14/06/2026

### 📋 Executive Summary
- **System**: 47 total units | 10.8tr rev | 3 stores active
- **Top concern**: LU5 Avocado Toast 4.0 underperforming (18 units vs LU3's 14)
- **Key Takeaway**: LU3 leading breakfast sales; LU5 needs promotional support

### ⚡ Flags
- ✅ All stores positive revenue
- 🟡 LU5 breakfast items below LU3 benchmark

### Weekly Roll-up (Δ vs W23)
| Store | Qty | Rev (tr) | Δ Qty | Δ Rev |
| LU3 | 14 | 3.1 | +0 | +0.0 |
| LU5 | 18 | 4.2 | +0 | +0.0 |
| LU7 | 15 | 3.5 | +0 | +0.0 |

### Store-level Breakdown
### LU3: 14 qty | 3.1tr rev
| Item Group | Item | Qty | Revenue | Avg Price |
| All-day Breakfast | Avocado Toast 4.0 | 14 | 3.1tr | 54,869đ |
```

## No Date Filtering Needed
The sheet is already a weekly snapshot — all rows belong to the target week. Parse all rows, aggregate by store.