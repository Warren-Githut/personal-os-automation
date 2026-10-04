# L'Usine Parser Refactor Status

Last updated: 2026-06-12

## Architecture

.kilo/skills/
├── _week_utils.py      # Week detection helpers
├── _utils.py           # Shared: _ask(), fetch_gviz(), gviz_cell(),
│                       #   week_bounds(), prev_week_bounds(), make_week_id(),
│                       #   parse_gviz_date(), formatting helpers,
│                       #   insert_or_replace_weekly(), short_name()
├── cph_config.py       # SEGMENTS_ORDER, CPH_BENCHMARKS, SEGMENT_MAP, NON_COST_COLS
├── hr_movements_parser.py
├── payroll_cph.py
├── col_cph.py
├── col_weekly_parser.py
├── cogs_parser.py
├── grabfood_parser.py
├── google_review_parser.py
├── hourly_cover_parser.py
├── item_sales_weekly_parser.py
└── lto_weekly_parser.py

## Refactor Progress

### Completed
- _utils.py and _week_utils.py created
- cph_config.py expanded with SEGMENT_MAP and NON_COST_COLS
- hr_movements_parser.py input() -> _ask() migration completed
- Dry run passed for hr_movements_parser.py with 20260612 file (Offer: 4, Joined: 2, Resignation: 1)
- Verified: grep -n 'input(' hr_movements_parser.py -> no output

### Remaining
- Remove duplicate config from payroll_cph.py (use from cph_config import ...)
- Update grabfood_parser.py, lto_weekly_parser.py, hourly_cover_parser.py, google_review_parser.py, item_sales_weekly_parser.py, col_weekly_parser.py, cogs_parser.py to use _week_utils and fetch_gviz
- Add _ask() verification step to CI/test pattern

## Verified Commands

```bash
cd C:/Users/khoans/Documents/Warren_OS_Local/.kilo/skills
grep -n 'input(' <parser>.py || true   # Should return nothing
grep -n '_ask(' <parser>.py            # Should show headless-compatible asks
```

## Known Issues
- PermissionError on Win32 when deleting Excel source file immediately after parsing (file lock). Wrap os.remove() in retry or defer cleanup.
- Hourly cover parser reads CSV export from GSheet, not gviz JSON. Keep separate path if needed.
