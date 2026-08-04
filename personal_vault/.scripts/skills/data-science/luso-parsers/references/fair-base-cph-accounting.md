# Fair Base CPH — Accounting Formula & Pitfalls (2026-07-11)

Companion to `luso-parsers` SKILL.md §Fair Base CPH. Warren corrected the CPH formula
this session; these are the durable, reusable lessons.

## 1. The formula (Warren-approved)

```
Fair Base CPH = (Total cost to Company
                 − OT Salary − Sale Incentive − Wine Bonus
                 − Balanced Scorecard − Performance − Others
                 − AL Outstanding − OIL Outstanding)
                / Working Hours
Working Hours = Payable Days × 8 (Full Time) | Total Working Hours (PT)
```

- `cph_full` (comparison only) = `Total cost to Company / Hours` — the OLD inflated number.
- Resignee excluded from function aggregate → goes to Resignee Log.
- Edge case: `Võ Thị Hồng Hân` + `Sous Chef` → `base_cost /= 2`. Encode in pipeline AND verify recompute.
- `calc_hours` fallback: `days*8 if days>0 else (wh if wh>0 else 0.0)`. June 2026 template had WH=0 for all → FT must use Payable Days.

### Why the old formula was wrong
Prior `payroll_cph.py` summed `Total cost to Company` raw → CPH inflated ~10–30%.
Raymond (LU3 ARM, resignee) example:
- Total cost to Company = 31,985,172
- Deductions (OT 0 + SaleInc 0 + Wine 0 + BSC 0 + Perf 1,666,666 + Others 7,259,627) = 8,926,293
- AL Outstanding 2,307,692 + OIL Outstanding 3,592,308 = 5,900,000 (severance/OIL — not operating cost)
- Fair Base CPH (operating) = (31,985,172 − 8,926,293 − 5,900,000) / 208 = **82,494 ≈ 82,521** (one-off Warren used)
- Old `Total cost/Hours` = 31,985,172 / 208 = 153,873 (wildly wrong for operating rate)
- Naive pipeline (no deductions, no AL/OIL) = (31,985,172 − 8,926,293) / 208 = 110,860

→ For an ACTIVE person (Jack, LU3 RM) AL/OIL = 0, so Fair Base CPH = (24,891,935 − 3,848,400) / 207.04 = **101,640**. Same number the SSOT carries.

## 2. sync_cph_gsheet month-wipe bug (ROOT CAUSE + FIX)

**Bug:** `sync_cph_gsheet.sync(ref_period=YYYYMM)` filtered `cph.json` to ONLY that month,
then `clear(A2:I1000)` + wrote 1 month. Running May AFTER June wiped June off the GSheet.
`ops_col.load_cph()` then fell back to the wrong month → COL used stale rates.

**Fix (shipped):** `build_rows()` ignores `ref_period` and FULL-REBUILDS from all months in
`cph.json` (newest-on-top). Sync is idempotent and never drops a month. `payroll_cph.py`
calls `sync()` with NO arg.

**Verify after any sync change:** temp `hermes-verify-*.py` that reads GSheet `02_MASTER_CPH`
A1:I20 and asserts `len(data_rows) == 6` (2 months × 3 stores) and both `202605` + `202606`
present, and `June LU3 FOH == 101640`.

## 3. Verify-gate false-confidence trap

The baked-in `verify_cph_gate` recomputed with the SAME wrong formula as the pipeline →
both agreed → `VERIFY_RESULT: PASS` while output was wrong. **A gate that reuses the buggy
formula is false confidence.**

**Rule:** the gate's recompute MUST call the same `base_cost_of()` (8-deduction) the pipeline
uses. Also: the gate must not `NameError` on a missing `ci_name` (a missing column mapping
made the gate crash → "ERROR gate skipped" → silent skip). Validate ALL column indexes
(incl. `ci_name`) before the gate runs; a skipped gate is worse than a failing one.

## 4. Red Flags benchmark-tag logic

`cph_config.py` CPH_BENCHMARKS = `(floor, target, ceiling)`:

```python
def cph_tag(cph, seg):
    f, t, c = CPH_BENCHMARKS[seg]
    if cph > c:  return "🔴"
    if cph > t:  return "🟡"
    if cph >= f: return ""      # normal
    return "🔵"                  # below floor
```

Pitfall shipped wrong: tagged 🔴 on values UNDER ceiling (e.g. LU3 FOH Mgmt 101,640 < 105,000).
Only > ceiling is 🔴. In June 2026 only Cleaner (all 3 stores > 40,000) was a real 🔴.
Most segments were 🔵 (below floor) or normal.

## 5. OT cost fallback (payroll lacks OT columns)

June 2026 payroll had `OT Salary = 0` for all (template defect) → no true OT cost.
Warren-approved fallback:

```
OT Cost (estimate) = Extra_Hours(June) × Fair Base CPH(SSOT June), per position (NOT blended)
```

- Map each Extra_Hours person → position → function → store CPH via `SEGMENT_MAP` (strict dict).
- Verified June 2026 estimate: **46.9M VND** (750.75h). By store: LU3 23.77M / LU5 15.31M / LU7 7.82M.
  By function: FOH Management 20.93M (44.6%) / BOH Cook 15.43M (32.9%) / BOH Leader 7.35M (15.7%).
- Clearly label ESTIMATE; replace with real payroll OT when a file with populated OT arrives.
  Real OT is typically ~10–15% LOWER (CPH already embeds OT cost).
- Root-cause read: ~90% of June OT = understaffing (LU3 Raymond 151h coverage for vacant SA;
  LU5 BOH turnover surge), NOT management failure. Use the gap/vacancy + HTE signals, not OT alone.

## 6. One-off rate overrides are session-scoped, never SSOT

Warren: "Raymond = 82,521, Jack = 120,000 just for this estimate." Those are TEMPORARY
estimate inputs. SSOT keeps the COMPUTED rate. When a person changes store (Jack LU7→LU3),
the computed rate follows the payroll file's store — do not hardcode old-store rates into
`cph.json` or `12_Wage_Structure_by_Role_Monthly.md`. Log one-off overrides only in chat/estimate.
