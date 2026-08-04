# Payroll CPH — XLSX Template Variance & Robust Loader

> Learned 2026-07-08. The L'Usine monthly payroll Excel is **not schema-stable** — HR
> changes the template between months. A parser that hardcodes header position or
> filename format will break silently. Capture the resilient loader pattern here.

## Symptom (June 2026)

`payroll_cph.py` v2 (XLSX-native) failed on:
`Monthly Payroll Report (LUS) 06.2026 - OPS.xlsx`

- v2 read with `pd.read_excel(path, header=1)` → assumed a single header row at row 2.
- New file has: company letterhead (rows 1-4) + `PAYROLL DETAILS SHEET - JUN 2026`
  + 2 blank rows + a **2-row header** (row 10 = short labels `No.`/`Full Name`/...,
  row 11 = sub-labels `SI (17.5%)`/...) + data from row 13.
- v2 period regex `\b(January|...|June) (\d{4})\b` could not match filename `06.2026`
  (no month word) → would need explicit `YYYYMM` arg.

Real data integrity note: June had **9 resignees**, 6 concentrated in **LU3 FOH**
→ FOH Management / FOH Floor Lead / FOH Bar Team all computed to **0** because every
employee in those segments was a resignee (correctly excluded). That zero is a
*real structural vacancy*, NOT a loader bug. Do not "fix" zeros by re-including
resignees — flag for Warren.

## Fix — `payroll_cph_robust.py` (template-resilient variant)

Lives in `vault/10_OPERATION_DATA/parsers/`. Same math as v2 (Total cost to Company
minus incentives, CPH = cost/hours, segment mapping, resignee exclusion, Hong Han
halving, red flags) — **only the loader changed**.

### Header auto-detection
```python
import openpyxl
wb = openpyxl.load_workbook(path, data_only=True)
ws = wb.active
header_row = None
for i in range(1, min(ws.max_row, 40) + 1):
    row_vals = [str(ws.cell(i, c).value).strip().lower()
                for c in range(1, 30)]
    if "no." in row_vals and "full name" in row_vals:
        header_row = i
        break
df = pd.read_excel(path, sheet_name=0, header=header_row - 1, dtype=str)
# Drop column-number junk row (No. is digit AND Full Name is digit) + blanks
df = df.dropna(subset=["No."])
df = df[df["No."].str.strip() != ""]
df = df[~df["Full Name"].astype(str).str.strip().str.isdigit()]
df = df[df["Full Name"].astype(str).str.strip() != ""]
```

### Flexible period parsing
```python
m = re.search(r"\b(January|...|December)\s+(\d{4})\b", stem, re.IGNORECASE)
if m:
    yyyymm = m.group(2) + MONTH_MAP[m.group(1).lower()]
else:
    m2 = re.search(r"\b(\d{2})\.(\d{4})\b", stem)   # "06.2026"
    if m2:
        yyyymm = m2.group(2) + m2.group(1)
# Fallback: require explicit YYYYMM 2nd arg
```

### Reused (never duplicate) from `cph_config.py`
`SEGMENTS_ORDER`, `CPH_BENCHMARKS`, `SEGMENT_MAP`, `NON_COST_COLS` — imported, not
re-declared. Shared config rule applies to the robust variant too.

## Ad-hoc Verification (temp script)

Write to `%TEMP%/hermes-verify-cph-robust.py`, run from `vault/10_OPERATION_DATA/parsers/`,
assert:
- exit 0
- `Detected header row: 11` present
- `Filtered to 65 rows in LU3/LU5/LU7`
- `Resignees Detected (9):`
- `All positions mapped - no UNMAPPED rows`
- `Using pre-computed 'Total cost to Company' column`
- `RED   LU3 | Cleaner: 40,311` and `WARN  LU7 | FOH Bar Team: 49,816`
- CSV on disk: 3 rows, `LU3 Cleaner == 40311`, `LU3 FOH Management == 0`

Then `rm` the temp file. Do NOT keep verify scripts in the vault.

## Pipeline Status (2026-07-08 → v3 redesign COMPLETE)

- `payroll_cph.py` v2 — original; **brittle to template drift**. Keep as reference only.
- `payroll_cph_robust.py` — resilient variant; **now REDUNDANT** — `payroll_cph.py` v3
  merged the robust loader AND fixed the Full-Time `Working Hours = 0` CPH bug.
  Archive/delete `payroll_cph_robust.py`.
- `payroll_cph.py` v3 — **CANONICAL**. Adaptive header detect + flexible period +
  `calc_hours()` (Full-Time → `Payable Days × 8`) + resignee exclusion + writes CSV +
  appends `_accumulation/cph.json` + prepends month block into
  `12_Wage_Structure_by_Role_Monthly.md` (idempotent on `### YYYY-MM`).
- Dashboard: `gen_cph_dashboard.py` → `CPH_Dashboard.html` (green theme,
  LU3/LU5/LU7/System filter). NO Google Sheet.
- Canonical command per `TODAY.md` / `CONTEXT.md §4`: `/cph`.
- **CRITICAL bug to never reintroduce:** Full-Time staff have blank `Total of Working
  Hours` → derive `Payable Days × 8`. Detail + verification assertions in
  `references/payroll-cph-v3-hours-and-large-write.md` §1.
- **Doc-rot WARNING:** vault files (`12_Wage_Structure_by_Role_Monthly.md`,
  `CPH_Phan_Tich_Rolling.md`) reference skill names `ops-cph-payroll`,
  `payroll-cph-engine`, `/ops-cph-payroll` that **do NOT exist** as skill files.
  Treat `payroll_cph.py` + `cph_config.py` as the real pipeline. Do not create
  phantom skills to satisfy those references — fix the references instead.

## Generalizable rule

> Any parser reading HR/Finance Excel must **auto-detect the header row** (scan for a
> known anchor like `No.`+`Full Name`) and **parse the period flexibly** (month-word OR
> `MM.YYYY` OR explicit arg). Never hardcode header row index or a single filename
> format for externally-produced spreadsheets — they drift without notice.
