# GSheet Parser Import Pattern — PYTHONPATH + LUSINE_HEADLESS

## Standard Invocation

All parsers in `vault/10_OPERATION_DATA/parsers/` must run from:
```
C:/Users/khoans/Documents/Warren_OS_Local/vault/10_OPERATION_DATA/scripts/modules/
```

With `PYTHONPATH` set to that directory for `_utils` imports.

## run_monday_gsheet_parsers.py Implementation

```python
parser_modules_dir = VAULT_ROOT / "10_OPERATION_DATA" / "scripts" / "modules"
env = os.environ.copy()
env["PYTHONPATH"] = str(parser_modules_dir)
if parser_info.get("headless", False):
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

## Manual Test Command

```bash
cd "C:/Users/khoans/Documents/Warren_OS_Local/vault/10_OPERATION_DATA/scripts/modules"
LUSINE_HEADLESS=1 PYTHONPATH="." python "../../../10_OPERATION_DATA/parsers/<parser_name>.py"
```

## LUSINE_HEADLESS Behavior

| Env Value | Behavior |
|-----------|----------|
| `LUSINE_HEADLESS=1` | Auto-returns default ("n") for all `_ask()` prompts — non-blocking |
| `LUSINE_FORCE=1` | Auto-returns "y" — force confirm |
| unset | Waits for interactive input (blocks cron) |

All cron jobs **MUST** set `LUSINE_HEADLESS=1`.

## _utils.py Imports Required

```python
from _utils import (
    fetch_gviz,           # GSheet gviz JSON fetch
    gviz_cell,            # Safe cell extraction from gviz row
    build_col_map,        # label → index map from gviz cols
    week_bounds,          # (week_start, week_end) for Mon-Sun containing today
    prev_week_bounds,     # (prev_ws, prev_we) for week before given week_start
    make_week_id,         # "YYYY-Www" string
    _ask,                 # Prompt with LUSINE_HEADLESS/FORCE support
)
```

## Common Parser Bugs Fixed (2026-06-14)

| Bug | Symptom | Fix |
|-----|---------|-----|
| `cv(row, col)` | `NameError: cv not defined` | → `gviz_cell(row, col)` |
| `detect_week()` | `NameError: detect_week not defined` | → `week_bounds()` (from _utils) |
| `get_prev_week(ws)` | `NameError: get_prev_week not defined` | → `prev_week_bounds(ws)` (from _utils) |
| `urllib` not defined | `NameError: urllib` in exception handler | Add `import urllib.request, urllib.error` |
| `timedelta` not defined | `NameError: timedelta` | Add `from datetime import date, timedelta` (or `datetime`) |
| `VAULT_ROOT` depth wrong | `FileNotFoundError: .../vault/vault/...` | `Path(__file__).parent.parent.parent.parent` |
| `LOG_FILE` double `vault/` | `.../vault/vault/10_OPERATION_DATA/...` | `VAULT_ROOT / "vault" / "10_OPERATION_DATA" / "xxx.md"` |
| Exit 1 on no data | Cron fails when GSheet empty | `sys.exit(0)` for "no data = warning" |
| `_ask()` blocks cron | Cron hangs waiting for input | Set `LUSINE_HEADLESS=1` in env |

## Parser Run Order (run_monday_gsheet_parsers.py)

```python
PARSERS = [
    {"name": "COL Weekly",           "script": ".../col_weekly_parser.py",        "required": True,  "headless": True},
    {"name": "COGS Supplier Monthly","script": ".../cogs_parser.py",              "required": True,  "headless": True},
    {"name": "Item Sales (Star Hor)","script": ".../item_sales_parser.py",       "required": False, "headless": True},
    {"name": "LTO Weekly Tracker",   "script": ".../lto_parser.py",              "required": False, "headless": True},
    {"name": "Hourly Cover + Revenue","script": ".../hourly_cover_parser.py",     "required": False, "headless": True},  # TBD
    {"name": "Google Reviews Weekly","script": ".../google_review_parser.py",    "required": False, "headless": True},
    {"name": "GrabFood Weekly",      "script": ".../grabfood_parser.py",         "required": False, "headless": True},
]
```

Required parsers fail the entire job; optional parsers log error and continue.

## Cron Job Creation

```bash
# Monday GSheet Parsers
hermes cronjob create --name "Monday GSheet Parsers" \
  --schedule "45 9 * * 1" \
  --script "vault/scripts/run_monday_gsheet_parsers.py" \
  --no-agent \
  --workdir "C:/Users/khoans/Documents/Warren_OS_Local"
```