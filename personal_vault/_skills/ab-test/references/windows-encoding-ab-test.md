# Windows Encoding A/B Test

## When to use

Comparing output encoding variants of a Python script that produces non-ASCII output (Vietnamese, emoji, symbols) on Windows — especially when the delivery path is a cron `no_agent=True` script that pipes raw stdout bytes to Telegram.

## The problem

Python on Windows defaults to different stdout encodings depending on how it's launched:
- **Via git-bash/MSYS2 terminal**: UTF-8 (MSYS2 sets `PYTHONIOENCODING` and terminal locale)
- **Via Windows native / CreateProcess (cron scheduler)**: System ANSI codepage (typically cp1252 for Vietnamese Windows)

So a script that works perfectly when run from `terminal()` may produce mojibake when run via cron `no_agent=True`.

## Test design

### Variant A — No explicit encoding
```python
import sys
# NO stdout.reconfigure — relies on Python default
print('📊 Frameworks.md — Macro update')
print('   → Brent tăng → GAS/PVD hưởng lợi (doanh thu ↑)')
```

### Variant B — Explicit UTF-8 reconfigure
```python
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
print('📊 Frameworks.md — Macro update')
print('   → Brent tăng → GAS/PVD hưởng lợi (doanh thu ↑)')
```

### Execution script
```python
import subprocess, sys

code_a = '''<Variant A code>'''
code_b = '''<Variant B code>'''

for label, code in [('A (no reconfigure)', code_a), ('B (with reconfigure)', code_b)]:
    p = subprocess.run([sys.executable, '-c', code], capture_output=True)
    raw = p.stdout  # raw bytes — same as what cron no_agent captures

    mojibake = raw.decode('cp1252', errors='replace')
    clean = raw.decode('utf-8')

    print(f'=== {label} ===')
    print(f'  As cp1252 (Telegram pipeline): {mojibake[:60]}')
    print(f'  As UTF-8 (correct):            {clean[:60]}')
    print(f'  MOJIBAKE: {mojibake != clean}')
```

## Winner logic

| Score | Condition | Verdict |
|-------|-----------|---------|
| B wins | A shows mojibake via cp1252, B clean via UTF-8 | B — cross-environment robustness |
| EQUAL | Both show same clean output | Both work (environment already UTF-8) |
| A wins | A clean, B mojibake (unlikely — reconfigure only helps) | Revert to A |

## Interpretation matrix

| Terminal test | Cron simulation (cp1252 decode) | Verdict |
|--------------|-------------------------------|---------|
| ✅ Clean | ✅ Clean | Both work. No fix needed. |
| ✅ Clean | ❌ Mojibake | **Fix needed.** Cron runs via Windows native with cp1252. Add `reconfigure(encoding='utf-8')`. |
| ❌ Mojibake | ❌ Mojibake | Encoding broken in both paths — fix script output logic first. |

## Prevention

For every `no_agent=True` script that prints non-ASCII, add this immediately after imports:

```python
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
```

This is idempotent — harmless when encoding is already UTF-8, critical when it isn't.
