# OPERATION_INDEX.md Duplicate Row Fix Pattern

Reproduced 2026-06-14. After parser runs (col_weekly_parser, etc.), the index table can accumulate duplicate blocks.

## Symptom
- OPERATION_INDEX.md shows 10+ duplicate table rows for the same files (e.g., `07_COL_Weekly_Log.md` and `weekly_ops_synthesis.md` repeated 5x)
- Table header `|| # | File | Cadence | Tracks | Last Updated |` appears multiple times
- Auto-sync logic may read wrong row

## Root Cause
Parser append logic writes to index without checking for existing rows, or multiple processes append concurrently.

## Fix (one-time)
1. Read full file: `cat OPERATION_INDEX.md`
2. Write corrected version with `write_file` (native Windows path) — keep only the clean 12-row table
3. Update frontmatter `last_updated: <today>`

## Prevention
- Run `/ops-lint --quick` weekly (cron Mon 06:30) — catches duplicate index rows
- Add pre-write check in parsers: read index, deduplicate before append
- `ops_index_watchdog.py` should flag tables with >N rows for 12 known logs

## Files to verify after fix
- `vault/10_OPERATION_DATA/OPERATION_INDEX.md` — 12 operational logs + 3 morning briefs
- `vault/00_CORE_LOGIC/TODAY.md` — reads index for COL/SPLH
- `/ops-morning-brief` — reads index for COGS lookup (Step 7)