# LTO Tracker Parser — GSheet Structure & Parser Notes

**Source**: `LU_COL_ENGINE_V4` → tab `LTO` (GID: `2144443698`)
**Output**: `10_OPERATION_DATA/04_LTO_Weekly_Log.md`

---

## GSheet Structure (Actual)

| Col | Label | Notes |
|-----|-------|-------|
| 0 | `L'Usine - LTO Feedback Daily Log All dropdowns linked to _Lists | Date format: yyyy-mm-dd Date` | **Date** (GSheet Date format) |
| 1 | `Store` | Store code: `LU3`, `LU5`, `LU7` (short names) |
| 2 | `LTO` | LTO campaign name |
| 3 | `Dish` | Dish name |
| 4 | `Qty Sold` | Quantity sold |
| 5 | `Rating (1-5)` | Customer rating |
| 6 | `Complaints` | Complaints text |
| 7 | `Positive Feedback` | Positive feedback text |
| 8 | `Negative / Improvement` | Negative feedback text |
| 9 | `Staff/Kitchen/Bar Notes` | Internal notes |

---

## Key Observations

| Aspect | Detail |
|--------|--------|
| **Store names** | Short: `LU3`, `LU5`, `LU7` (not the long codes) |
| **Date format** | GSheet `Date(2026,5,8)` format (month 0-indexed) |
| **No target columns** | No Target_Qty, Target_Revenue in sheet |
| **Rating** | 1-5 scale, used for emoji flags |

---

## Parser Logic (v3.0)

```python
STORES = ["LU3-LTT-Q1", "LU5-CM-Q7", "LU7-SC-Q1"]  # GSheet uses short names
STORE_NORMALIZE = {
    "LU3": "LU3", "LU3-LTT-Q1": "LU3",
    "LU5": "LU5", "LU5-CM-Q7": "LU5",
    "LU7": "LU7", "LU7-SC-Q1": "LU7",
}

# Date column detection (fuzzy)
ci_date = None
for i, col in enumerate(cols):
    label = (col.get("label") or "").strip().lower()
    if label == "date" or "date" in label:
        ci_date = i
        break
if ci_date is None:
    ci_date = 0

# Other columns by label
ci_store = cm.get("Store")
ci_lto = cm.get("LTO")
ci_dish = cm.get("Dish")
ci_qty = cm.get("Qty Sold")
ci_rating = cm.get("Rating (1-5)")
ci_complaints = cm.get("Complaints")
ci_positive = cm.get("Positive Feedback")
ci_negative = cm.get("Negative / Improvement")
ci_notes = cm.get("Staff/Kitchen/Bar Notes")
```

### Filter Week (Mon-Sun)

```python
start_int = int(week_start.strftime("%Y%m%d"))
end_int = int(week_end.strftime("%Y%m%d"))

for row in rows:
    d = gviz_cell(row, ci_date)
    if d is None: continue
    try:
        d_str = str(d).strip()
        m = re.match(r"Date\((\d+),(\d+),(\d+)\)", d_str)
        if m:
            d_parsed = date(int(m.group(1)), int(m.group(2)) + 1, int(m.group(3)))
        else:
            d_parsed = date.fromisoformat(d_str[:10])
        d_int = int(d_parsed.strftime("%Y%m%d"))
    except (TypeError, ValueError, AttributeError):
        continue

    if start_int <= d_int <= end_int:
        store_raw = gviz_cell(row, ci_store)
        # Accept any store starting with LU3, LU5, LU7
        if store_raw and (store_raw.startswith("LU3") or store_raw.startswith("LU5") or store_raw.startswith("LU7")):
            result.append(row)
```

---

## Parsing

```python
def parse_row(row, col_indices):
    cm, ci_date, ci_store, ci_lto, ci_dish, ci_qty, ci_rating, ci_complaints, ci_positive, ci_negative, ci_notes = col_indices
    def get(idx): return gviz_cell(row, cm.get(idx)) if cm.get(idx) is not None else None

    store_raw = get(ci_store)
    return {
        "store_raw": store_raw,
        "store": STORE_NORMALIZE.get(store_raw, store_raw),
        "lto_name": get(ci_lto) or "",
        "dish": get(ci_dish) or "",
        "qty": int(get(ci_qty)) if get(ci_qty) else 0,
        "revenue": 0,  # No revenue column
        "rating": float(get(ci_rating)) if get(ci_rating) else 0,
        "complaints": get(ci_complaints) or "",
        "positive": get(ci_positive) or "",
        "negative": get(ci_negative) or "",
        "notes": get(ci_notes) or "",
    }
```

---

## Aggregation

- Group by store → group by LTO name
- Sum qty, track rating average, count complaints/positive
- Attainment %: N/A (no targets in sheet)

### Output Table (per store)

| LTO Item | Dish | Qty | Avg Rating | Flag |
|----------|------|-----|------------|------|
| campaña | Dish Name | 150 | 4.2 ✅ | |

---

## Store Name Handling

**GSheet uses short names**: `LU3`, `LU5`, `LU7`
**Previous parsers expected**: `LU3-LTT-Q1`, `LU5-CM-Q7`, `LU7-SC-Q1`

```python
STORES = ["LU3-LTT-Q1", "LU5-CM-Q7", "LU7-SC-Q1"]  # For filtering
STORE_NORMALIZE = {
    "LU3": "LU3", "LU3-LTT-Q1": "LU3",
    "LU5": "LU5", "LU5-CM-Q7": "LU5",
    "LU7": "LU7", "LU7-SC-Q1": "LU7",
}

# In filter: match by prefix
if store_raw and store_raw.startswith("LU3"): result.append(row)

# In parse row:
"store": STORE_NORMALIZE.get(store_raw, store_raw),
```

---

## Output Format

Follows standardized format. Since no targets:
- Executive Summary: total qty, ratings
- Flags: 🔴 avg rating <3.5, 🟡 3.5-4.0, ✅ ≥4.0
- Systemwide roll-up → per store LTO items table with avg rating emoji
- No attainment % (no targets)

---

## Notes

- Week W24 data may be empty (stores haven't entered data yet)
- Historical weeks (W23, W22) show full data in log
- Parser handles empty weeks gracefully (writes "no LTO this week")