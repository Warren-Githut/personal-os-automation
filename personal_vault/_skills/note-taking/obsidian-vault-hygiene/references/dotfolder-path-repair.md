# dotfolder-path-repair.md — Real transcript + verify recipe

## Context (2026-07-16)
After the 2026-07-15 dotfolder cleanup (scripts→.scripts, _assets→._assets), Warren reported "chạy parser bị struggle". Root cause was NOT the dotfolder rename — it was **stale hardcoded paths** in 3 scripts that broke when Hermes/cron invoked them from a different CWD.

## The 3 broken spots (all fixed)
1. `vault/.scripts/gen_today_and_send.py`
   - `VAULT = Path(r"C:\...\Warren_OS_Local")` (repo root)
   - `SCRIPTS = VAULT / "vault/scripts"` → SCRIPT import `_send_telegram` from deleted dir
   - Fix: `SCRIPTS = VAULT / "vault/.scripts"`
2. `vault/.scripts/regenerate_today.py`
   - Module level: `REVENUE_SCRIPT = VAULT_ROOT / "vault" / ".scripts" / ...` (fixed)
   - **BUT** inside `main()`: `REVENUE_SCRIPT = VAULT_ROOT / "scripts" / ...` (local shadow, still stale) → runtime `[ERROR] not found`
   - Fix: change the `main()` local too
3. `vault/.scripts/gen_grabfood_dashboard.py`
   - `umd_path = VAULT_ROOT / "vault" / "10_OPERATION_DATA" / "_assets" / "chart.umd.min.js"` → `_assets` should be `._assets`
   - Fix: `"._assets"`

## Verification recipe (ad-hoc, run from /tmp to simulate Hermes CWD)
```python
import os, sys, tempfile, subprocess
VAULT = r"C:\Users\khoans\Documents\Warren_OS_Local"
SCR = os.path.join(VAULT, "vault", ".scripts")
# 1. no stale token anywhere in file (grep ENTIRE file, not just count)
src = open(os.path.join(SCR, "regenerate_today.py"), encoding="utf-8").read()
assert '"scripts"' not in src
assert src.count('".scripts"') >= 2  # module + main()
# 2. run from different CWD
r = subprocess.run([sys.executable, os.path.join(SCR, "gen_today_and_send.py")],
                   capture_output=True, text=True, cwd=tempfile.gettempdir(), timeout=60)
assert r.returncode == 0, r.stderr
print("PASS: runs from /tmp, imports _send_telegram OK")
```
11-check version covers all 3 scripts + E2E from /tmp → all PASS.

## Lessons
- Bulk `.replace()` catches module-level strings but MISSES local-var shadows inside functions. Grep the whole file for the old token.
- `VAULT / "vault/.scripts"` (string appended to absolute root) is CWD-independent for the BASE but still hardcodes the sub-path → breaks if sub-folder renamed. Prefer `Path(__file__).resolve().parent` for everything.
- **Always verify from a non-vault CWD** — `cd vault && python script.py` hides CWD-relative bugs that Hermes/cron actually hit.
- Dotfolder rename was CORRECT. The fix is in the script, not reverting the folder name.
