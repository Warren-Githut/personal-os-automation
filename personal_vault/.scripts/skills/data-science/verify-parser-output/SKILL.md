---
name: verify-parser-output
description: "MANDATORY fact-check gate after any LLM parses/computes from Excel/CSV/PDF. Independent recompute + cross-source diff to catch fabricated numbers, category drops, drift. Enforces Warren rule: never trust LLM, verify everything. Use after every parser/py script that reads spreadsheets and emits aggregates."
type: skill
version: 1.0
status: active
applies_to: ["Hermes Desktop"]
---

# verify-parser-output — LLM Output Fact-Check Gate

> **Warren's non-negotiable rule:** "Không bao giờ tin LLM, phải verify mọi thứ LLM nói."
> After ANY LLM parses/computes from a file (Excel/CSV/PDF/screenshot), this gate is MANDATORY before the result is trusted, committed, or shown to Warren.

## When to use
- After a parser/script reads a spreadsheet and outputs aggregates (counts, sums, cost, balances, P&L, % change).
- After LLM "calculates" anything from tabular data — even if it looks confident.
- Before committing parser output to vault / before reporting numbers to Warren.

## The 4-Step Gate (all 4 required)

### Step 1 — Independent Recompute (NEVER reuse LLM's code)
Write a FRESH script. Do NOT copy the LLM's parsing logic. Re-derive from raw source with different method if possible.
- If LLM used markitdown -> you can reuse markitdown, but recompute aggregates from scratch with your own row-loop.
- If LLM used openpyxl -> use markitdown instead, or vice versa (method diversity catches method-specific bugs).

### Step 2 — Cross-Source Assert
Compare LLM output vs your recompute on EVERY emitted number:
- Per-row category assignment (did any row get dropped to "OTHER"? e.g. mã CK rỗng nhưng dòng tổng có trị giá)
- Totals / sums / averages / balances
- Derived metrics (P&L = giá - vốn, % thay đổi, room còn lại)

### Step 3 — Category Drop Scan (HIGH-PRIORITY for bank/health logs)
LLMs silently drop rows with empty/malformed keys. Scan for:
- Rows where mã/chỉ-tiêu is NaN/empty but description/category is valid -> these often belong to a known line.
- Count len(rows_after_filter) vs len(raw_data_rows). Any mismatch = dropped rows = investigate.

### Step 4 — Emit Verification Report
Print explicit ad-hoc verification (not "suite green"):
```
VERIFY [parser_name]:
  Recompute method: <markitdown row-loop / openpyxl / ...>
  LLM said: <key numbers>
  Independent recompute: <key numbers>
  MATCH: <per-metric PASS/FAIL>
  Dropped rows: <count + reason>
  RESULT: PASS | FAIL
```
Temp script under C:\Users\khoans\AppData\Local\Temp with hermes-verify- prefix. Clean up after.

## Hard Rules
- A parser result with NO verification report = UNTRUSTED. Do not commit, do not report as fact.
- If recompute disagrees -> LLM is wrong until proven otherwise. Show both, flag the delta.
- Never "fix" the recompute to match LLM. Fix the LLM's logic (or report the bug).

## Reusable Template (Python)
```python
# hermes-verify-<parser>_.py — independent recompute
import subprocess, tempfile, os
from collections import defaultdict

XLSX = r"<path/to/source.xlsx>"
# Step 1: fresh parse (markitdown if LLM used openpyxl, vice versa)
md = tempfile.mktemp(suffix=".md")
subprocess.run(["python","-m","markitdown",XLSX], stdout=open(md,"w",encoding="utf-8"),
               stderr=subprocess.DEVNULL, check=True)

# Step 2: independent row-loop, YOUR OWN categorize()
cat = defaultdict(lambda: defaultdict(int))
for ln in open(md, encoding="utf-8").read().splitlines():
    if not ln.startswith("|"): continue
    c = [x.strip() for x in ln.split("|")]
    # adapt to your columns: code, category, amount, ...
    code, cat_name, amt = c[1], c[2], c[3]
    if not code: continue
    st = categorize_line(cat_name)   # your own, handles NaN keys
    if st == "OTHER": continue
    cat[st]["sum"] += float(amt)

# Step 3: cross-assert vs LLM's claimed numbers
print("Independent recompute:", dict(cat))
print("VERIFY_RESULT: <compare>")
os.unlink(md)
```
Replace categorize_line with domain logic. The point: write it yourself, don't trust the LLM's version.

## Worked Example — bank statement balance (2026-07-09)

LLM parsed bank statement, categorized by mã giao dịch only -> hàng "SỐ DƯ CUỐI KỲ" có format khác (không có mã) -> LLM rớt -> tính sai số dư cuối kỳ. Independent recompute categorized by **description** (fallback khi mã rỗng) -> số dư khớp thực tế. Caught before commit.

```python
def line_of(desc, code):
    if "SỐ DƯ CUỐI KỲ" in desc: return "CLOSING_BALANCE"
    if code in ("CK", "TT"): return "TRANSFER"
    return "OTHER"
```

Test-on-copy protocol (never test against production SSOT): `references/verify-test-protocol.md`.

## Integration
- Parser skills (capture-sleep, legal-document-ingest, bctc-pdf-ingest, personal-morning-brief, saigon-weather-data) MUST call this gate at the end of their workflow (they carry a MANDATORY VERIFY GATE block).
- After any parser run, Hermes runs verify-parser-output before reporting.
- If parser is in a cron job -> the cron prompt must include "run verify-parser-output gate, report MATCH/FAIL in delivery".
- Skill applies to ALL Hermes profiles (warren / stock / personal). stock-profile/skills is a SYMLINK to warren-profile/skills (shared); personal_profile/skills is a separate real dir. Patch the canonical warren-profile copy to propagate to stock-profile; a blocked cross-profile write means the target is shared, not missing.

## Pitfalls (from real failures)
- Bank statement drop: hàng "TOTAL" hoặc "SỐ DƯ CUỐI KỲ" có format khác -> LLM rớt -> sai số dư. Scan kỹ các dòng tổng.
- Stale verification: citing an old ad-hoc run's numbers as "evidence" for new code = invalid. Re-run on CURRENT changed files.
- String-match false FAIL: auto-generated markdown spacing differs from hand-format -> regex assert fails though logic is correct. Use loose \s* regex or parse semantically, not exact-string.
- Cross-profile symlink trap: stock-profile/skills is a SYMLINK to warren-profile/skills; personal_profile/skills is a real separate dir. A blocked cross-profile write when editing "stock-profile" skills means the target is shared/canonical, NOT missing. Run `ls -la <profile>/skills` before patching to confirm.
- Cross-profile symlink trap: stock-profile/skills is a SYMLINK to warren-profile/skills; personal_profile/skills is a real separate dir. A blocked cross-profile write when editing "stock-profile" skills means the target is shared/canonical, NOT missing. Run `ls -la <profile>/skills` before patching to confirm.
