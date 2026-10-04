# Deterministic Parser Review Checklist

When reviewing a deterministic parser (Excel/CSV/JSON → structured output), the standard 5-axis review applies, but these specific correctness patterns are the most common failure modes.

## Hardcoded Row/Column Indices

**Problem:** The parser assumes Excel layout never changes. A single extra row (new store, new header line, blank row) silently shifts all data.

**What to check:**
- Every `range(a, b)` and `rows[i]` reference
- Every hardcoded column index (`row[0]`, `row[5]`)
- Are indices 0-based or 1-based? Excel row numbers vs Python list indices.

**Mitigations:**
- Row count guard: `if len(rows) < MIN_EXPECTED: warn/fail`
- Column validation: check header cell values before trusting positions
- Store-code filter: filter by expected set (`{"LU3", "LU5", "LU7"}`) to reject garbage rows

## Worksheet Name Assumptions

**Problem:** `wb["Sheet Name"]` raises `KeyError` if renamed.

**What to check:**
- Sheet names are hardcoded → guard them with `if name not in wb.sheetnames: return error`
- The error message should list available sheet names

## Input Validation

**Problem:** Arguments like `--prev-total abc` crash with unhelpful traceback.

**What to check:**
- Every `float()`, `int()`, `json.loads()` call on user-provided data
- Every file path: does the file exist? Is it the right format?
- Fallback values when cells are None

## Arithmetic Verification

**Problem:** Floating point drift (82.99999999999997 instead of 83.0) cascades into wrong totals.

**What to check:**
- Every float value is cleaned with `round(x, 2)` (or appropriate precision)
- Cross-check: `FOH + BOH == Total` per store
- Cross-check: `Sum of stores == Grand Total` system-wide
- Delta formula: `((current - prev) / prev) * 100`

## Edge Cases

- Empty cells → None/0 handling
- Missing prev-month data (first month being tracked)
- Employee with 0 hours → skip or include?
- Night Extra Hours tracked separately → are they summed into totals?

## Idempotency

**Always verify:** Run parser twice on same input → output must be identical (sorted, rounded, formatted).

## Session Example (2026-07-02)

Real bugs found in `parse_extra_hours.py` code review:

| Finding | Severity | Fix |
|---------|----------|-----|
| `wb["TOTAL Extra Hour"]` → KeyError if sheet renamed | Required | try/except + sheetname check |
| Hardcoded row range `range(4, 10)` skipped LU3 FOH row | Required | Corrected to `range(3, 9)` + row count guard |
| `float(sys.argv[idx])` → crash on non-numeric input | Important | try/except with friendly message |
| Floating point artifacts in raw Excel values | Required | `round(x, 2)` on every cell read |
