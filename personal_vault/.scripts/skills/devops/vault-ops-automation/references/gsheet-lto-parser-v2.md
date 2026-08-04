# LTO Weekly Tracker Parser Pattern

## Source
- **Sheet**: LU_COL_ENGINE_V4
- **Tab**: "LTO" (GID: 2144443698)
- **Format**: Row per LTO transaction (Date + Store + LTO + Dish + Qty + Rating + Feedback fields)

## Actual Columns
| Index | Label | Description |
|-------|-------|-------------|
| 0 | Date | GSheet Date format: `Date(2026,5,10)` = 2026-06-10 |
| 1 | Store | LU3-LTT-Q1 / LU5-CM-Q7 / LU7-SC-Q1 (prefix match) |
| 2 | LTO | Campaign name (LTO Drink Summer, MATCHA ERA, POWER LUNCH) |
| 3 | Dish | Specific item name |
| 4 | Qty Sold | Integer |
| 5 | Rating (1-5) | Customer rating |
| 6 | Complaints | Text |
| 7 | Positive Feedback | Text |
| 8 | Negative / Improvement | Text |
| 9 | Staff/Kitchen/Bar Notes | Text |

## Parser Logic

```python
def parse_lto(rows):
    by_store = {"LU3": [], "LU5": [], "LU7": []}
    
    for row in rows:
        cells = row.get("c", [])
        if len(cells) < 6: continue
        
        # Parse GSheet date: Date(2026,5,10) → 2026-06-10
        d_cell = cells[0].get("v") if cells[0] else None
        m = re.match(r"Date\((\d+),(\d+),(\d+)\)", str(d_cell))
        if m:
            d = date(int(m.group(1)), int(m.group(2))+1, int(m.group(3)))
        
        if not (week_start <= d <= week_end): continue
        
        store_raw = cells[1].get("v") if cells[1] else None
        if not store_raw: continue
        
        # Fuzzy store match by prefix
        store_code = None
        for k in ["LU3", "LU5", "LU7"]:
            if store_raw.startswith(k):
                store_code = k
                break
        
        by_store[store_code].append({
            "lto": cells[2].get("v") or "",
            "dish": cells[3].get("v") or "",
            "qty": int(float(cells[4].get("v") or 0)),
            "rating": float(cells[5].get("v") or 0) if cells[5].get("v") else 0,
        })
```

## Date Parsing

```python
# GSheet Date format: Date(year, month-1, day)
m = re.match(r"Date\((\d+),(\d+),(\d+)\)", str(d_cell))
if m:
    d = date(int(m.group(1)), int(m.group(2))+1, int(m.group(3)))
```

## Store Name Normalization

```python
STORE_NORMALIZE = {
    "LU3-LTT-Q1": "LU3",
    "LU5-CM-Q7": "LU5",
    "LU7-SC-Q1": "LU7",
}

# Fuzzy match by prefix
for k in ["LU3", "LU5", "LU7"]:
    if store_raw.startswith(k):
        store_code = k
        break
```

## Campaign-Based Aggregation

```python
ltos = {}
for i in items:
    name = i["lto"]  # Campaign name: "LTO Drink Summer", "MATCHA ERA", "POWER LUNCH"
    if name not in ltos:
        ltos[name] = {"qty": 0, "rating_sum": 0, "rating_cnt": 0, "dish": i["dish"]}
    ltos[name]["qty"] += i["qty"]
    if i["rating"]:
        ltos[name]["rating_sum"] += i["rating"]
        ltos[name]["rating_cnt"] += 1
```

## Output Format (Standardized)

```markdown
## 2026-W23 | 01/06–07/06/2026

### 📋 Executive Summary
- **System**: 87 total units | LU7 dominated with 76 units (POWER LUNCH)
- **Top performer**: LU7 with 76 units (POWER LUNCH 56 units)
- **Key Takeaway**: LU7 POWER LUNCH strong, LU5 Drink Summer underperforming

### ⚡ Flags
- 🔴 LU5 Drink Summer: 7/35 target (20%) — far below target
- ✅ LU7 POWER LUNCH: 56 units — strong execution
- 🟡 LU3 Drink Summer: 4 units only — limited rollout

### Weekly Roll-up (Δ vs W22)
| Store | Qty | vs W22 | Avg Rating |
| **LU3** | 4 | +4 | 4.7★ ✅ |
| **LU5** | 7 | +7 | 5.0★ ✅ |
| **LU7** | 76 | +76 | 4.0★ ✅ |

### Store-level Breakdown
### LU3: 4 qty (4.7★)
| LTO Item | Dish | Qty | Avg Rating |
| LTO Drink Summer | Lychee Sprizt | 3 | 5.0★ ✅ |

### LU5: 7 qty (5.0★)
| LTO Item | Dish | Qty | Avg Rating |
| LTO Drink Summer | Lychee Citrus Pritz | 5 | 5.0★ ✅ |

### LU7: 76 qty (4.0★)
| LTO Item | Dish | Qty | Avg Rating |
| POWER LUNCH | POWER LUNCH | 56 | 4.0★ ✅ |
| LTO Drink Summer | Dragonfruit Cloud Tea | 8 | 4.0★ ✅ |
```

## Key Notes

1. **No targets in sheet** — targets come from config/tracker, not GSheet
2. **Campaign-based grouping** — parse by LTO campaign name from column 2
3. **Week filtering by date** — filter by Date column (column 0)
4. **Rating is optional** — some rows have 0/no rating
5. **Store names use prefixes** — LU3-LTT-Q1, LU5-CM-Q7, LU7-SC-Q1