# Stock Adaptation Case (warren → stock-profile, 2026-07-22)

## Starting point
warren review-gate (auto-reviewer + reviewer-node + safenet) built, scored 92/100 on warren-profile.
stock-profile already had a **verbatim copy** (same 87-line auto-reviewer) → battle-test scored **38/100** (vỏ cứng PASS, 0% domain adapt).

## Adaptations applied
1. **Created** `C:/Users/khoans/Documents/Stock_OS/stock_vault/00_CORE_LOGIC/ANCHORS.md` — 9 anchors:
   - A1 Long-term thesis bắt buộc · A2 Risk assessment bắt buộc · A3 Source tags [HIGH]/[MOD]/[LOW]
   - A4 Capital segregation (VN equities core / BTC DCA / Polymarket ≤5%, KHÔNG refill speculative từ core)
   - A5 Conviction ≠ all-in mù quáng (margin of safety) · A6 Comparison > absolute · A7 Min data window ≥4 quý
   - A8 Pet peeves (no source / no risk / theory no numbers / off-topic) · A9 Personal-domain cấm tuyệt đối
2. **reviewer-node checklist** → stock 5 axes:
   - (1) Số liệu/Source: P/E EPS NI OCF target cite? tags đúng? peer-benchmark?
   - (2) Format/Unit: đơn vị rõ, tỷ giá, % change > absolute
   - (3) Logic/Thesis: A1 thesis? A2 risk? correlation=causation? FOMO? A5 margin of safety?
   - (4) Consistency/ANCHORS: A4 core→Poly? A2 thiếu risk? A9 personal ban?
   - (5) Completeness: 3 góc (Fundamental/Valuation/Risk), bucket alloc, A7 ≥4 quý
3. **auto-reviewer** → ANCHORS path `C:/Users/khoans/Documents/Stock_OS/stock_vault/00_CORE_LOGIC/ANCHORS.md` (both How-to-call L31 + Pitfalls L87).
4. **safenet** → route L32 bỏ `verify-data-window` (L'Usine) → inline A7 ≥4 quý; description `warren-profile`→`stock-profile`.

## Drift grep (post-adapt) — CLEAN
```
grep -rn "LU3\|LU5\|LU7\|triệu VND\|Saigon Centre\|mall regulation\|vault/00_CORE_LOGIC/ANCHORS.md\|verify-data-window\|warren-profile" stock/skills/...
```
→ only 2 hits = correct stock ANCHORS path lines. Zero L'Usine tokens.

## Battle-test re-run
Target ≥85/100. Structural C1/C2/M3/M4 intact; domain fit (A2/A4/A5/A7) now checkable.

## Lesson
The review-gate STRUCTURE is profile-agnostic; the CHECKLIST + ANCHORS + routed-skills are NOT. Adopt = fork + rewrite those three, never symlink/copy.
