# W29 False-Alarm Reproduction Recipe (2026-07-20)

Concrete L'Usine hourly parser bugs that produced a 6.4% cross-source "gap" which was actually a STALE cross-check (SSOT ingested 4h earlier, parser not re-run). Two real parser defects were also found and fixed alongside.

## Bug 1 — Thousands-separator parse failure (data loss)
GSheet store-total cell `"41,864,868"` → `float("41,864,868")` raises `ValueError` → revenue silently becomes `0`.
Lost ~37M → net reported 646.7M instead of true 683.7M.

**Fix:** add tolerant coercion used everywhere a GSheet numeric cell is read:
```python
def num(v):
    if v in (None, ""): return 0.0
    try: return float(str(v).replace(",", "").strip())
    except (TypeError, ValueError): return 0.0
def to_int(v): return int(round(num(v)))
```
Replace every `float(cell)` / `int(cell)` on GSheet-derived values with `num()` / `to_int()`.

## Bug 2 — Hourly subtotal drift (misaligned pivot)
GSheet "Hourly Revenue" pivot has "HH Total" subtotal rows whose label sits in the HOUR column (col1), NOT col0. Order-type rows (Dine in, GrabFood, Split, HotLine, Delivery Now) can be misaligned by one hour group vs their subtotal. Summing raw order-type rows → LU3 hourly exceeded store-total by 10%.

**Fix:** use the "HH Total" subtotal rows as the AUTHORITY for `hourly[store][hour][day]`; order-type rows only advance the hour label. If a given hour group has NO subtotal row (observed: LU5 missing "07 Total"), fall back to summed order-types for that hour.

```python
is_hourly_subtotal = bool(re.match(r"^\d{2} Total$", str(hour_val or "").strip()))
if is_hourly_subtotal:
    # authority row — overwrite hourly[store][hour][day]
    ...
else:
    # order-type row: advance last_hour_str, accumulate into _order_acc fallback
    ...
# after loop: for hour in _order_acc: if hour not in hourly[store]: use fallback
```

## Bug 3 — Cross-source reconcile false alarm (the root cause Warren flagged)
Parser run BEFORE SSOT W29 ingest → cached W29-vs-W28 cross-check → reported 6.4% gap 🔴.
Re-run AFTER ingest → W29-vs-W29 = 0.1% net / 0.3% covers (PASS).

**Fix (governance + code):** see SKILL.md R1–R5. Parser `cross_check_ssot()` now prints explicit:
`> ✅ **SSOT tuần W29 CÓ MẶT** — cross-check so CÙNG tuần (không so vs tuần trước).`

## Verify gate (baked-in)
After building `daily_totals` + `hourly`, assert per store:
`Σ hourly[Hr][day].covers == daily_totals[day].covers` and `Σ hourly[Hr][day].revenue_net ≈ daily_totals[day].revenue_net (≤1%)`.
FAIL → `sys.exit(2)`, do NOT write. This catches Bug 2 at parse time.

## W29 final numbers (reconciled)
| Metric | Hourly | SSOT | Diff |
|--------|--------|------|------|
| Net Rev | 683,672,941 | 684,550,556 | 0.13% |
| Covers | 2,590 | 2,583 | 0.27% |
| LU3 / LU5 / LU7 net | 242.5 / 197.1 / 244.1M | 243.0 / 197.8 / 243.7M | -0.2% / -0.4% / +0.2% |

## Battle-test (temp script, %TEMP%)
1. SSOT W29 present → output has "CÓ MẶT" + "Khớp", no "DATA GAP".
2. SSOT W99 absent → output has "DATA GAP", no "CÓ MẶT".
3. Re-run reads latest SSOT (no cache).
4. W29 net 683.7M vs SSOT 684.6M = 0.13%; covers 2590 vs 2583 = 0.27%.
