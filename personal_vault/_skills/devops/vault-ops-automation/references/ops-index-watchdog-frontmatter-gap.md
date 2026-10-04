# OPERATION_INDEX Watchdog — Frontmatter Update Gap

**Discovered:** 2026-06-19 (daily cron `lusine-daily-col-parse`)

## Problem
The `ops_index_watchdog.py` script (at `vault/scripts/.archive/2026-06_phase2/ops_index_watchdog.py`) updates the table rows in `OPERATION_INDEX.md` from log files' frontmatter `last_updated` values, but **does not update the index file's own frontmatter `last_updated` field**.

## Evidence
- Index frontmatter showed `last_updated: 2026-06-14` after watchdog ran
- Watchdog output: `Synced 10_OPERATION_DATA\OPERATION_INDEX.md`
- Table rows correctly updated to show latest log dates (e.g., 2026-06-16 for weekly logs)
- But index file's own frontmatter stale at 2026-06-14

## Impact
- `/ops-morning-brief` and session-start sync rely on index frontmatter `last_updated` as a metadata signal
- Stale index frontmatter → could trigger false "index needs rebuild" alerts
- Violates the Update Protocol in OPERATION_INDEX.md §48-53: "When `/process-logs` or `/ops-ingest` appends to a log file, it MUST update: 3. This file's `last_updated` frontmatter"

## Workaround (Current)
Manual patch after watchdog run:
```bash
# After index sync, update index file's own frontmatter
sed -i 's/last_updated: .*/last_updated: 2026-06-19/' OPERATION_INDEX.md
```
Or in Python:
```python
from datetime import date
today = date.today().isoformat()
# Patch frontmatter last_updated: today
```

## Fix Needed
Update `ops_index_watchdog.py` to:
1. After syncing table rows, update the index file's own frontmatter `last_updated` to today
2. Use same frontmatter parsing logic already in the script
3. Write back with updated `last_updated`

## Code Location
- Watchdog: `vault/scripts/.archive/2026-06_phase2/ops_index_watchdog.py`
- Also installed at: `vault/scripts/ops_index_watchdog.py` (per skill references)

## Related
- `references/ops-index-sync.md` — sync protocol + hooks
- `references/vault_root-path-bug.md` — VAULT_ROOT double-`vault/` path bug pattern
- Cron job: `lusine-index-sync` (Sun 18:00) and `lusine-daily-col-parse` (Daily 09:00 both run watchdog)