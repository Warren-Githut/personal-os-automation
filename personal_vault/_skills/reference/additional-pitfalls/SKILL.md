---
name: additional-pitfalls
description: Additional pitfalls captured for ops-col skill
---
# Additional Pitfalls for Ops-Col

- **Store Index Confusion**: Store mapping in GSheet uses `row[2]` not `row[1]`; mismapping leads to wrong store updates.
- **Date Header Typo Handling**: When a re-sent block's date header contradicts context, read GSheet for both candidate dates before concluding conflict.
- **Duplicate Guard False Positive**: `Khong co du lieu nao de append` can be triggered by duplicate entries; verify by reading back GSheet row.
- **Coverage-Only Append Pitfall**: Missing `Guest: N` leads to `Covers=0` silently; always readback to verify non-zero covers.
- **Hours Alert False Positive**: Prior-week FOH-only entries cause artificially low baseline; compare FOH+Bar delta only.
- **Systemic Append Script Failure**: Repeated `Script exit code 1` across entries signals underlying append script issue; treat as systemic, not per-entry.
- **Regex Case Sensitivity**: Revenue regex case-sensitive; ensure `(?i)LU` is used to capture lowercase store codes.
- **Comma Decimal Normalization**: Hour values with comma (e.g., `6,5h`) must be normalized to `6.5h` before parsing.
- **Alert Regression Guard**: BOH alerts must fire independently; ensure separate baseline checks.
- **Auto-Stale Logic**: Entries stalled >6 runs with same error should be auto-staled; ensure proper note field population.

## approve_col() FALSE FAILURE loop — fixed & verified 2026-07-25

- **Root cause of recurring `Script exit code 1` systemic errors**: `col_queue_handler.py approve_col()` flagged failure whenever ops_col.py exited non-zero — even when (a) ops_col idempotently SKIPPED because the row already existed (stdout `Khong co du lieu nao de append`), or (b) the append actually succeeded and GSheet read-back confirmed it. Entry got stuck in `error` → retry → same skip → error, forever. stderr was never captured, so Warren saw a blind "Script exit code 1".
- **Fix (in approve_col, live-verified both paths)**:
  - FIX A: `result.stderr[-800:]` → `entry["append_stderr"]` + shown in error_reason; subprocess timeout 60→120s.
  - FIX B1: rc!=0 AND stdout contains the skip message → treated as SUCCESS.
  - FIX B2: independent GSheet read-back (date YYYYMMDD @row[0], store @row[2], revenue @row[3] vs `parse_brain_dump` expected) — all stores present & matching → SUCCESS; missing row or mismatch → hard fail. Read-back only runs when append_failed is already False, so B2 cannot mask a genuine nonzero exit without the skip message (fails safe).
- **Intentional constraint**: a dump LACKING revenue can never auto-pass verify — parsed expected rev=0 mismatches the sheet value → entry stays `error`. Resolve by including revenue in the reformatted text (note: since 2026-07-25 Option A, `parse_brain_dump` also accepts per-store `Total Net Revenue: X` lines — no `LUx: <num>` token needed).
- **Simulate-test recipe (reuse after any approve_col edit)**: write a temp script that (1) `_save_queue`-injects entry `{id:"COL-TEST-REV", status:"pending_approval", reformatted_text:<dump for a date whose rows already exist>}` into `_inbox/col_queue.json`, (2) calls `h.approve_col()` and asserts the return string ("✅ Da append" for the dup-skip path; "revenue mismatch ... vs parsed 0" for a revenue-stripped variant), (3) in a `finally` block DELETES `COL-TEST-REV` from BOTH pending and history (history is capped at 20 — a leftover test entry evicts a real record). Pitfalls: approve_col searches the queue instance IT loads, so inject via `_save_queue` before calling; use `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` on Windows to survive the ✅/❌ emojis.