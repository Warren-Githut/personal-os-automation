# GSheet Parser Template — Standard Pattern

All automated GSheet parsers in `vault/10_OPERATION_DATA/parsers/` follow this template.
Source: `LU_COL_ENGINE_V4` (Sheet ID: `1ZtIocc_Ic1z-tO1JGd4ZLnRB_7ZHHkvpJ5emaWJyeEE`)

## Template Structure

```python
#!/usr/bin/env python3
"""
<Parser Name> v1.0
Source: <Tab Name> tab in LU_COL_ENGINE_V4 Google Sheet
Output: 10_OPERATION_DATA/<target_log>.md
"""

import io
import os
import sys
import urllib.request
import urllib.error
import json
import re
from datetime import date, timedelta
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from _utils import fetch_gviz, gviz_cell, build_col_map, week_bounds, prev_week_bounds, make_week_id

SHEET_ID  = "1ZtIocc_Ic1z-tO1JGd4ZLnRB_7ZHHkvpJ5emaWJyeEE"
SHEET_GID = "<GID>"  # tab "<Tab Name>" — rename-safe
VAULT_ROOT = Path(__file__).parent.parent.parent.parent
LOG_FILE   = VAULT_ROOT / "vault" / "10_OPERATION_DATA" / "<target_log>.md"

STORES = ["LU3", "LU5", "LU7"]

# ── Fetch ─────────────────────────────────────────────────────────────────────

def fetch_sheet():
    url = (
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
        f"/gviz/tq?tqx=out:json&gid={SHEET_GID}"
    )
    try:
        with urllib.request.urlopen(url, timeout=20) as resp:
            text = resp.read().decode("utf-8")
    except urllib.error.URLError as e:
        print(f"ERROR: Không kết nối được GSheet — {e}\nKiểm tra internet hoặc thử lại sau.")
        sys.exit(1)
    match = re.search(r"google\.visualization\.Query\.setResponse\(([\s\S]*)\)", text)
    if not match:
        raise ValueError("Cannot parse gviz response")
    table = json.loads(match.group(1))["table"]
    return table["cols"], table["rows"]

# ── Filter & parse ────────────────────────────────────────────────────────────

def filter_week(cols, rows, week_start, week_end):
    cm = build_col_map(cols)
    ci_date  = cm.get("Date")
    ci_store = cm.get("Store")
    start_int = int(week_start.strftime("%Y%m%d"))
    end_int   = int(week_end.strftime("%Y%m%d"))
    result = []
    for row in rows:
        d = gviz_cell(row, ci_date)
        if d is None:
            continue
        try:
            d_int = int(d)
        except (TypeError, ValueError):
            continue
        if start_int <= d_int <= end_int:
            store = gviz_cell(row, ci_store)
            if store in STORES:
                result.append(row)
    return result, cm

def parse_row(row, cm):
    def get(name):
        return gviz_cell(row, cm.get(name))

    return {
        "date":      int(get("Date") or 0),
        "day":       get("Day") or "",
        "store":     get("Store") or "",
        # --- ADD DOMAIN-SPECIFIC FIELDS HERE ---
    }

# ── Aggregation ───────────────────────────────────────────────────────────────

def store_agg(parsed_rows, store):
    # Filter & sort by date
    days = sorted(
        [r for r in parsed_rows if r["store"] == store],
        key=lambda x: x["date"]
    )
    if not days:
        return None
    # Aggregate totals & per-item breakdown
    return {
        "days": days,
        "total_qty": sum(r["qty"] for r in days),
        "total_rev": sum(r["revenue"] for r in days),
        # ...
    }

# ── Build entry (prepend/replace by week_id) ──────────────────────────────────

def build_entry(week_start, week_end, parsed_rows, prev_parsed_rows=None):
    iso_week = week_start.isocalendar()[1]
    week_id  = f"{week_start.year}-W{iso_week:02d}"
    date_range = f"{week_start.strftime('%d/%m')}–{week_end.strftime('%d/%m/%Y')}"

    L = [f"## {week_id} | {date_range}", ""]

    for store in STORES:
        agg = store_agg(parsed_rows, store)
        if not agg:
            L.append(f"### {store}: (no data)")
            L.append("")
            continue

        # Delta vs prev week
        delta = ""
        if prev_parsed_rows:
            prev_agg = store_agg(prev_parsed_rows, store)
            if prev_agg and prev_agg.get("total_rev"):
                dq = agg["total_qty"] - prev_agg["total_qty"]
                dr = agg["total_rev"] - prev_agg["total_rev"]
                delta = f" ({dq:+} qty) ({dr/1e6:+.1f}tr rev)"

        L.append(f"### {store}: {agg['total_qty']} | {agg['total_rev']/1e6:.1f}tr{delta}")
        L.append("")

        # Domain-specific table (top items, LTO attainment, etc.)
        # ...

    # Weekly roll-up
    total_qty = sum(r["qty"] for r in parsed_rows)
    total_rev = sum(r["revenue"] for r in parsed_rows)
    L.append(f"### Weekly Roll-up: {total_qty} qty | {total_rev/1e6:.1f}tr rev")
    if prev_parsed_rows:
        prev_qty = sum(r["qty"] for r in prev_parsed_rows)
        prev_rev = sum(r["revenue"] for r in prev_parsed_rows)
        L.append(f"Δ vs W{iso_week-1:02d}: {total_qty - prev_qty:+} qty | {(total_rev - prev_rev)/1e6:+.1f}tr rev")
    L.append("")
    L.append("---")
    return "\n".join(L)

# ── Write log (prepend/replace by week_id) ────────────────────────────────────

def run():
    week_start, week_end = week_bounds()
    iso_week = week_start.isocalendar()[1]
    week_id = f"{week_start.year}-W{iso_week:02d}"

    print(f"📅 Target: {week_id} — {week_start.strftime('%d/%m')} → {week_end.strftime('%d/%m/%Y')}")
    print("📊 Fetching <Source> sheet...")

    cols, rows = fetch_sheet()

    # Current week
    filtered, cm = filter_week(cols, rows, week_start, week_end)
    expected = len(STORES) * 7
    print(f"📊 Current week: {len(filtered)} rows (expected ~{expected})")

    parsed = [parse_row(r, cm) for r in filtered]

    # Previous week (for delta)
    prev_start, prev_end = prev_week_bounds(week_start)
    prev_filtered, _ = filter_week(cols, rows, prev_start, prev_end)
    prev_parsed = [parse_row(r, cm) for r in prev_filtered] if prev_filtered else []
    print(f"📊 Prev week: {len(prev_filtered)} rows")

    entry = build_entry(week_start, week_end, parsed, prev_parsed)

    # Write log (prepend/replace)
    if LOG_FILE.exists():
        existing = LOG_FILE.read_text(encoding="utf-8")
        pattern = rf"(## {re.escape(week_id)}.*?)(?=\n## |\Z)"
        replaced = re.sub(pattern, "", existing, flags=re.DOTALL).strip()

        if week_id in existing:
            print(f"⚠️  Entry {week_id} already in log. Overwriting...")
            new_content = entry + "\n\n---\n\n" + replaced if replaced else entry + "\n"
        else:
            print(f"INFO: Adding new entry for {week_id}")
            new_content = entry + "\n\n---\n\n" + existing if existing else entry + "\n"
    else:
        print(f"INFO: {LOG_FILE.name} not found — creating new.")
        new_content = entry + "\n"

    LOG_FILE.write_text(new_content, encoding="utf-8")
    print(f"\n✅ Written → {LOG_FILE.relative_to(VAULT_ROOT)}")

if __name__ == "__main__":
    run()
```

## Required Imports from `_utils`

```python
from _utils import fetch_gviz, gviz_cell, build_col_map, week_bounds, prev_week_bounds, make_week_id
```

## Cron Integration

Add to `run_monday_gsheet_parsers.py`:

```python
{
    "name": "<Parser Name>",
    "script": VAULT_ROOT / "10_OPERATION_DATA" / "parsers" / "<parser_name>.py",
    "output": "<target_log>.md",
    "required": False,  # True for COL, COGS
    "headless": True,
}
```

## Run Command (for testing)

```bash
LUSINE_HEADLESS=1 PYTHONPATH="C:/Users/khoans/Documents/Warren_OS_Local/vault/10_OPERATION_DATA/scripts/modules" python "../../../10_OPERATION_DATA/parsers/<parser_name>.py"
```

## Common Fixes When Porting Legacy Parsers

| Issue | Fix |
|-------|-----|
| `cv(row, col)` | → `gviz_cell(row, col)` |
| `detect_week()` | → `week_bounds()` (from _utils) |
| `get_prev_week(ws)` | → `prev_week_bounds(ws)` (from _utils) |
| Missing `urllib.request` / `urllib.error` | Add imports at top |
| Missing `timedelta` / `datetime` | Add `from datetime import date, datetime, timedelta` |
| `VAULT_ROOT` wrong depth | `Path(__file__).parent.parent.parent.parent` |
| `LOG_FILE` path has double `vault/` | `VAULT_ROOT / "vault" / "10_OPERATION_DATA" / "xxx.md"` |
| Exit 1 on no data | Exit 0 (cron: no data = warning, not failure) |
| `_ask()` prompts in headless | Use `LUSINE_HEADLESS=1` env |

## Existing Parser Examples (in `vault/10_OPERATION_DATA/parsers/`)

| Parser | Tab / GID | Output Log |
|--------|-----------|------------|
| `col_weekly_parser.py` | COL_Weekly_ / 1732633441 | 07_COL_Weekly_Log.md |
| `cogs_parser.py` | PRICE_CHANGE / 865155568 | 03_COGS_Supplier_Monthly_Log.md |
| `google_review_parser.py` | Google Review Log / 762945748 | 05_Google_Review_Weekly_Log.md |
| `grabfood_parser.py` | Grabfood / 689394201 | 06_GrabFood_Weekly_Log.md |
| `item_sales_parser.py` | Star Horse / 72569880 | 11_Item_Sales_Weekly_Log_Star_Horse_Tracker.md |
| `lto_parser.py` | LTO / 2144443698 | 04_LTO_Weekly_Log.md |
| `hourly_cover_parser.py` | Hourly_Revenue / TBD | 09_Hourly_Cover_Revenue_Log.md (TBD) |

## Source of Truth

All parsers read from **single GSheet**: `LU_COL_ENGINE_V4` (ID: `1ZtIocc_Ic1z-tO1JGd4ZLnRB_7ZHHkvpJ5emaWJyeEE`)
Different tabs separated by `gid` parameter.