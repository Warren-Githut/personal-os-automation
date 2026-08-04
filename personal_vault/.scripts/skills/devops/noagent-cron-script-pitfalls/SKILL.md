---
name: noagent-cron-script-pitfalls
description: "Pitfalls when writing Python scripts that run as no_agent Hermes cron jobs (VAULT_ROOT path breakage, regex-matching upstream stdout, heartbeat throttle). Use when building/patching a no_agent cron script for warren-profile."
version: 1.0.0
author: Hermes
falseer: "write no_agent cron script | script for cron | no_agent=True | cron job script path | col-deterministic-watcher style script | col-telegram-intake style poller"
category: devops
tags: ['cron', 'no_agent', 'script', 'pitfalls', 'path', 'heartbeat']
related_skills: ['new-automation', 'ops-col', 'cron-job-ops']
---

# no_agent Cron Script Pitfalls

> Hard-won lessons from building `col-deterministic-watcher` (2026-07-23) to replace the LLM-driven `col-queue-watcher-v2`. These bite SILENTLY: the cron reports `execution_success: true` but produces ZERO side effects.

## HARD RULE 1 — Never derive VAULT_ROOT from `__file__` in a copied script

A `no_agent` cron resolves `script` by joining into `%APPDATA%/hermes/profiles/warren-profile/scripts/` (guard blocks any other path). So the "SSOT" script in `vault/.scripts/` must be COPIED there.

If the script does `VAULT_ROOT = Path(__file__).resolve().parents[1]`:
- From `vault/.scripts/X.py` → `parents[1]` = `vault/` ✅ (works when run by hand)
- From `profile/scripts/X.py` (cron runtime) → `parents[1]` = `profile/` ❌

→ Every derived path breaks silently: `OPS_COL_SCRIPT` → `profile/.scripts/ops_col.py` (missing), `_cron_heartbeat.json` written to `profile/` (not vault), queue file not found.

**FIX:** hardcode absolute in any script destined for no_agent cron:
```python
VAULT_ROOT = Path(r"C:\Users\khoans\Documents\Warren_OS_Local\vault")
```

## HARD RULE 2 — Regex must match REAL upstream stdout, not assumed format

When a watcher parses another script's stdout (e.g. `col_deterministic_watcher.py` parsing `ops_col.py --dry-run`), do NOT assume the output layout.

Bad (assumed): `r'(LU[357]):\s*Rev=([\d,]+)\s*\|\s*COL=([\d.]+)%\s*\|\s*(Pass|Fail)'`
Real `ops_col.py` output: `LU3: Rev=26,592,500 | Covers=104 | Rev/Cov=255,697 | COL=21.43% | Fail | Trend=N/A`
→ regex fails → all stores reported `[MISSING]` (false negative).

**FIX:** run the upstream dry-run once, capture REAL output, write regex against it:
```python
store_pat = re.compile(r'(LU[357]):\s*Rev=([\d,]+).*?COL=([\d.]+)%.*?(Pass|Fail)')
```
Use `.*?` non-greedy to skip intermediate fields. VERIFY: feed a test queue entry → run cron → confirm preview shows real store data (not MISSING).

## HARD RULE 3 — Heartbeat time-gate when Warren throttles

`ops-col` Step 0 says "ALWAYS update `_cron_heartbeat.json` even no-op". BUT Warren may throttle: for the COL deterministic watcher (schedule `0 9,10 * * *`) he said "chỉ 2 lần/ngày, 9h và 10h sáng". His explicit instruction WINS over the generic rule.

**FIX:** gate the write:
```python
def _update_heartbeat():
    if datetime.now().hour not in (9, 10):  # Warren throttle 2026-07-23
        return
    # ... write json
```
VERIFY with simulated `datetime.now()`: 09:30 writes, 08:xx skips.

## Verify Protocol (MANDATORY after any no_agent script edit)

`execution_success: true` is NOT proof of work. After `cronjob action=run`:
1. Check the ACTUAL destination file changed (e.g. `vault/_cron_heartbeat.json` timestamp matches run time, NOT an old value).
2. Check NO stray file written to `profile/` (e.g. `profile/_cron_heartbeat.json` should NOT exist).
3. For watchers: inject a test `raw` queue entry → run → confirm `pending_approval` + real preview → cleanup (delete test entry, do NOT approve → no GSheet append).

## HARD RULE 4 — Call upstream module functions DIRECTLY, never parse main() output

`ops_col.py __main__` returns a human string message that VARIES by branch (`"Khong co du lieu nao de append..."` on dry-run skip, or a preview block) — it is NOT structured data. A watcher that calls `ops_col.main(dry_run=True)` then regex-parses the returned string gets `[MISSING]` for every store.

ALSO: `ops_col.py __main__` does `text = ' '.join(sys.argv[1:])`, so passing a multi-line brain dump via `subprocess([..., text, '--dry-run'])` collapses newlines → parse fail.

**FIX:** import the module and call the calculation primitives directly:
```python
import importlib.util
spec = importlib.util.spec_from_file_location("ops_col_direct", str(OPS_COL_SCRIPT))
ops_col = importlib.util.module_from_spec(spec); spec.loader.exec_module(ops_col)
service = ops_col._get_sheets_service()
parsed = ops_col.parse_brain_dump(reformatted_text)        # -> {date, ym, day, stores:{...}}
cph = ops_col.load_cph(service)                             # NEEDS service arg
history = ops_col.load_history(service)                     # NEEDS service arg
for store in ["LU3","LU5","LU7"]:
    d = parsed["stores"][store]
    rates, _ = ops_col.resolve_cph(parsed["ym"], store, cph)
    row = ops_col.calculate_row(parsed["date"], parsed["day"], store,
                                d["revenue"], d["hours"], rates, history, covers=d["covers"])
    rowd = dict(zip(ops_col.HEADER_44, row))
    col = rowd["COL_Percentage_Whole_Store"]; status = rowd["Status"]
```
- `load_cph(service)` / `load_history(service)` REQUIRE the Google Sheets `service` object — calling without it raises `TypeError: missing 1 required positional argument: 'service'`.
- Cache the imported module (module-level `_load_ops_col()`) so repeated queue entries don't re-exec the file.

VERIFY: inject a real Telegram `[col]` dump → run watcher → preview shows 3 stores with real COL% (not MISSING, not ERROR).

## HARD RULE 5 — External fetch MUST return a failure sentinel (None), never [] (silent death)

**Bug class (found + fixed 2026-07-25, `col_telegram_intake.py` + `quota.py`):** a `no_agent` script that polls/fetches an external source (Telegram `getUpdates`, local state file, API) wraps the call in `try/except Exception: return []` (or `return []` on a 200 `{"ok":false}`). When the token expires / network dies / file corrupts, that `[]` collapses into the caller's "no new work" branch → **silent no-op forever, no alert, exit code 0**. The cron shows `last_status=ok` but is dead. This is the exact anti-pattern the @vartekxx "verifier gate" article warns about — "without verifier = agent agrees with itself on repeat."

**Rule — distinguish FAILURE from EMPTY with a sentinel:**
- A fetch/parse function that CAN fail MUST return a distinct sentinel for failure (`None`) vs empty (`[]`).
- Caller: `if updates is None: print(FATAL); sys.exit(1)` (FAILURE = non-zero, alert) vs `if not updates: return` (EMPTY = legit silent no-op).
- Guard the API envelope BEFORE extracting results: `if not data.get("ok"): return None` — a 200 with `ok:false` is FAILURE, not empty.
- For state-file loads (e.g. `quota.py`): corrupt/missing-key JSON must `sys.exit(1)` + print ERROR, NOT auto-reset to a default silently (that reports wrong data with exit 0).

```python
def _get_updates(token, offset):
    try:
        data = json.loads(urllib.request.urlopen(req, timeout=10).read())
        if not data.get("ok"):          # 200 but API error -> FAIL, not empty
            return None
        return data.get("result", [])
    except Exception:
        return None                       # FAIL -> sentinel, never []

def main():
    updates = _get_updates(token, offset)
    if updates is None:                  # FAILURE branch
        print("[!] getUpdates FAILED - token/network? Exiting non-zero.", file=sys.stderr)
        sys.exit(1)
    if not updates:                      # EMPTY branch (legit no-op)
        return
```

**Why it matters:** `audit-automation` only flags `deliver=local` crons as "pseudo-silent" IF the script self-sends Telegram. A poller that swallows its own exception sends NOTHING — no Telegram, no non-zero exit — so even the cron delivery layer can't catch it. The `None`-sentinel + `sys.exit(1)` is the MINIMUM verifier gate for any external-fetch `no_agent` script.

**Verify after writing:** force a failure (bad token / offline / corrupt file) → assert `exit code != 0` + stderr FATAL line. Do NOT ship a poller whose exception path returns `[]`.

**Reviewer-node catch (2026-07-25):** an independent critic caught two blind spots the first pass missed — (1) the `ok:false` 200-response path was still returning `[]` (same silent death), fixed by the `if not data.get("ok")` guard; (2) `quota.py` only validated JSON-parse, not required keys — a file missing fields parsed fine then crashed later or reported wrong. Always validate schema, not just parseability.

## HARD RULE 6 — Concurrent queue writes NEED a file lock (race drops entries)
**Bug class (found + fixed 2026-07-27, `col_queue_handler.py`):** two `no_agent` consumers of the SAME queue file both call `queue_col_dump` → `_load + append + _save`:
- `telegram_bot.py` (aiogram, live, persistent) 
- `col_telegram_intake.py` (getUpdates cron, offset-based)

Without a lock, two near-simultaneous writes clobber each other's snapshot → a just-queued entry (e.g. `COL-20260727-072837`) **vanishes** from `col_queue.json`. Symptom: Warren sees the ack ("✅ Da nhan COL...") but the deterministic watcher later reports "No raw entries" → the `[col]` post is **received but never appended to GSheet**. This looks like "cron didn't run" but it's a dropped queue entry.

**FIX:** wrap read-modify-write in an exclusive file lock. `filelock.FileLock` is cross-platform (Windows + Linux) — prefer it over `msvcrt.locking` (wrong arg-count signature on py3.14, raises `TypeError`). Refactor `queue_col_dump` and `approve_col` to mutate+save **inside** the lock:
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
Callers pass a closure that mutates `queue` in place; the lock owns the save. Do NOT `_save_queue` again inside the caller (double-save is harmless but redundant).

**Sub-fix — id collision:** `col_id = f"COL-{datetime.now():%Y%m%d-%H%M%S}"` collides when 2 dumps land in the same second → duplicate ids → `find-by-id` logic matches the wrong entry. Use `%f` microseconds: `f"COL-{datetime.now():%Y%m%d-%H%M%S.%f}"`.

**VERIFY (repro recipe in references/queue-lock-repro.md):** spawn N threads (N≥5) each calling `queue_col_dump` concurrently → assert exactly N pending entries, all unique ids, 0 lost. Re-run WITHOUT the lock to confirm the bug reproduces (entries dropped / dup ids).

## HARD RULE 7 — no_agent cron scripts printing emoji CRASH on Windows cp1252 stdout
**Bug class (found + fixed 2026-07-27, `ops_col.py`):** `main()` returns a string containing ✅/❌. Under Windows `no_agent` cron, `sys.stdout` is cp1252 → `UnicodeEncodeError: 'charmap' codec can't encode character '\u2705'` → **exit code 1 EVEN THOUGH the GSheet append SUCCEEDED** (the append happened before the print). This leaves `col_queue.json` stuck on `status:"error"` (a FALSE error) and — combined with the RULE 6 race — drops the entry. Symptom again reads as "cron failed / didn't run".

**FIX:** force UTF-8 stdout at the top of the script (idempotent, wrap in try/except):
```python
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
```
Now the script exits 0 on success and the queue entry lands as `done`.

**VERIFY:** run `python ops_col.py --dry-run` (or a synthetic dump) under a harness that does NOT pre-set UTF-8; assert `returncode == 0` and `UnicodeEncodeError` absent from stderr. (py3.12+ has `.reconfigure`; on older Py the `except` swallows gracefully.)

> **Pattern:** any `no_agent` script that prints non-ASCII (emoji, Vietnamese accents) and is invoked by Windows cron MUST set stdout encoding, or it will exit 1 on the print even when all real work succeeded. This is a SILENT false-failure — the data is fine, only the report crashed.
