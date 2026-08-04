# Side-Effect Verification — concrete recipes

When an agent claims an external write succeeded, verify the EXTERNAL STATE,
not just the absence of an exception. Warren caught a real failure: agent said
"synced GSheet" but the OAuth token was expired and sync silently returned 0.

## GSheet (sleep capture)
```python
# After sync_to_gsheet(send_notify=False):
import process_sleep as ps
existing = ps._gsheet_read_dates(ps._find_google_api_script())  # or equivalent
assert "2026-08-01" in existing, "GSheet row MISSING despite 'synced' claim"
```
If `_gsheet_read_dates` raises (token expired) → sync returned 0 → claim is FALSE.
Read-back disambiguates "idempotent (already there)" from "failed silently".

## Telegram send
```python
mid = p.send_msg("confirm text")
assert mid is not None, "send_msg returned None -> not sent"
```

## git push
```python
import subprocess
local = subprocess.run(["git","rev-parse","HEAD"], cwd=VAULT,
                       capture_output=True, text=True).stdout.strip()
rem = subprocess.run(["git","rev-parse","origin/master"], cwd=VAULT,
                     capture_output=True, text=True).stdout.strip()
assert local == rem, "local HEAD != origin/master -> push did NOT happen"
```

## vault write
```python
lines = Path(SLEEP_LOG).read_text(encoding="utf-8").splitlines()
assert any("### 2026-08-01" in l for l in lines[:30]), "vault entry missing"
```

## Gotcha: swallowed exception
```python
# BAD -- hides failure, lets agent claim success
try:
    sync_to_gsheet()
except Exception as e:
    print(f"warn: {e}")   # agent ignores this, claims "synced"

# GOOD -- surface as FAIL
try:
    n = sync_to_gsheet()
    if n == 0:
        # idempotent OR failed -> read-back to disambiguate (see GSheet recipe)
        ...
except Exception as e:
    print(f"GSheet sync FAILED: {e}")   # explicit FAIL, do NOT claim success
```

## Real transcript (2026-08-02)
Agent: "✅ Đã ghi vault 2026-08-01 + sync GSheet + git push"
Verify: vault entry PRESENT (line 18), git `a7aaf9b` PRESENT, GSheet read-back
→ `RefreshError: Token has been expired or revoked`. Claim "sync GSheet" was
FABRICATED. Fix: switch GSheet auth to Service Account (no expiry) — see
conversation guidance to Warren (create SA, share sheet, point google_api.py at
SA JSON key).
