# GSheet Parser Fixes — Session 2026-06-14

## Systematic Bugs Fixed Across Multiple Parsers

### 1. VAULT_ROOT Path Depth Bug
**Affected parsers:** `col_weekly_parser.py`, `cogs_parser.py`, `google_review_parser.py`, `grabfood_parser.py`

**Root cause:** Parsers live in `vault/10_OPERATION_DATA/parsers/` but write to `vault/10_OPERATION_DATA/`. The path depth was `parent.parent.parent` (3 levels) but needs `parent.parent.parent.parent` (4 levels) because:
```
parsers/col_weekly_parser.py → parsers/ → 10_OPERATION_DATA/ → vault/ → Warren_OS_Local/
                                         ↑ LOG_FILE parent
```

**Fix pattern:**
```python
# WRONG
VAULT_ROOT = Path(__file__).parent.parent.parent
LOG_FILE = VAULT_ROOT / "vault" / "10_OPERATION_DATA" / "07_COL_Weekly_Log.md"

# CORRECT
VAULT_ROOT = Path(__file__).parent.parent.parent.parent
LOG_FILE = VAULT_ROOT / "vault" / "10_OPERATION_DATA" / "07_COL_Weekly_Log.md"
```

### 2. cv() vs gviz_cell() Import Bug
**Affected parsers:** `google_review_parser.py`, `grabfood_parser.py`, `col_weekly_parser.py` (had both)

**Root cause:** Parsers imported `cv` from `_utils` but `_utils.py` only exports `gviz_cell`. The `cv` function never existed.

**Fix pattern:** Replace all `cv(row, col_index)` with `gviz_cell(row, col_index)`:
```python
# WRONG
from _utils import cv, fetch_gviz, ...
store_name = cv(row, COL_STORE)

# CORRECT
from _utils import fetch_gviz, gviz_cell, ...
store_name = gviz_cell(row, COL_STORE)
```

### 3. Missing Helper Functions in _utils
**Affected parser:** `grabfood_parser.py`

**Root cause:** Used `parse_gviz_datetime()` and `datetime` but neither was imported or defined.

**Fix:** Add helper function directly in parser:
```python
from datetime import date, datetime, timedelta

def parse_gviz_datetime(raw) -> date | None:
    if raw is None:
        return None
    s = str(raw).strip()
    m = re.match(r"DateTime\((\d+),(\d+),(\d+),(\d+),(\d+),(\d+)\)", s)
    if m:
        return datetime(int(m.group(1)), int(m.group(2)) + 1, int(m.group(3)),
                       int(m.group(4)), int(m.group(5)), int(m.group(6))).date()
    try:
        return date.fromisoformat(s[:10])
    except ValueError:
        return None
```

### 4. Exit Code for "No Data" in Cron
**Affected parser:** `grabfood_parser.py`

**Root cause:** Parser exited with code 1 when no data for current week, causing cron job to report failure.

**Fix:** Exit 0 on "no data yet" — it's a warning, not failure:
```python
if not curr_p and not curr_a:
    print(f"\n⚠️  0 rows for {week_id}. No GSheet data yet — skipping write.")
    print(f"⚡ Warren: enter W{iso_week:02d} data into the 'Grabfood' GSheet tab, then re-run the parser.")
    # Exit 0 for cron: no data = warning, not failure
    sys.exit(0)
```

### 5. Headless Mode for Cron
**Pattern:** All GSheet parsers respect `LUSINE_HEADLESS=1` via `_utils._ask()`:
```python
# In _utils.py _ask():
if os.environ.get("LUSINE_HEADLESS") == "1":
    print(f"{prompt}{default} [headless auto]")
    return default
```

**Cron invocation:**
```bash
LUSINE_HEADLESS=1 PYTHONPATH="..." python parser.py
```

Or in Python subprocess:
```python
env = os.environ.copy()
env["LUSINE_HEADLESS"] = "1"
env["PYTHONPATH"] = str(parser_modules_dir)
subprocess.run([sys.executable, str(script)], cwd=parser_modules_dir, env=env, ...)
```

---

## Monday Morning Cron Sequence (Final)

```
08:30  → Daily Case Sweep (daily_case_sweep.py)
09:00  → Weekly Vault Lint (/ops-lint --quick)
09:30  → Daily Today Revenue Report (generate_today_revenue.py)
09:45  → Monday GSheet Parsers (run_monday_gsheet_parsers.py)
       ├── COL Weekly (col_weekly_parser.py)
       ├── COGS Supplier (cogs_parser.py)
       ├── Google Reviews (google_review_parser.py)
       ├── GrabFood (grabfood_parser.py)
       └── Hourly Cover* (hourly_cover_parser.py - TBD)
10:00  → Daily TODAY Regeneration (regenerate_today.py)
10:30  → Auto Process-Logs GSheet (auto_process_logs_gsheet.py)
```

*Hourly Cover parser TBD — add to run_monday_gsheet_parsers.py when created.

---

## GSheet Source Mapping (All in LU_COL_ENGINE_V4)

| Data | Tab | GID | Parser | Log File |
|------|-----|-----|--------|----------|
| COL / Working Hours | COL_Weekly_ | 1732633441 | col_weekly_parser.py | 07_COL_Weekly_Log.md |
| COGS Supplier | PRICE_CHANGE | 865155568 | cogs_parser.py | 03_COGS_Supplier_Monthly_Log.md |
| Google Reviews | Google Review Log | 762945748 | google_review_parser.py | 05_Google_Review_Weekly_Log.md |
| GrabFood | Grabfood | 689394201 | grabfood_parser.py | 06_GrabFood_Weekly_Log.md |
| Hourly Cover | Lu_Hourly_Revenue | TBD | hourly_cover_parser.py | 09_Hourly_Cover_Revenue_Log.md |

---

## Files Modified in This Session

| File | Changes |
|------|---------|
| `vault/10_OPERATION_DATA/parsers/col_weekly_parser.py` | VAULT_ROOT depth + urllib imports + `detect_week→week_bounds` + `get_prev_week→prev_week_bounds` + timedelta import |
| `vault/10_OPERATION_DATA/parsers/cogs_parser.py` | VAULT_ROOT depth fix |
| `vault/10_OPERATION_DATA/parsers/google_review_parser.py` | VAULT_ROOT depth fix |
| `vault/10_OPERATION_DATA/parsers/grabfood_parser.py` | VAULT_ROOT depth + cv→gviz_cell + parse_gviz_datetime + exit 0 on no data |
| `vault/scripts/run_monday_gsheet_parsers.py` | Added COGS parser + LUSINE_HEADLESS=1 env + PYTHONPATH for _utils |
| `vault/scripts/regenerate_today.py` | New: daily TODAY.md refresh wrapper |
| `vault/scripts/auto_process_logs_gsheet.py` | New: verify automated sources |
| `vault/00_CORE_LOGIC/CONTEXT.md` | Updated data cadence + automation table |
| `vault/00_CORE_LOGIC/CONTEXT.md` | Updated data cadence + automation table |

---

## Verification Commands

```bash
# Test all Monday parsers (headless)
python vault/scripts/run_monday_gsheet_parsers.py

# Test individual parsers
LUSINE_HEADLESS=1 PYTHONPATH="vault/10_OPERATION_DATA/scripts/modules" python vault/10_OPERATION_DATA/parsers/col_weekly_parser.py
LUSINE_HEADLESS=1 PYTHONPATH="vault/10_OPERATION_DATA/scripts/modules" python vault/10_OPERATION_DATA/parsers/cogs_parser.py
LUSINE_HEADLESS=1 PYTHONPATH="vault/10_OPERATION_DATA/scripts/modules" python vault/10_OPERATION_DATA/parsers/google_review_parser.py
LUSINE_HEADLESS=1 PYTHONPATH="vault/10_OPERATION_DATA/scripts/modules" python vault/10_OPERATION_DATA/parsers/grabfood_parser.py

# Verify cron jobs
hermes cronjob list
```