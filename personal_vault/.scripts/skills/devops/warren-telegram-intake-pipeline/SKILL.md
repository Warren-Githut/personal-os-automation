---
name: warren-telegram-intake-pipeline
description: Debug L'Usine Telegram intake race, UnicodeError, filelock.
type: debugging
version: 1.0.0
---

# warren-telegram-intake-pipeline

Debug + harden the Warren/L'Usine Telegram intake pipeline that turns Warren's brain-dump posts into GSheet rows.

## When to use
- Warren posts `[col]` / a review / a case / `[capture-sleep]` to Telegram and it is "received" (he saw an ack like "Da nhan COL brain dump...") but NEVER appears in the GSheet / `col_queue.json` / vault.
- `vault/_inbox/col_queue.json` is missing an entry you know was posted.
- A no_agent cron reports `exit code 1` / `status: error` even though the GSheet append actually succeeded.
- You are editing any `vault/.scripts/*.py` that runs as a Windows no_agent Hermes cron and prints non-ASCII (emoji ✅/❌).

## Architecture (read this first)
Two independent consumers poll the SAME Telegram bot token:
1. `vault/.scripts/lusine-ops/lusine_ops/telegram_bot.py` — **aiogram** async live bot. Handles ALL text -> `case_brain_nl_handler.handle_message()` -> for `[col]` calls `col_queue_handler.queue_col_dump()`.
2. `vault/.scripts/col_telegram_intake.py` — **getUpdates** long-poll cron (`*/15 9-11`), reads offset from `vault/.scripts/.col_telegram_offset.json`, queues via the same `queue_col_dump()`.

⚠️ **Telegram delivers each update to ONLY ONE poller.** If both run, they race; the loser never sees the message. This is the #1 cause of "received but lost".

## Pitfalls (HARD)

### P1 — Double-consumer race drops messages
If `telegram_bot.py` (aiogram) and `col_telegram_intake.py` (getUpdates) both run against one token, a posted `[col]` may be consumed by one and never queued by the other. Symptom: Warren sees the ack but `col_queue.json` has no entry -> the deterministic watcher (`col_deterministic_watcher.py`) finds nothing -> no GSheet append.
**Fix:** make ONE consumer authoritative. Either disable the getUpdates cron (let aiogram be sole poller), or make them mutually exclusive (lock / single process). Do NOT leave both polling the same token.

### P2 — Windows no_agent cron: emoji print -> UnicodeEncodeError -> false exit 1
A script that succeeds but then `print()`s an emoji (✅/❌) under a Windows no_agent cron hits `UnicodeEncodeError: 'charmap' codec can't encode ... cp1252` -> Python exits 1. The GSheet append (which ran BEFORE the print) is fine, but the cron marks the job `error` and the queue entry can get stuck.
**Fix:** at the very top of the script (after `import sys`):
```python
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
```
Applied to `vault/.scripts/ops_col.py` (2026-07-27). See `references/col_intake_debug_recipe.md`.

### P3 — Concurrent JSON queue writes clobber entries (no lock)
`col_queue_handler._save_queue()` does load -> append -> save of the whole `col_queue.json`. If `telegram_bot.py` and `col_telegram_intake.py` write near-simultaneously, the last writer wins with a stale snapshot -> a just-queued entry vanishes. This is the actual mechanism behind P1's "lost entry".
**Fix:** wrap load+mutate+save in a `filelock.FileLock` (cross-platform). See recipe.
⚠️ **msvcrt trap:** `msvcrt.locking(fd, LK_LOCK, 0,0,0,0)` raises `TypeError: locking expected 3 arguments, got 6` on Python 3.14 (the 6-arg form is NOT accepted on this build). Use `filelock` instead — already installed in this env (`pip install filelock` if missing).

### P4 — Queue entry ID collisions within 1 second
`col_id = f"COL-{datetime.now().strftime('%Y%m%d-%H%M%S')}"` collides if two entries arrive in the same second -> duplicates with same id -> watcher processes one, the rest are orphans/overwritten.
**Fix:** `%Y%m%d-%H%M%S.%f` (microseconds). Applied to `col_queue_handler.queue_col_dump` (2026-07-27).

## Warren preferences (FORMAT)
- COL preview must look like the **TODAY.md table format** (markdown `| Store | Rev | ... |`), NOT the one-liner `LU3: Rev=51,525,860 | Covers=169 | COL=9.39% | [SQL] [PASS]` + conflict block that `_build_preview` in `col_deterministic_watcher.py` currently emits. Warren called that "lạ" (weird) on 2026-07-27.
- Primary revenue = **Warren's typed revenue in the dump**; SQL is a reference line only (shown when it conflicts beyond threshold). Do NOT silently override Warren's number with SQL in the preview.
- When Warren says "gửi bố lại định dạng đúng, cùng file TODAY.md", re-send the data as a clean TODAY.md-style table AND attach the `TODAY.md` file via `MEDIA:/path/to/TODAY.md`.

## Debug recipe (forensic sequence)
See `references/col_intake_debug_recipe.md` for the exact commands used to trace a lost `COL-20260727-072837` entry:
1. `git diff` / working-vs-HEAD on `col_queue.json` -> was the entry ever written then reverted?
2. Read `.col_telegram_offset.json` -> is the offset already past Warren's message update_id?
3. Cron heartbeats (`_cron_heartbeat.json`) -> did watcher/intake actually run?
4. Grep the ack string source (`queue_col_dump` return) -> confirms which consumer printed it.
5. Read back GSheet rows by `YYYYMMDD` to confirm append landed (independent verify).

## Relation to `ops-col`
The SOP/COL-calculation logic lives in the `ops-col` skill + `vault/.scripts/ops_col.py`. This skill covers the **pipeline robustness/debugging layer** only. `ops-col`'s SKILL.md currently does NOT document P1–P4 or the preview-format preference. If `ops-col` is curator-adopted, fold these in (see reply note: `ops-col` appears user-owned/bundled -> autonomous patch refused; recommend `hermes curator adopt ops-col`).

## Verify gate (after any pipeline fix)
Simulate 5–8 concurrent `queue_col_dump()` calls (threads) -> assert all entries present + unique IDs (see recipe). Then read back the GSheet row by `YYYYMMDD` to confirm append. Never declare "fixed" on a single serial run.

**Re-runnable probe:** `scripts/verify_queue_filelock.py` (shipped in this skill). Spawns N concurrent `queue_col_dump()` against a temp queue + lock, asserts (1) all entries survive the lock, (2) unique IDs. Run after ANY edit to `col_queue_handler._save_queue` / `queue_col_dump`:
```bash
cd vault/.scripts && python3 /c/Users/khoans/AppData/Local/hermes/profiles/warren-profile/skills/devops/warren-telegram-intake-pipeline/scripts/verify_queue_filelock.py --n 8
# expect: threads=8 entries_written=8 unique_ids=8  RESULT: PASS
```
Before the filelock fix (2026-07-27) this failed intermittently with lost/duplicate entries; after the `filelock` + `%f` id fix it passes deterministically.

## Warren expects agent-skills discipline
When debugging this pipeline, Warren explicitly asked to "using-agent-skill để debug" — apply the agent-skills / reviewer-node discipline (independent verification, no blind trust of stdout) rather than a single narrative pass.
