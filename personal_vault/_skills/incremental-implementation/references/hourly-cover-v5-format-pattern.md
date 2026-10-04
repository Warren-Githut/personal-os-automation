# Hourly Cover Revenue Log v5.0 — Format Pattern

> Reusable pattern for redesigning weekly operational logs to 60% machine / 40% human format.
> Applied 2026-07-06 to `09_Hourly_Cover_Revenue_Log.md`. Saved 21% tokens (291 lines) with compression of 6 older weeks.

## The Hybrid Format (60% Machine / 40% Human)

### Entry structure (6 sections, in order):
```
1. ### 📊 Data          — JSON block (1-line compact, Hermes parses this)
2. ### Executive Summary — 3 bullets (human skimmable)
3. ### 🔥 Decision Board — Flag 🟢🟡🔴 + FBM recommend per store
4. ### Hourly Detail     — Markdown tables (M T W T F S S day headers)
5. ### MTD               — Month-to-date table
6. ### 📈 Dashboard      — Link to HTML dashboard
```

### JSON Block Schema (Compact, 1 line)
```json
{"week_id":"2026-W27","period":"29/06-05/07/2026","rev":601524000,"covers":2526,"stores":[{"id":"LU3","c":892,"r":198450000,"rc":222478},{"id":"LU5","c":778,"r":211680000,"rc":272082},{"id":"LU7","c":856,"r":191394000,"rc":223591}],"vs":{"covers_pct":5.8,"revenue_pct":-3.8}}
```

**Compact vs pretty-printed:** 315 chars vs 3,208 chars (**90% smaller**). Dropped full hourly arrays (data stays in markdown tables). Shortened field names (`c`=covers, `r`=revenue, `rc`=rev/cover, `vs`=vs_prior_week). Hourly arrays only needed in JSON when Hermes needs programmatic access per-hour — for weekly summary dashboard, store-level aggregates suffice.

**Older pretty-printed version** (use only when hourly programmatic access needed):
```json
{
  "week_id": "2026-W26",
  "period": "22/06–28/06/2026",
  "net_revenue_total": 625468000,
  "total_actual_covers": 2387,
  "total_gross_covers": 2764,
  "total_split_orders": 377,
  "stores": [
    {"id": "LU3", "actual_covers": 836, ...}
  ],
  "hourly": {...},  // 2,800+ chars
  "vs_prior_week": {"covers_pct": -5.3, "revenue_pct": -9.2}
}
```

### Revenue Unit
- **M** (triệu VND), round to 1 decimal
- `round(value / 1_000_000, 1)` — e.g. `2,759,000` → `2.8M`
- Display: `covers·revenue_M` — e.g. `10·2.8M`

### Day Headers
- 1-letter: `M T W T F S S` (Mon Tue Wed Thu Fri Sat Sun)
- Column alignment: `:--:|` for day columns

### Decision Board
| Flag | Store | Detail | 🧑‍🍳 FBM Recommend |
| 🟢 | LU5 | Good metric | Concrete action |
| 🟡 | LU7 | Watch item | Check specific area |
| 🔴 | LU3 | Critical | **Action item** |

### What to Drop from Old Format
- ALL table (derivable from 3 stores)
- Conversion section (move to frontmatter once)
- Cross-check (only log when >2% discrepancy)
- Weekly Roll-up (data already in JSON + Decision Board)

### Old Week Compression
Replace verbose sections with:
```
## 2026-W25 | 15/06–21/06/2026
<!-- ⏤ Compressed — data archived in dashboard HTML. -->
```

## Dashboard HTML Pattern
- Vanilla HTML + Chart.js 4.x CDN
- Colors: LU3 `#CCFF99`, LU5 `#4CAF50`, LU7 `#1B5E20`, Sys `#2196F3`, BG `#E8F5E9`
- Use `.replace("{PLACEHOLDER}", value)` pattern (NOT f-strings) to avoid JS/Python quoting conflicts
- Manage chart instances manually (`let charts = []` + `makeChart()` + `destroyAll()`)
- Pass weeks array as parameter to helper functions (closure bug prevention)
