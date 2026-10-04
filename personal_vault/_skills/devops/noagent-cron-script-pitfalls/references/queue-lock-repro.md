# Queue Lock Repro Recipe (col_queue_handler.py)

**Bug (2026-07-27):** Warren posted `[col]` revenue 26/7 to Telegram at 07:28.
The live bot acked ("✅ Da nhan COL brain dump...") but the queue entry
`COL-20260727-072837` vanished from `vault/_inbox/col_queue.json`.
The deterministic watcher (10:05) then found "No raw entries" → 26/7 never
appended to GSheet `07_COL_Weekly_Log`.

**Root cause:** two `no_agent` consumers of the SAME bot token + SAME
queue file race each other:
- `telegram_bot.py` (aiogram, live, persistent) → `case_brain_nl_handler.handle_message` → `queue_col_dump`
- `col_telegram_intake.py` (getUpdates cron, offset-based) → `_queue` → `queue_col_dump`

Both do `_load + append + _save`. Without a lock, two near-simultaneous
writes clobber each other's in-memory snapshot → the just-queued entry is lost.
A second contributor: `ops_col.py` printed ✅ under Windows cp1252 stdout →
`UnicodeEncodeError` → exit 1 even though the GSheet append SUCCEEDED →
false `status:"error"` (compounds the lost-entry confusion).

**The fixes (committed `45835ce`):**
1. `ops_col.py` top: `sys.stdout.reconfigure(encoding="utf-8")` (idempotent, try/except).
2. `col_queue_handler.py`: wrap load+mutate+save in `filelock.FileLock`
   (cross-platform; do NOT use `msvcrt.locking` — wrong arg count on py3.14).
3. `col_id` now uses `%f` microseconds → no id collision on rapid fire.

## Repro (asserts the fix holds)

```python
import sys, io, threading, json, tempfile, pathlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import col_queue_handler as cq

tmp = pathlib.Path(tempfile.gettempdir()) / "tq_repro.json"
lk  = pathlib.Path(tempfile.gettempdir()) / "tq_repro.json.lock"
for p in (tmp, lk):
    if p.exists(): p.unlink()
cq.COL_QUEUE_FILE = tmp          # don't touch the real queue

def worker(n):
    cq.queue_col_dump(f"LU3 test {n}", source="test")

ts = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
[t.start() for t in ts]; [t.join() for t in ts]

data = json.loads(tmp.read_text(encoding="utf-8"))
pend = data["pending"]
ids  = [e["id"] for e in pend]
print("pending:", len(pend), "| unique:", len(set(ids)) == len(ids))
print("RESULT:", "PASS" if len(pend) == 8 and len(set(ids)) == 8 else "FAIL")
for p in (tmp, lk):
    if p.exists(): p.unlink()
```

**Expected:** `pending: 8 | unique: True | RESULT: PASS`.
**To confirm the bug reproduces WITHOUT the fix:** comment out the `with _QUEUE_LOCK:`
block in `_with_lock` (so it just calls fn without locking) and re-run →
entries drop / ids duplicate.

## Verify the utf-8 fix
```bash
python ops_col.py --dry-run     # exit code must be 0, no UnicodeEncodeError in stderr
```
On Windows no_agent cron, pre-fix this printed `UnicodeEncodeError` and exited 1
despite a successful append.
