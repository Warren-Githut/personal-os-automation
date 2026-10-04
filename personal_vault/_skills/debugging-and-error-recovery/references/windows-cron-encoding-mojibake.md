# Windows Cron Encoding Mojibake

## Symptom

Telegram receives garbled text when a `no_agent=True` cron script runs on Windows:

```
ðŸ“Š Frameworks.md — Macro update (2026-06-24)
   â†’ Brent tÄƒng â†’ GAS/PVD hÆ°á»Ÿng lá»£i (doanh thu â†‘)
```

Expected:
```
📊 Frameworks.md — Macro update (2026-06-24)
   → Brent tăng → GAS/PVD hưởng lợi (doanh thu ↑)
```

## Root Cause

Python on Windows has **two different stdout encodings** depending on how it's invoked:

| Execution path | Default encoding | Result |
|----------------|-----------------|--------|
| git-bash terminal (MSYS) | `utf-8` (via env vars) | ✅ Clean Unicode |
| Windows native (CreateProcess) — used by cron | `cp1252` (system ANSI) | ❌ Mojibake |

When the Hermes cron scheduler runs a `no_agent=True` script, it uses Windows native process creation (not git-bash). Python detects the console encoding as cp1252, writes UTF-8 bytes to stdout, but the scheduler reads them as cp1252 → mojibake.

## Diagnosis

### Local test passes but cron fails

```bash
# Terminal (git-bash) — always works
python3 script.py
# → 📊 Clean output

# But cron (Windows native) — garbled
# Simulate by decoding raw bytes as cp1252:
python3 -c "
import subprocess, sys
p = subprocess.run([sys.executable, 'script.py'], capture_output=True)
raw = p.stdout
print(raw.decode('cp1252', errors='replace'))
# → ðŸ“Š (mojibake confirmed)
"
```

### A/B test methodology

```python
# Variant A: no fix → mojibake via cp1252
# Variant B: with reconfigure → clean via UTF-8

import sys, subprocess

for code, label in [
    ('import sys; print(chr(0x1F4CA))', 'A (no reconfigure)'),
    ('import sys; sys.stdout.reconfigure(encoding="utf-8"); print(chr(0x1F4CA))', 'B (with reconfigure)'),
]:
    p = subprocess.run([sys.executable, '-c', code], capture_output=True)
    mojibake = p.stdout.decode('cp1252', errors='replace')
    clean = p.stdout.decode('utf-8', errors='replace')
    print(f'{label}: mojibake={repr(mojibake)} | clean={repr(clean)}')
```

## Fix

```python
import sys
# Must be called BEFORE any print() statements
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
```

Place this IMMEDIATELY after imports, at module level. `reconfigure()` is available in Python 3.7+.

## Prevention

Add to every `no_agent=True` cron script that outputs non-ASCII text (Vietnamese, emoji, arrows):

1. **Required**: `sys.stdout.reconfigure(encoding='utf-8')` after imports
2. **Document**: Add the fix to the skill's "Common Issues" section
3. **Test**: Run the A/B test above before deploying

## See Also

- `stock-marcro-framework/skills/SKILL.md` — real-world application (frameworks_cron.py)
- Python docs: `sys.stdout.reconfigure()` — available since Python 3.7
- Wikipedia: [Mojibake](https://en.wikipedia.org/wiki/Mojibake) — the general class of encoding corruption
