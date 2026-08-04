# col-deterministic-watcher Build/Debug Log (2026-07-23)

## Context
Replace LLM-driven `col-queue-watcher-v2` (every 30m, free model) with a `no_agent` deterministic
script (0 token). Warren directive: cheaper, no rate-limit, only run 09:00 + 10:00 daily.

## Bugs found + fixes (in order)

### BUG 1 — wrong script dir
`col_deterministic_watcher.py` used `SCRIPTS_DIR = VAULT_ROOT / "scripts"`.
Disk: `vault/scripts/` does NOT exist; `ops_col.py` lives at `vault/.scripts/ops_col.py`.
FIX: `SCRIPTS_DIR = VAULT_ROOT / ".scripts"`.

### BUG 2 — heartbeat early-return
`main()` had `if not raw_entries: return ""` BEFORE the `_update_heartbeat()` call (added at end).
No-op runs skipped heartbeat -> violated ops-col Step 0.
FIX: call `_update_heartbeat()` as FIRST line of `main()`.

### BUG 3 — VAULT_ROOT derived from __file__ breaks under cron
Script copied to `profile/scripts/` for no_agent cron. `parents[1]` resolved to `profile/` not `vault/`.
Symptom: `execution_success: true` but heartbeat file unchanged (written to `profile/_cron_heartbeat.json` instead).
FIX: hardcode `VAULT_ROOT = Path(r"C:\Users\khoans\Documents\Warren_OS_Local\vault")`.

### BUG 4 — watcher regex MISSING
Regex expected `LU3: Rev=X | COL=Y%` contiguous. Real `ops_col.py` output has `Covers= / Rev/Cov=` between.
All stores reported `[MISSING]`.
FIX: `r'(LU[357]):\s*Rev=([\d,]+).*?COL=([\d.]+)%.*?(Pass|Fail)'`.

### BUG 5 — heartbeat throttle (Warren preference)
Warren: "chi 2 lan/ngay, 9h va 10h".
FIX: time-gate inside `_update_heartbeat()`: `if datetime.now().hour not in (9, 10): return`.

## Final state
- Cron `col-deterministic-watcher` (job_id `7a080d54e0ac`), schedule `0 9,10 * * *`, no_agent, deliver all.
- SSOT: `vault/.scripts/col_deterministic_watcher.py` (git: warren-os-lusine).
- Runtime copy: `profile/scripts/col_deterministic_watcher.py` (git: warren-profile-root, force-add, gitignored).
- Test: injected TEST raw entry -> cron -> pending_approval + real 3-store preview -> deleted entry (no GSheet append). All green.

## Reproduction recipe (re-test after any edit)
```python
# 1. inject TEST raw entry (date 20990101 future placeholder)
import json; from pathlib import Path
qf = Path('vault/_inbox/col_queue.json')
q = json.loads(qf.read_text(encoding='utf-8'))
q['pending'].append({'id':'COL-TEST-20990101','status':'raw',
  'raw_text':'<full 3-store dump with REVENUE + COVERS>', 'source':'TEST'})
qf.write_text(json.dumps(q, indent=2, ensure_ascii=False), encoding='utf-8')
# 2. cronjob action=run job_id=<id>
# 3. assert queue entry status == pending_approval AND preview shows 3 stores (not MISSING)
# 4. cleanup: remove TEST entry, git checkout col_queue.json
```
