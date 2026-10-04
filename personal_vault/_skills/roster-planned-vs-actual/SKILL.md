---
name: roster-planned-vs-actual
description: "Planned vs actual roster check. Alert on variance > 15%."
status: active
created: 2026-09-10
version: 1.0
triggers:
  - "roster variance check"
  - "planned vs actual hours"
  - "roster vs actual comparison"
  - "manager sent roster"
  - "workforce planning check"
  - "roster planned actual"
---

# roster-planned-vs-actual — Planned vs Actual Roster Checker

> Compare planned workforce roster (manager sends weekly) vs actual working hours (GSheet SSOT).
> Alert when variance exceeds threshold.

## When to use

- Manager sends roster for next week (typically Saturday)
- Daily check: compare today's planned vs actual hours
- Weekly summary: variance report for the week
- Investigating COL spikes (planned vs actual mismatch)

## Data flow

```
Manager Telegram (weekly) → roster_telegram_intake.py → roster_planned/YYYYMMDD.txt
                                                                    ↓
GSheet COL_Weekly (daily) → fetch_actual_hours()        → roster_vs_actual.py compare
                                                                    ↓
                                              variance > 15% → Telegram alert + vault log
```

## SSOT sources

| Data | Source | Key |
|------|--------|-----|
| Planned roster | Telegram text → parse → file | `10_OPERATION_DATA/roster_planned/YYYYMMDD.txt` |
| Actual hours | GSheet COL_Weekly (gid 1732633441) | `Total_Hours_Whole_Store` column, calendar month incl OT (ANCHOR A21) |
| Variance log | `10_OPERATION_DATA/18_Roster_Variance_Log.md` | Weekly summary |

## Procedure

### 1. Receive and parse roster (Saturday or when manager sends)

```bash
# Save roster text to file
python3 .scripts/roster_telegram_intake.py --text "<telegram message>"

# Or process file directly
python3 .scripts/roster_vs_actual.py --roster-file roster_planned/YYYYMMDD.txt --date 20260915
```

**Expected Telegram format:**
```
LU3 Roster (15-21 Sep 2026):
Mon 15/9: Mgmt 10, Lead 8, SA 36, Bar 8, CDP 8, Cook 28, Cleaner 16 = 114h
Tue 16/9: Mgmt 10, Lead 8, SA 30, Bar 6, CDP 6, Cook 24, Cleaner 16 = 100h
...

LU5 Roster:
Mon 15/9: Mgmt 8, Lead 6, SA 20, Bar 6, CDP 6, Cook 18, Cleaner 12 = 76h
...

LU7 Roster:
Mon 15/9: Mgmt 8, Lead 6, SA 20, Bar 6, CDP 6, Cook 18, Cleaner 12 = 76h
...
```

### 2. Compare planned vs actual (daily)

```bash
# Check today
python3 .scripts/roster_check_daily.py

# Check specific date
python3 .scripts/roster_vs_actual.py --roster-file roster_planned/YYYYMMDD.txt --date 20260915

# Check entire week
python3 .scripts/roster_vs_actual.py --roster-file roster_planned/YYYYMMDD.txt --week 2026-09-15

# Custom threshold
python3 .scripts/roster_vs_actual.py --roster-file roster_planned/YYYYMMDD.txt --date 20260915 --threshold 10

# JSON output (for cron)
python3 .scripts/roster_vs_actual.py --roster-file roster_planned/YYYYMMDD.txt --date 20260915 --json
```

### 3. Interpret output

- **OK**: variance within ±threshold% (default 15%)
- **🔴 OVER**: actual > planned by >threshold (overstaffed or manager added hours)
- **🔴 UNDER**: actual < planned by >threshold (understaffed, sick leave, no-show)
- **NO_ACTUAL**: planned exists but no actual data in GSheet yet

### 4. Alert and log

- Alert only fires when |variance| > threshold
- Log weekly summary to `10_OPERATION_DATA/18_Roster_Variance_Log.md`
- Cron: `roster_check_daily.py` at 08:00 daily

## Parsing rules

Segment aliases (case-insensitive):
- `Mgmt`, `Management`, `RM`, `ARM`, `Shift`, `SM` → FOH_Mgmt
- `Lead`, `Sup`, `Captain`, `Floor` → FOH_Lead
- `SA`, `Service`, `Agent`, `Svc` → FOH_SA
- `Bar` → FOH_Bar
- `CDP`, `BOH_Lead` → BOH_Lead
- `Cook`, `Commis`, `Demi`, `BOH`, `BOH_Cook` → BOH_Cook
- `Cleaner`, `Clean` → Cleaner

**Total line (`= 114h`) is required** — cross-checks sum of segments.

## Pitfalls

1. **BOH segment ambiguity**: "BOH 36" parses as BOH_Cook 36. If manager writes "CDP 8, Cook 28" separately, both parse correctly. Always prefer split format for accuracy.

2. **Date parsing**: Format `DD/MM` or `DD-MM` only. `15 Sep` (text month) not supported in current parser — manager must use numeric dates.

3. **GSheet lag**: Actual hours may not be entered until end of day. Morning checks show `NO_ACTUAL` — not an error.

4. **File naming**: Roster files must be named `YYYYMMDD.txt` (8-digit date = Monday of that week). Parser filters to `*.txt` with 8-digit numeric stem.

5. **Week boundary**: Week = Monday-Sunday (ISO). Roster file dated Monday covers the full week.

6. **Threshold tuning**: Default 15% works for most days. Friday-Saturday may need 20% (higher volume = more variance). Adjust with `--threshold`.

## Cron setup

```
0 8 * * *  roster-check-daily
  → python3 .scripts/roster_check_daily.py
  → Alert if |variance| > 15%
  → deliver: local (script sends Telegram directly)
```

## Vault structure

```
10_OPERATION_DATA/
├── roster_planned/
│   ├── 20260915.txt    ← roster for week starting Sep 15
│   ├── 20260922.txt    ← roster for week starting Sep 22
│   └── ...
└── 18_Roster_Variance_Log.md  ← SSOT variance log
```

## Dependencies

- `urllib.request` (stdlib) — GSheet gviz API fetch
- GSheet must be publicly readable (or shared with service account)
- `10_OPERATION_DATA/roster_planned/` directory must exist