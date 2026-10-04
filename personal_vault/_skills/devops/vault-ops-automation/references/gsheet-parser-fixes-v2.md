# GSheet Parser Common Fixes (Session 2026-06-14)

## Windows Path Resolution for Vault Root

**Problem**: `VAULT_ROOT = Path(__file__).parent.parent.parent` resolves incorrectly when parser is at `vault/10_OPERATION_DATA/parsers/`

**Fix**:
```python
# Correct: 4 levels up from parsers/
VAULT_ROOT = Path(__file__).parent.parent.parent.parent
LOG_FILE = VAULT_ROOT / "vault" / "10_OPERATION_DATA" / "07_COL_Weekly_Log.md"
```

## Import Fixes for Parser Modules

All parsers must run from `10_OPERATION_DATA/scripts/modules/` for `_utils` imports:

```bash
# Cron job / manual run:
LUSINE_HEADLESS=1 PYTHONPATH="C:/Users/khoans/Documents/Warren_OS_Local/vault/10_OPERATION_DATA/scripts/modules" python ../../parsers/<parser>.py
```

In `run_monday_gsheet_parsers.py`:
```python
parser_modules_dir = VAULT_ROOT / "10_OPERATION_DATA" / "scripts" / "modules"
env = os.environ.copy()
env["PYTHONPATH"] = str(parser_modules_dir)
env["LUSINE_HEADLESS"] = "1"
subprocess.run([sys.executable, str(script)], cwd=parser_modules_dir, env=env, ...)
```

## Parser-Specific Fixes

### COL Weekly Parser (`col_weekly_parser.py`)
| Issue | Fix |
|-------|-----|
| `detect_week()` not defined | Use `week_bounds()` from `_utils` |
| Missing `timedelta` import | Add `from datetime import date, timedelta` |
| `cv()` undefined | Replace with `gviz_cell()` |
| VAULT_ROOT path | Add one more `.parent` |

### COGS Parser (`cogs_parser.py`)
| Issue | Fix |
|-------|-----|
| Form rows at top of sheet | Dynamic header detection (`find_header_row`) |
| VAULT_ROOT path | 4 levels up + `/vault` |
| Column labels vary | Dynamic column mapping by header labels |
| Header row buried | Scan first 20 rows for "item" + "supplier" |

### Google Reviews Parser (`google_review_parser.py`)
| Issue | Fix |
|-------|-----|
| VAULT_ROOT path | 4 levels up + `/vault` |
| `cv()` undefined | Replace with `gviz_cell()` |

### GrabFood Parser (`grabfood_parser.py`)
| Issue | Fix |
|-------|-----|
| VAULT Root path | 4 levels up + `/vault` |
| `cv()` undefined | Replace with `gviz_cell()` |
| `parse_gviz_datetime` missing | Add local function |
| `sys.exit(1)` on no data | Use `sys.exit(0)` for cron (no data = warning, not failure) |

```python
def parse_gviz_datetime(raw):
    """Parse GSheet datetime: 'DateTime(2026,5,8,14,30,0)' or ISO format."""
    if raw is None: return None
    s = str(raw).strip()
    m = re.match(r"DateTime\((\d+),(\d+),(\d+),(\d+),(\d+),(\d+)\)", s)
    if m:
        return datetime(int(m.group(1)), int(m.group(2))+1, int(m.group(3)),
                       int(m.group(4)), int(m.group(5)), int(m.group(6))).date()
    try:
        return date.fromisoformat(s[:10])
    except ValueError:
        return None
```

### Hourly Cover Parser (`hourly_cover_parser.py`)
| Issue | Fix |
|-------|-----|
| Pivot table format | Parse by column position (Store=0, Hour=1, OrderType=2, daily covers/revenue at fixed offsets) |
| Store normalization | `LU3-LTT-Q1` → `LU3`, `LU5-CM-Q7` → `LU5`, `LU7-SC-Q1` → `LU7` |
| Revenue columns same label | Map by position: covers at col 3,5,6,8,11,13,15,17,19,21; revenue at col 5,7,8,10,11,13,14,15,16,17,18,20 |
| `prev_parsed` from log | Parse previous week block from log file using regex |

```python
# Day columns by position (covers, empty, revenue)
day_cols = {"mon": {"covers": 3, "revenue": 5}, "tue": {"covers": 6, "revenue": 8}, ...}
```

### Item Sales Parser (`item_sales_parser.py`)
| Issue | Fix |
|-------|-----|
| No Date/Store columns | Sheet is weekly summary per item per store |
| Outlet column label | Find column with "Outlet" in label (not "Store") |
| Store names | `LU3-LTT-Q1`, `LU5-CM-Q7`, `LU7-SC-Q1` → normalize to LU3/LU5/LU7 |

### LTO Parser (`lto_parser.py`)
| Issue | Fix |
|-------|-----|
| Date column label | Search for "date" in label (not exact "Date") |
| Store names | Fuzzy match: `store_raw.startswith("LU3")` etc. |
| Date parsing | Handle `Date(2026,5,10)` format (month is 0-indexed) |
| No targets in sheet | Skip attainment %, compute avg rating instead |

## Runner Pattern (`run_monday_gsheet_parsers.py`)

```python
parser_modules_dir = VAULT_ROOT / "10_OPERATION_DATA" / "scripts" / "modules"
env = os.environ.copy()
env["PYTHONPATH"] = str(parser_modules_dir)
env["LUSINE_HEADLESS"] = "1"
result = subprocess.run(
    [sys.executable, str(script)],
    cwd=parser_modules_dir,
    env=env,
    capture_output=True,
    text=True,
    timeout=120,
)
```

## Cron Exit Codes
- Required parsers (COL, COGS): `sys.exit(1)` on failure
- Optional parsers (Reviews, GrabFood, Item Sales, LTO): `sys.exit(0)` on failure + log error
- No data in sheet: `sys.exit(0)` (warning, not failure)

## LUSINE_HEADLESS=1
All parsers must support `LUSINE_HEADLESS=1` env var for non-interactive cron runs.