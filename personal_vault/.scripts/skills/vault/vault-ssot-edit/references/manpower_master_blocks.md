# Manpower_Master.md — Block Layout & Cascade Map

File: `30_KNOWLEDGE_BASE/wiki/04_labour_costs/Manpower_Master.md`
SSOT headcount L'Usine (3 LU + Office). Chuẩn: 2026-07-09.

## Blocks
- **Block 0 — Metadata**: ghi context tạm / proposal / allocation (vd manager T7/2026).
  KHÔNG tạo file mới, ghi vào đây.
- **Block 1 — PLAN (target định biên)**:
  | Store | FOH | Bar | BOH | Cleaner | Office | Total | Scope |
  Sys row = tổng. Final: LU3 25 / LU5 19 / LU7 21 / Office 3 / Sys 68.
- **Block 2 — ACTUAL STOCK** (sync payroll, newest on top):
  | Store | HC | Active | Total Cost (M) | Avg Cost/Head (M) |
  Monthly snapshots Jan–May 2026. May = latest (Sys 63 HC / 56 Active).
- **Block 3 — GAP + VACANCY** (sync HR log):
  | Store | Plan | Active | Gap | Top Vacancy | Days Open | Flag |
  Gap = Plan − Active. **Plan column ở đây là riêng biệt** — phải khớp Block 1.
- **Exec Summary**: top-line bullet "thiếu N active" phải = Block 3 Sys Gap.

## Cascade map (khi bump 1 store plan)
Block 1 (store row + Sys Total) → Block 3 (store Plan cell + Sys Gap + Flag)
→ Exec Summary bullet → (nếu rename) repoint cross-linked wiki files.

## Known trap (09/07 session)
Bump LU5 18→19: sửa Block 1 (LU5 Total 18→19, Sys 67→68, Scope plan 68)
+ Exec Summary (-11→-12) NHƯNG quên Block 3 ô `| LU5 | 18 | 16 | -2 |`
→ Block 3 stale, Sys gap -12 ≠ sum store (-11). Fix: Block 3 LU5 Plan 18→19, Gap -2→-3.

## Cross-linked files (repoint khi rename file)
Manpower_Plan_Analysis_Tracking.md → Manpower_Master.md (đã rename 07/07).
Active files repointed 09/07: HR_Movements, Shift_Rostering, Extra_Hours, OIL_Tracking,
Service_Charge_Policy, OPS_Incentive, Google_Reviews, build_oil_t1.py, case lu5-duy.
Archive/log/cache (WIKI_GRAPH.json, FRONTMATTER_CACHE.json, 10_archive/) giữ tên cũ — read-only.
