# Morning Brief Command Fixes

Captured from `ops-morning-brief.md` updates 2026-06-13.

## Calendar helper
- `ops-morning-brief.md` Step 5 originally called `push_gcal.py --list --today`
- `push_gcal.py` does NOT have a list/read mode — only event creation.
- Fix: use `vault/scripts/list_gcal.py` with no args (defaults to today).
  Command: `python vault/scripts/list_gcal.py`
  Or `python vault/scripts/list_gcal.py --date YYYY-MM-DD`

## COGS lookup
- `ops-morning-brief.md` Step 7 now reads `OPERATION_INDEX.md` first, then resolves
  the COGS filename from §Operational Logs rather than hardcoding `03_COGS_Supplier_Monthly_Log.md`.

## New script
- `vault/scripts/list_gcal.py` — list today’s calendar events via service account
  (readonly scope), defaults to current date, prints title + start time.
