# Payroll XLSX → Role-Breakdown Headcount (L'Usine)

Technique for parsing the monthly L'Usine payroll Excel (`Monthly Payroll Report (LUS) MM.YYYY - OPS*.xlsx`)
into role-level Active headcount (FOH / Bar / BOH / Cleaner / Office) to drive `Manpower_Master.md` Block 2/3.

## Why markitdown, not liteparse
- liteparse (OCR) FAILS on spreadsheet tables — returns only a few role names, drops all numbers/columns.
- `markitdown` converts xlsx → pipe-delimited markdown reliably. Use it for ALL Office docs (xlsx/docx/pptx).
  ```bash
  python -m markitdown "file.xlsx" > file.md
  ```

## Column layout (verified on 06.2026)
- Data rows start with `| NaN | <No> | <EmpCode LUS/NM> | <Name> | ...`
- Split the line on `|`; meaningful cells (0-based after split):
  - `[2]` = No, `[3]` = EmpCode, `[4]` = Name
  - `[6]` = Location (e.g. `L'Usine Le Thanh Ton - LU3`, `LTT Office`)
  - `[8]` = Department, `[9]` = Position, `[10]` = Employee Status (Active / Resigned / Resignee)
  - `[67]` = **Total cost to Company** (numeric, VND). VERIFIED by scanning the Grand Total row for the 15.5M / 16808000 region — index 67, NOT 73.
- Skip rows where EmpCode doesn't start with `LUS` or `NM` (the Grand Total row is `| NaN | Grand Total | ...` → no code → correctly skipped).

## Categorization (Per Warren's Block 1 split: FOH=Mgmt+Service, Bar separate)
```python
def categorize(dept, pos):
    if dept == "Store - Management": return "FOH"          # RM / ARM count in FOH
    if dept == "FOH - Service":      return "Bar" if "Bar" in pos else "FOH"
    if dept == "BOH - Operations":   return "Cleaner" if "Cleaner" in pos else "BOH"
    if dept in ("Maintenance", "Operation Admin"): return "Office"  # Office = maint + F&B coord
    return "OTHER"
```
Store mapping: `"LU3" in loc`, `"LU5" in loc`, `"LU7" in loc`, `"LTT Office" in loc` → `Office`.
**Active only** = Status == `"Active"`. Resigned/Resignee excluded from Active (but counted in HC total).

## Verified June 2026 numbers (Active)
| Store | FOH | Bar | BOH | Cleaner | Office | Active | Cost(M) |
|-------|-----|-----|-----|---------|--------|--------|---------|
| LU3 | 9 | 2 | 8 | 3 | — | 22 | 164.7 |
| LU5 | 5 | 2 | 4 | 3 | — | 14 | 153.3 |
| LU7 | 6 | 4 | 7 | 3 | — | 20 | 151.8 |
| Office | — | — | — | — | 2 | 2 | 46.5 |
| Sys | | | | | | 58 | 516.2 |

LU7 Bar = 4 actual vs plan 3 → **dư 1** (Warren correction 2026-07-09).

## PITFALL — never test the writer against the real SSOT file
`update_manpower_master.py` writes directly into `Manpower_Master.md`. A test run with a fake month
(`--month 2026-07` on a June file) WILL write garbage ("July") into the production file.
**Fix:** copy both the Master and the xlsx into `%TEMP%`, rewrite `MM_PATH` in a copied script to point at
the temp copy, run, assert, then `shutil.rmtree(tmp)`. Never run the real script with a throwaway month
against the committed SSOT. If you do — `git checkout -- <file>` reverts, then re-apply the hand edits.

### Verify-on-copy recipe (ad-hoc, temp)
```python
import os, re, subprocess, tempfile, shutil
SRC_MM = r"...\Manpower_Master.md"
SRC_XLSX = r"...\01_Payroll\2026-06_LUS_payroll.xlsx"
SCRIPT = r"...\scripts\update_manpower_master.py"
tmp = tempfile.mkdtemp(prefix="hermes-verify-mm-")
mm_copy = os.path.join(tmp, "Manpower_Master.md")
xlsx_copy = os.path.join(tmp, "payroll.xlsx")
shutil.copy(SRC_MM, mm_copy); shutil.copy(SRC_XLSX, xlsx_copy)
sc = os.path.join(tmp, "update_mm.py")
code = open(SCRIPT, encoding="utf-8").read().replace(r"C:\...\Manpower_Master.md", mm_copy)
open(sc, "w", encoding="utf-8").write(code)
out = subprocess.run(["python", sc, "--xlsx", xlsx_copy, "--month", "2026-13"],
                     capture_output=True, text=True)
res = open(mm_copy, encoding="utf-8").read()
assert "### 2026-13 (latest)" in res
assert "FOH −1 / Bar −1 / BOH −1 / Cln ±0 → **−3**" in res
assert "| **Sys** | **68** | **58** | **-10**" in res
shutil.rmtree(tmp, ignore_errors=True)
```
Use a month NOT in the source (e.g. `2026-13`) to bypass the idempotency guard and prove the patch logic.

## Arithmetic discipline
Warren caught a manual sum error: `RM1 + FloorLead2 + SA4 = 7`, not 8. When transcribing parser/role
totals into the SSOT by hand, re-add the components before writing. The script computes totals from the
parsed dict, so script output is safe — hand-edited summaries are not.
