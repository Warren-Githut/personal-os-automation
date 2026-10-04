# Vault SSOT Sync Wrapper Pattern (session 2026-07-07)

## Context
Warren wanted a single SSOT for manpower (`Manpower_Master.md`) replacing scattered headcount refs across `Labour_Cost_Hub.md` / `HR_Movements_*` / `Shift_Rostering.md`. `update_manpower_master.py` wraps `parse_payroll.py` to sync Actual Stock (Block 2) from payroll Excel into the SSOT, preserving Block 1 (Warren's approved plan) and Block 3 (gap/vacancy).

## Key bugs found & fixed (on REAL April Excel)
| # | Bug | Root cause | Fix |
|---|-----|-----------|-----|
| 1 | Month detected as `2026-07` for "Apr 2026" file | `parse_payroll` month_map uses full names ("april"); filename "Apr" doesn't match → `month=None` → wrapper fell back to `date.today()` | Add `--month YYYY-MM` override + filename-abbrev guess map |
| 2 | System total included "Office" (71 HC) | `parse_payroll` normalizes "ltt office"→"Office", includes in `result["system"]` | Filter to `STORE_ORDER`=[LU3,LU5,LU7], recompute sys from OPS-only |
| 3 | Newest month inserted at BOTTOM | Insert logic used `em < month` / region END | Insert before first NEWER existing (`em > month`); newest→TOP |
| 4 | Double `(latest)` after backfill | `_relabel_latest` not run / wrong regex | Strip all `(latest)`, re-add to max month, run AFTER insert |
| 5 | `vault/vault/...` FileNotFoundError | `SCRIPT_DIR.parent / "vault" / ...` — SCRIPT_DIR already = `vault/scripts` | `SCRIPT_DIR.parent / "30_KNOWLEDGE_BASE"/...` |

## Data discrepancy note (for Warren decision)
April Excel parse = 56 active (LU3 23 / LU5 12 / LU7 21). `Payroll_Manpower_Rolling.md` §April = 57 active (LU3 22 / LU5 14 / LU7 21). LU5 off by 2. Excel = payroll source-of-truth (CFO); Rolling = manual summary. Recommend Excel as canonical for Block 2; note discrepancy vs Rolling.

## Condensed verify script (ad-hoc, temp)
```python
# hermes-verify-<name>.py  — run from vault/scripts, uses REAL source + fixture
import subprocess, sys, re, tempfile, openpyxl
from pathlib import Path
import update_manpower_master as u
tmp = tempfile.mkdtemp(prefix="hermes-verify-")
mc = Path(tmp)/"MM.md"; mc.write_text(u.MASTER_DEFAULT.read_text(encoding="utf-8"), encoding="utf-8")
apr = r"C:/Users/khoans/Documents/Warren_OS_Local/.hermes/desktop-attachments/Monthly Payroll Report (LUS) Apr 2026 - OPS.xlsx"
r1 = subprocess.run([sys.executable,"update_manpower_master.py",apr,"--month","2026-04","--master",str(mc),"--apply"],capture_output=True,text=True)
# fixture for newer month
fx = Path(tmp)/"aug.xlsx"; wb=openpyxl.Workbook(); ws=wb.active; ws.title="Payroll Aug 2026"
hdr=[""]*81
for i,h in [(3,"Emp. Code"),(4,"Full Name"),(5,"Division"),(6,"Location"),(7,"Dept"),(8,"Function"),(9,"Position"),(10,"Status"),(21,"Days"),(22,"Hours"),(23,"OT"),(25,"Gross"),(26,"OT$"),(28,"Meal"),(36,"SVC"),(57,"Cost"),(77,"Net")]:
    hdr[i-1]=h
for i,h in enumerate(hdr,1):
    if h: ws.cell(row=1,column=i,value=h)
# 3 OPS rows (LU3/LU5/LU7) with col indices from cm dict below, Grand Total at col 2/57
# ... build rows, save, then:
r3 = subprocess.run([sys.executable,"update_manpower_master.py",str(fx),"--month","2026-08","--master",str(mc),"--apply"],capture_output=True,text=True)
c = mc.read_text(encoding="utf-8")
assert "APPLIED" in r1.stdout and "APPLIED" in r3.stdout
assert "### 2026-08 (latest)" in c
assert "### 2026-05 (latest)" not in c and "### 2026-05" in c   # NO trailing space
assert c.find("### 2026-08") < c.find("### 2026-05") < c.find("### 2026-04")
assert c.count("(latest)") == 1
print("RESULT: ALL PASS")
import shutil; shutil.rmtree(tmp, ignore_errors=True)
```
Column-index map for fixture rows: `cm={"No":2,"Code":3,"Name":4,"Div":5,"Loc":6,"Dept":7,"Func":8,"Pos":9,"Status":10,"Days":21,"Hours":22,"OT":23,"Gross":25,"OT$":26,"Meal":28,"SVC":36,"Cost":57,"Net":77}`.

## Truncated month-map guess (for wrapper)
```python
guess_map = {"jan":"01","feb":"02","mar":"03","apr":"04","may":"05","jun":"06",
             "jul":"07","aug":"08","sep":"09","oct":"10","nov":"11","dec":"12"}
```
