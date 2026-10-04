# Payroll CPH v3 — Working Hours Bug & Large-Write Timeout

> Learned 2026-07-08 during the CPH-system redesign (input template → pipeline v3 →
> `12_Wage_Structure_by_Role_Monthly.md` SSOT + `CPH_Dashboard.html`). Two non-trivial
> failure modes surfaced that any future payroll_cph maintenance must know.

## 1. Full-Time `Total of Working Hours = 0` CPH BUG

**Symptom (v3 first cut):** CPH exploded for some segments — LU7 FOH Bar Team computed
**410,430 VND/hr** (correct: 49,816); LU3 BOH Cook **1.5M** (correct: 45,969).
CPH = Total cost / (headcount × hours). The divisor collapsed because
`Total of Working Hours` is **blank (0) for Full-Time staff** — their hours are derived
from `Total of Payable Days × 8`, not entered in that column. Part-time staff DO have the
column filled. Dividing cost by ~0 explodes CPH.

**Root cause:** `hours = float(row['Total of Working Hours'] or 0)` ignored Working Type.

**Fix — `calc_hours(row)` (shipped in `payroll_cph.py` v3):**
```python
def calc_hours(r):
    wtype = str(r[ci_wtype]).strip().lower() if ci_wtype >= 0 and r[ci_wtype] else ""
    days  = float(r[ci_days] or 0) if ci_days >= 0 else 0.0
    wh    = float(r[ci_hours] or 0) if ci_hours >= 0 else 0.0
    if "full" in wtype and days > 0:
        return days * 8.0
    return wh
```
Requires three column indexes from the detected header row:
- `ci_hours = col_index(hdr, "total of working hours", "tổng số giờ làm việc")`
- `ci_days  = col_index(hdr, "total of payable days", "tổng số ngày trả lương")`
- `ci_wtype = col_index(hdr, "working type", "hình thức làm việc")`

**Verification after any hours change:** re-run on the known-good June file and assert
`LU7 FOH Bar Team ≈ 49,816` and `LU3 BOH Cook ≈ 45,969` (cross-check vs hand-verified
May→June deltas). A segment computing to 0 with NON-zero cost is the hours-bug signature.

**Generalizable rule:** for HR/Finance XLSX where hours may be derived, NEVER use a single
"working hours" column directly. Check Working Type and derive from payable days for
Full-Time. This blank-derived-column class of bug recurs across payroll templates.

## 2. Large `write_file` Stream Timeout — Split Markdown Into Chunks

**Symptom:** writing a large vault markdown (CPH SSOT keeper: frontmatter + exec summary +
2 monthly delta tables + resignee log + quarterly + hidden JSON) via ONE `write_file` call
**timed out the stream** — content never delivered, file left unwritten. Distinct from the
known `patch` fuzzy-match *indentation corruption* issue (that is about edit matching;
this is about payload size killing the stream).

**Fix — chunk large writes:**
1. `write_file` the **frontmatter + first human section** (small).
2. `patch` (mode=replace, anchor a unique trailing line) to **append** the next block.
3. Repeat per logical block (resignee log, quarterly, methodology).
4. Hidden JSON block: build the JSON in a **temp Python script**, then `patch` the
   `<!-- CPH_JSON ... -->` marker line (single targeted replace). Do NOT inline a
   multi-KB JSON literal into a `write_file`/`patch` argument.

**Safe limit observed:** keep any single tool-call argument **under ~8K tokens**. Files
exceeding that MUST be chunked. Applies to `write_file` AND large `patch` `new_string`.

## 3. Idempotent Month-Block Insertion (avoid duplicate `### YYYY-MM`)

When a pipeline prepends a month block into a markdown SSOT, format the header with a
dash (`### 2026-06`) — NOT the raw `YYYYMM` (`### 202606`). The idempotency regex
`^### 2026-06\b` will NOT match a `### 202606` block, causing a duplicate on re-run.
v3 uses `disp = f"{yyyymm[:4]}-{yyyymm[4:]}"` for both the block header and the skip-check.
Also: if a prior buggy run already inserted a `### 202606` block, remove it (line-based
scan + skip until the blank after the `| Sys` row) before re-running, or the keeper
accumulates duplicates.
