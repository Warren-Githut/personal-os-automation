# COL Parser Bug Fix — 2026-07-25 (reproduction + class lesson)

> Warren-profile parser-fix worked example. Class lessons are durable; specific files
> may drift — re-read them before acting.

## Symptom
COL Telegram Preview showed `LU5 Rev=24,893,460 | COL=23.75% | [FAIL]` and a false
`⚠️ VERIFY DRIFT ... 268.9%` warning on a brain dump where all 3 stores had real
revenue (~24.9M / 32.5M / 35.8M).

## Root cause (2 bugs, chained)
1. **Format gap:** Warren pastes revenue as `Total Net Revenue: 24.893.500` inside each
   store's DAILY SALES REPORT block. `ops_col.parse_brain_dump` only matched the
   `LU3: <num>` token -> got 0 revenue for all stores.
2. **Fallback scope-blindness:** `col_deterministic_watcher._detect_lu5_guest_ac_revenue`
   grabbed the GLOBAL first `Guest` (90, from LU3 block) x first `AC` (276,594, LU3) =
   24,893,460 and injected it as LU5 revenue. Preview showed LU5 = LU3's revenue, LU3/LU7 = 0.

Latent tech-debt: `_lu5_revenue_bounds()` iterated `for week in history:` but
`ops_col.load_history()` returns a DICT `{(date,store): {'Rev':...}}` -> `week` was a
tuple -> `.get("stores")` raised, silently fell back to wide range.

## Key lessons (class-level)
- **Parser fallbacks that derive a value from text MUST scope to the correct section,
  never grab the global first-match.** Global-first regex on multi-store dumps leaks
  data across stores. Split by store section (same regex as the main parser) and
  extract within that section. (`_extract_store_section` helper = the fix pattern.)
- **Verify gates can false-alarm when the parser itself is broken.** The drift check
  compared Σ(Guest×AC) vs the (garbage) parsed total -> phantom 268.9%. Real data was
  consistent (true sum vs Σ(Guest×AC) = 1.45% diff). When a verify warning fires, first
  sanity-check the parser's per-store outputs before trusting the warning.
- **Match the data structure, not the assumption.** `load_history()` returns a dict, not
  a list of weeks. Iterating it yields tuple keys. Read the source function before
  writing loops over its return value.

## Fix summary
- `ops_col.py`: extract `Total Net Revenue: X` bound to the CURRENT store section
  (inside the store_sections loop). Guard keeps the larger of token vs TNR revenue.
- `col_deterministic_watcher.py`: added `_extract_store_section()` (identical split
  regex to ops_col); `_detect_lu5_guest_ac_revenue` now scopes Guest/AC to LU5's own
  block; added >=2-stores-missing guard to skip injection; fixed `_lu5_revenue_bounds`
  to iterate `history.values()` and read `rec['Rev']`.
- `tests/test_ops_col.py`: fixed stale `HEADER_43`->`HEADER_44` + len 43->44; added
  regression tests test_6/7/8.

## Reproduction (real-input, no GSheet needed for the parse path)
```python
import importlib.util, pathlib
spec = importlib.util.spec_from_file_location('w', str(pathlib.Path('col_deterministic_watcher.py')))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
dump = """LU3 DAILY SALES REPORT JULY 24
Total Net Revenue: 24.893.500/776.318.906
Guest: 90
AC: 276.594

LU5 DAILY SALES REPORT JULY 24
Total Net Revenue: 32.471.400 / 705.207.230
Guest: 111
AC: 280.360

LU7 DAILY SALES REPORT JULY 24
Total Net Revenue: 35.820.800/ 768.546.500
Guest: 110
AC: 325.644
"""
parsed = m._compute_col(m._reformat_brain_dump(dump))
# Fixed: LU3=24,893,500 LU5=32,471,400 LU7=35,820,800, no drift warning.
```
