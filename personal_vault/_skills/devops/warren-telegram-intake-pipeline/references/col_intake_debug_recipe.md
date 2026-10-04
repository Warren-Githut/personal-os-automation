# COL Intake Debug Recipe (from session 2026-07-27)

## Symptom traced
Warren posted `[col]` 26/7 revenue to Telegram at 07:28, saw ack "Da nhan COL brain dump...", but `col_queue.json` had no `COL-20260727-072837` entry -> watcher found nothing -> 26/7 never appended to GSheet `07_COL_Weekly_Log`.

## Forensic commands (run from vault root, git-bash)
```bash
# 1. Is the entry anywhere in the queue?
python3 -c "import json;d=json.load(open('vault/_inbox/col_queue.json'));print('072837' in json.dumps(d))"

# 2. working tree vs HEAD — was it written then reverted?
git diff --quiet vault/_inbox/col_queue.json && echo "WORKING==HEAD" || echo "WORKING!=HEAD"
git show HEAD:vault/_inbox/col_queue.json | grep -c "COL-20260727-072837"   # expect 0

# 3. Telegram offset (getUpdates cron)
python3 -c "import json;print(json.load(open('vault/.scripts/.col_telegram_offset.json')))"

# 4. Did the cron jobs actually run? (heartbeat)
python3 -c "import json;d=json.load(open('vault/_inbox/_cron_heartbeat.json'));print({k:v for k,v in d.items() if 'col' in k.lower()})"

# 5. Where does the ack string come from? (confirms which consumer printed it)
grep -rn "Da nhan COL brain dump" vault/.scripts/

# 6. Independent GSheet read-back after append
python3 -c "
import ops_col as oc
svc=oc._get_sheets_service()
rows=svc.spreadsheets().values().get(spreadsheetId=oc.SHEET_ID,range=f\"'{oc.COL_SHEET_NAME}'!A1:AR500\").execute().get('values',[])
print([(r[0],r[2],r[3]) for r in rows if len(r)>=4 and r[0].replace('/','').replace('-','')=='20260726'])
"
```

## Root cause found
Two pollers on one token (`telegram_bot.py` aiogram + `col_telegram_intake.py` getUpdates) + `_save_queue()` had no lock -> a queued entry was clobbered by a concurrent write -> watcher had nothing to process. Plus `ops_col.py` printed ✅ under cp1252 -> false exit 1.

## Applied fixes (committed 45835ce, pushed)
### A) ops_col.py — utf-8 stdout (top of file, after imports)
```python
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
```

### C) col_queue_handler.py — filelock + microsecond id
```python
import filelock
_QUEUE_LOCK = None

def _with_lock(fn):
    global _QUEUE_LOCK
    if _QUEUE_LOCK is None:
        _QUEUE_LOCK = filelock.FileLock(str(COL_QUEUE_FILE) + ".lock")
    with _QUEUE_LOCK:
        queue = _load_queue()
        result = fn(queue)
        _save_queue(queue)
        return result
```
- `queue_col_dump`: wrap the load+append in `_with_lock`; `col_id = f"COL-{datetime.now().strftime('%Y%m%d-%H%M%S.%f')}"`.
- `approve_col`: move its body into `_approve_inner(queue, entry)` (mutates, no save); call inside `_with_lock`; drop the standalone `_save_queue(queue)` (save happens in lock).

## Verify (concurrent simulate)
```python
import col_queue_handler as cq, threading, json, pathlib, tempfile
tmp = pathlib.Path(tempfile.gettempdir())/'tq.json'
cq.COL_QUEUE_FILE = tmp
def w(n): cq.queue_col_dump(f'LU3 test {n}', source='test')
ts=[threading.Thread(target=w,args=(i,)) for i in range(8)]
[t.start() for t in ts]; [t.join() for t in ts]
d=json.loads(tmp.read_text(encoding='utf-8'))
pend=d['pending']
assert len(pend)==8 and len({e['id'] for e in pend})==8, "LOST OR DUP"
```
PASS = 8 entries, all unique ids. (Before the lock, the race could drop entries.)

## msvcrt.locking trap (do NOT use)
On Python 3.14 the 6-arg form raises `TypeError: locking expected 3 arguments, got 6`.
Use `filelock.FileLock` instead — already installed in this env.
