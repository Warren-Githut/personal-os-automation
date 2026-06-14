---

description: "Log parsing pipeline (auto-detect → select → run → insight check → commit) adapted for Hermes+Deepseek toolchain."
updated: 2026-06-02
---

# /process-logs
# v2.0 | 2026-05-26
# A single command — Hermes auto-detects and asks which parser to run.
# v2.0: Added WIKI INSIGHT CHECK after parse — surfaces potential insights, Warren decides which to /ingest.

---

## Usage

```
/process-logs
```

No arguments needed. Hermes automatically:
1. `list_files(path="_inbox/exports/")` check new files
2. Ask Warren which parser to run (if multiple options)
3. Run and write log

---

## AUTO-DETECT FLOW

When Warren types `/process-logs`, Hermes follows this order:

### Step 1 — Scan inbox
```
list_files(path="_inbox/exports/"):
- *.csv          → GrabFood parser
- *HR*.xlsx      → HR parser
- *.png / *.jpg  → Revenue parser (needs 4 files)
```

### Step 2 — Ask Warren
If files exist → list and ask confirm:
```
Found in _inbox/exports/:
  [1] grabfood_w20.csv → run GrabFood parser (06_GrabFood_Weekly_Log)
  [2] HR_May.xlsx      → run HR parser (02_HR_Weekly_Log)

Run all? [Y/n] or type number to select:
```

If no files → ask:
```
No new files found in _inbox/exports/.
Which parser do you want to run?
  [1] COGS Supplier  — 03_COGS_Supplier_Monthly_Log (end of month)
  [2] LTO            — 04_LTO_Weekly_Log
  [3] Google Reviews — 05_Google_Review_Weekly_Log
  [4] GrabFood       — 06_GrabFood_Weekly_Log
  [5] Revenue        — 01_Weekly_Revenue_Log
  [6] HR             — 02_HR_Weekly_Log
  [7] COL Weekly     — 07_COL_Weekly_Log
```

### Step 3 — Run parser (parallel when running multiple)
If Warren selects "run all" or selects ≥2 parsers:
  → Run PARALLEL: use multiple `execute_command()` calls in the same message, 1 call per parser
    with `LUSINE_HEADLESS=1`. Do not wait for previous parser to finish before running next.
  → After all complete: display combined summary (pass/fail per parser).
If Warren selects 1 parser: run normally, display preview output, confirm before writing.

### Step 4 — Cleanup
After successful write → ask Warren if they want to delete files in `_inbox/exports/`.

---

## Parser Registry

| # | Parser | Script | Source | Output Log | Frequency |
|---|--------|--------|--------|------------|-----------|
| 1 | COGS Supplier | `.claude/skills/cogs_parser.py` | GSheet PRICE_CHANGE | `03_COGS_Supplier_Monthly_Log.md` | End of month |
| 2 | LTO | `.claude/skills/lto_weekly_parser.py` | GSheet tab "LTO Log" | `04_LTO_Weekly_Log.md` | Weekly |
| 3 | Google Reviews | `.claude/skills/google_review_parser.py` | GSheet tab "Google Review Log" | `05_Google_Review_Weekly_Log.md` | Weekly |
| 4 | GrabFood | `.claude/skills/grabfood_parser.py` | GSheet tab "Grabfood" | `06_GrabFood_Weekly_Log.md` | Weekly |
| 5 | Revenue | **MANUAL** — Warren paste screenshot Power BI | PNG → Hermes extract | `01_Weekly_Revenue_Log.md` | Weekly |
| 6 | HR | `.claude/skills/hr_movements_parser.py` | Excel drop (HR sends Friday) | `02_HR_Weekly_Log.md` | Weekly |
| 7 | COL Weekly | `.claude/skills/col_weekly_parser.py` | GSheet COL_Weekly | `07_COL_Weekly_Log.md` | Weekly |

GSheet ID (all parsers): `1ZtIocc_Ic1z-tO1JGd4ZLnRB_7ZHHkvpJ5emaWJyeEE`

---

## Flag Logic (COGS)
- 🔴 `>13%` — needs menu pricing review immediately
- 🟡 `5–13%` — monitor
- 🟢 `<-5%` — COGS benefit
- ⚠️ missing volume → `N/A`, footnote count of items

## Log vs Wiki
- **Log** = data + flags + 1-line insight per red flag
- **Wiki** = deep analysis → use `/ops-ingest` afterwards
- ⚠️ **Wiki writes NEVER auto-fire from /process-logs.** Warren must explicitly confirm before any wiki page is created.

---

## ═══ WIKI INSIGHT CHECK (auto after all parsers complete) ═══

*Purpose: After all log entries are written, surface potential wiki-worthy insights for Warren to review. NEVER auto-write to wiki.*

After all parsers finish and logs are written, Hermes scans the output and presents:

```
📝 POTENTIAL WIKI INSIGHTS (from this run)

If there are 🔴 flags or noteworthy insights:
  [1] [parser name] | [flag/insight 1-line] | Confidence: [HIGH/MOD]
  [2] [parser name] | [flag/insight 1-line] | Confidence: [HIGH/MOD]
  ...

Which to /ops-ingest into wiki? Type number (1, 2...) or "none".
```

**Rules:**
- Only surface items with 🔴 flags OR clear trend breaks vs previous period.
- Each suggestion must include a confidence tag [HIGH/MOD/LOW].
- If Warren selects a number → Hermes triggers `/ops-ingest [filename] [domain]` with the corresponding raw file. Do NOT write wiki directly.
- If Warren says "none" → skip. No wiki touched.
- If no noteworthy insights → skip this block silently. Do not show empty.

Wait for Warren. No wiki write occurs without explicit number selection.

---

## Error Handling

| Error | Handling |
|-------|----------|
| GSheet fails to load | Notify + retry |
| No files in inbox | Show parser selection menu |
| Month already has entry | Ask overwrite or skip |
| Abnormal volume data | Flag ⚠️, do not crash |

## --- POST-OP: SYSTEM_VIEW Update ---

After all parsers complete and logs are written:
1. Read 0_CORE_LOGIC/SYSTEM_VIEW.md\
2. Update sections matching the parser(s) just run:
   - Revenue parser ? update \## ?? REVENUE\
   - COL parser ? update \## ?? LABOUR\
   - Google Reviews parser ? update \## ? GOOGLE REVIEWS\
   - LTO parser ? update \## ?? LTO\
   - GrabFood parser ? update \## ?? GRABFOOD\
   - HR parser ? update headcount in \## ?? LABOUR\
   - COGS parser ? skip (COGS not tracked in SYSTEM_VIEW)
3. Update \last_updated\ in frontmatter to today

### POST-OP: SYSTEM_VIEW Update

After all parsers complete and logs are written:
1. Read 00_CORE_LOGIC/SYSTEM_VIEW.md
2. Update sections matching the parser(s) just run:
   - Revenue parser -> update "## 💰 REVENUE"
   - COL parser -> update "## 👥 LABOUR"
   - Google Reviews parser -> update "## ⭐ GOOGLE REVIEWS"
   - LTO parser -> update "## 🎯 LTO"
   - GrabFood parser -> update "## 🛵 GRABFOOD"
   - HR parser -> update headcount in "## 👥 LABOUR"
   - COGS parser -> skip (COGS not tracked in SYSTEM_VIEW)
3. Update last_updated in frontmatter to today
