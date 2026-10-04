# GSheet Pivot Table Parser Pattern

## Problem
Some GSheet tabs (e.g., `Hourly_Revenue` in `LU_COL_ENGINE_V4`) use **pivot table format** instead of flat rows:

| Store | Hour | Order Type | Mon Covers | Mon Revenue | Tue Covers | Tue Revenue | ... |
|-------|------|------------|------------|-------------|------------|-------------|-----|
| LU3-LTT-Q1 | 07 | Dine-in | 5 | 1.2M | 3 | 0.8M | ... |
| LU5-CM-Q7 | 08 | Takeaway | 10 | 2.5M | ... | ... | ... |

- Rows = Store × Hour
- Columns = daily metrics (covers + revenue per day)
- Headers often duplicated (e.g., "Gross Sales (after discount), VND" repeated for all 7 days)

## Solution: Parse by Column Position

```python
# Map day columns by fixed position (not header text)
# Col 3: Mon covers, Col 5: Mon revenue, Col 6: Tue covers, Col 7: Tue revenue...
day_names = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
covers_idx = 3
for i, day in enumerate(day_names):
    day_cols[day] = {"covers": covers_idx, "revenue": covers_idx + 2}
    covers_idx += 3  # covers, empty, revenue = 3 cols per day
```

Then detect headers as fallback for validation.

## Store Name Normalization

GSheet uses full outlet names; parser outputs internal codes:

```python
STORES = ["LU3-LTT-Q1", "LU5-CM-Q7", "LU7-SC-Q1"]
STORE_NORMALIZE = {
    "LU3-LTT-Q1": "LU3",
    "LU5-CM-Q7": "LU5",
    "LU7-SC-Q1": "LU7",
}
```

## Output Format

```markdown
## 2026-W24 | 08/06–14/06/2026

### LU3: 798350 covers | 10.5tr rev
| Day | Covers | Revenue |
|-----|--------|---------|
| T2  | 9      | 2.7tr   |

**Peak day (T5) hourly:**
| Hour | Covers | Revenue |
|------|--------|---------|
| 07:00 | 798336 | 1.1tr   |

### Weekly Roll-up: 849655 covers | 15.2tr rev
```

## Key Implementation Details

1. **Parse each row → emit (store, hour, day, covers, revenue) entries**
2. **Aggregate by store → daily totals + hourly breakdown for peak day**
3. **Delta vs previous week** (requires parsing previous week from log file)
4. **Exit 0 on "no data"** — not an error; just means GSheet not populated yet