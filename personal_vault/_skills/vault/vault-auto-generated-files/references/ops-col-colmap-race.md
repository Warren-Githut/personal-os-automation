# ops-col: GSheet column map + double-consumer race (captured 2026-07-27)

> Belongs conceptually to the `ops-col` skill, but `ops-col` is USER-OWNED in warren-profile.
> Kept here until `hermes curator adopt ops-col` embeds it. Durable technique — not session-specific.

## 1. GSheet `07_COL_Weekly_Log` column map (verified 2026-07-27)
Sheet ID: `1ZtIocc_Ic1z-tO1JGd4ZLnRB_7ZHHkvpJ5emaWJyeEE`
0-based list idx → spreadsheet column letter (col number = idx+1):

| idx | col | field |
|----:|-----|-------|
| 0 | A | date (YYYYMMDD) |
| 1 | B | weekday |
| 2 | C | store (LU3/LU5/LU7) |
| 3 | D | rev_net (VND) |
| 4 | E | rev FOH |
| 5 | F | rev BOH |
| 25 | Z | COL_Percentage_Whole_Store |
| 37 | AL | Status (Pass/Fail) |
| 43 | AR | Cover |

Read pattern (cases_parser helpers `_get_gsheet_service`, `GSHEET_ID`, `GSHEET_RANGE`):
```python
ymd = target_date.strftime("%Y%m%d")
for r in rows:
    if str(r[0]).replace("/","") != ymd: continue
    store = str(r[2]).strip().upper()
    col_pct = float(str(r[25]).replace("%","").strip())   # col Z
    status  = str(r[37]).strip()                            # col AL
    cover   = int(str(r[43]).replace(",","").strip())      # col AR
```

## 2. Double Telegram-consumer race (root cause of lost COL entries)
Two independent pollers share ONE bot token:
- `telegram_bot.py` (aiogram, live bot) → `case_brain_nl_handler.handle_message` → `queue_col_dump`
- `col_telegram_intake.py` (getUpdates + persistent offset file, cron)

Telegram delivers each update to ONLY one consumer → they race. A `[col]` post consumed by one
is invisible to the other. Combined with a non-atomic `_save_queue` (load→append→write whole file),
a just-queued entry (`COL-20260727-072837`) vanished from `col_queue.json` → the deterministic
watcher had nothing to process → Warren's post was "received but never appended".

Fix applied (in `col_queue_handler.py`, currently user-owned — re-apply after adopt):
- `filelock.FileLock` around the load→mutate→save in `queue_col_dump` / `approve_col`.
- `col_id` uses `%Y%m%d-%H%M%S.%f` (microseconds) to avoid id collisions on same-second posts.
- `ops_col.py`: `sys.stdout.reconfigure(encoding="utf-8")` so printing OK/ERR emoji doesn't raise
  `UnicodeEncodeError` under Windows no_agent cron (cp1252) → false exit-code-1.

## 3. Warren rule: SQL wins on conflict
When a `[col]` dump's typed revenue conflicts with IKKO SQL (>5%), **use SQL** — Warren:
"SQL là số chính xác nhất". The watcher (`col_deterministic_watcher._resolve_rev_covers`) already
implements this; the appended GSheet row must be SQL-consistent (SQL rev + SQL covers), otherwise
COL% recomputes wrong. If you ever hand-fix a row, set rev/covers/COL%/Status all from SQL.
