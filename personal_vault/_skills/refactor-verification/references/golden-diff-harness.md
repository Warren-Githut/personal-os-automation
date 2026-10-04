# Golden-Diff Harness — reusable probe template

A probe that runs a case matrix through the real call path and dumps output for byte-level diffing.

## Minimal template

```python
#!/usr/bin/env python3
"""Golden-output capture. Usage: python3 hermes-golden.py out.txt"""
import sys
from pathlib import Path

sys.path.insert(0, r"<repo>/scripts")
import module_under_test as m

OUT = Path(sys.argv[1])
lines = []

def emit(label, result):
    lines.append(f"[{label}]")
    lines.append(str(result))
    lines.append("")

def make_row(date, weight, bp="99/65"):
    """Same dict shape the module builds internally — history rows."""
    sysp, _, dia = bp.partition("/")
    return {"date": date, "weight_kg": float(weight), "fasting_h": 18,
            "sleep_hours": 7.5, "quality": 90, "sleep_raw": "7h30",
            "bp_systolic": int(sysp) if sysp.isdigit() else 0,
            "bp_diastolic": int(dia) if dia.isdigit() else 0}

def make_case(date, w=62, bp="99/65"):
    return {"date": date, "sleep": "7h30", "quality": "90",
            "weight": f"{w}kg", "fasting": "18h", "bp": bp}

# --- Case matrix: every branch, both sides of every threshold ---
for n in range(1, 8):                       # below / at / above a 7-day window
    hist = [make_row(f"2026-09-{d:02d}", 62) for d in range(20, 20 + n)]
    emit(f"window-{n}", m.generate_insight(make_case("2026-09-27"), hist))

for bp in ["80/50", "99/60", "99/65", "150/95", None]:   # include the None case
    emit(f"bp-{bp}", m.generate_insight(make_case("2026-09-27", bp=bp), hist))

OUT.write_text("\n".join(lines), encoding="utf-8")
print(f"wrote {len(lines)} lines to {OUT}")
```

Run: `python3 hermes-golden.py before.txt` → refactor → `python3 hermes-golden.py after.txt` → `diff before.txt after.txt`.

## Write-path probe (never touch production)

For anything that writes files, copy the data tree to a temp dir and redirect the module's path constants at it.

```python
import shutil, sys, tempfile
from pathlib import Path

REAL = Path(r"<repo>/personal_vault")
tmp = Path(tempfile.mkdtemp(prefix="probe-"))
vault = tmp / "personal_vault"
shutil.copytree(REAL / "10_PULSE", vault / "10_PULSE")
(vault / "_inbox" / "01_unprocessed").mkdir(parents=True, exist_ok=True)
(vault / "scripts").mkdir(parents=True, exist_ok=True)
shutil.copy(REAL / "scripts" / "module.py", vault / "scripts" / "module.py")

sys.path.insert(0, str(vault / "scripts"))
import module_under_test as m

# Redirect EVERY path constant the module uses, plus external side effects
m.VAULT_ROOT = vault
m.TARGET_FILE = vault / "10_PULSE" / "log.md"
m.SA_KEY_PATH = vault / "scripts" / "config" / "nonexistent.json"   # force skip remote sync
m.send_remote = lambda msg: False                                    # stub side effects

# ... run cases, then assert production is untouched:
real = (REAL / "10_PULSE" / "log.md").read_text(encoding="utf-8")
assert "### <test-date>" not in real
shutil.rmtree(tmp, ignore_errors=True)
```

## Pinning the clock for time-dependent code

```python
def parse_as(today, log_str):
    saved = (m.NOW, m.CURRENT_YEAR, m.CURRENT_MONTH)
    m.NOW, m.CURRENT_YEAR, m.CURRENT_MONTH = today, today.year, today.month
    try:
        return m.parse(log_str)
    finally:
        m.NOW, m.CURRENT_YEAR, m.CURRENT_MONTH = saved

# Multiple simulated "todays" — one date can never reach the failing branch
for today_s, log_s, want in [("2026-09-26", "oct 1", "2026-10-01"),
                             ("2026-01-01", "dec 31", "2025-12-31")]:
    got = parse_as(datetime.strptime(today_s, "%Y-%m-%d"), log_s)
    assert got == want, f"today={today_s} log={log_s}: got {got}, want {want}"
```

## Worked triage — "my test failed" was wrong three times

Each case below looked like a code bug and wasn't. In every case the *test* assumed a branch or precondition that was never met.

**1. Case landed in the wrong branch.** A case meant to exercise the "drift" branch set `delta = -1.5`, exceeding the `> 1.0` jump threshold — so it fired the jump branch, which reports a different day count. Fix: read the real output, compute the preconditions the target branch actually needs (`abs(delta) <= 1.0` AND `spread > 0.5`), and build the case from those.

**2. Case degenerated at n=1.** A single history row has zero spread, so the "stable" branch fires instead of "drift" — correct behavior. Fix: assert the branch that genuinely applies at n=1, and cover n>=2 for the other.

**3. Sanity check read `HEAD`.** `git show HEAD:file` was used to prove "the old code had the hardcoded string" — it passed, then inverted the moment the fix was committed. Fix: pin `BUGGY_REF = "<sha>"`.

**Before touching product code on any of these, confirm pre-existing:**
```bash
git stash && python3 probe.py && git stash pop    # same result => not your bug
git show <sha>:<path>:<file>                        # inspect the committed version
```

## Float comparison

```python
check("parses 8h05", abs(m.parse_duration("8h05") - (8 + 5/60)) < 1e-9)
```
`5/60 == 0.08333…`; asserting `== 8.083` is a float-precision failure that looks like a logic failure.

## Pitfall: newest-on-top logs break naive block extraction

A log that prepends newest entries means the block *after* a date is the next-newest one, not an older date. Splitting on a specific neighbouring date silently returns the wrong block (or raises IndexError). Use a marker-based split instead:

```python
m = re.search(rf"### {date}\n(.*?)(?=\n### |\Z)", text, re.DOTALL)
```
