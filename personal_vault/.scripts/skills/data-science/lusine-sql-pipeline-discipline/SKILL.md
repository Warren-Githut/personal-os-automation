---
name: lusine-sql-pipeline-discipline
description: "Discipline cho mọi parser/script/cron query IKKO SQL (iikoAPI) trong L'Usine vault — firewall read-only, công thức chuẩn, month constraint, post-build review. Trigger: viết/ sửa SQL parser, revenue pipeline, best-seller query."
version: 1.0.0
author: hermes
trigger: Viết parser SQL IKKO / sửa revenue_sql_parser / query iikoAPI.dbo.Orders / post-build review parser
---

# L'Usine SQL Pipeline Discipline

> Lessons từ session 2026-07-24 (build revenue_sql_parser.py + weekly-revenue-sql). Áp dụng cho MỌI code query IKKO SQL.

## 🔴 HARD RULE 1: SQL Firewall (CRITICAL)

**Mọi parser/script query SQL PHẢI qua `sqlclient.run_query()` — KHÔNG connect thẳng `pyodbc.connect()`.**

- `vault/.scripts/sqlserver_client/sqlclient.py` có firewall `is_readonly()` chặn INSERT/UPDATE/DELETE.
- Connect thẳng pyodbc = **bypass firewall** = violation ANCHORS read-only.
- **Code-review MUST check:** nếu file mở `pyodbc.connect()` trực tiếp → flag CRITICAL, fix = lazy-load `sqlclient` module, gọi `run_query()`.

**Bug thực tế (2026-07-24):** `revenue_sql_parser.py` có `_run_sql()` tự mở pyodbc → review bắt C1. Fix:
```python
_sqlclient = None
def _setup_sql_env():
    global _sqlclient
    if _sqlclient: return _sqlclient
    sys.path.insert(0, str(SQLCLIENT_DIR))
    import sqlclient
    sqlclient.load_env()
    os.environ["MSSQL_DATABASE"] = "iikoAPI"
    _sqlclient = sqlclient
    return sqlclient
def _run_sql(sql):
    return _setup_sql_env().run_query(sql)
```

## 🔢 HARD RULE 2: CÔNG THỨC CHUẨN (dùng MỌI khi query)

- **Net Revenue** = `SUM(AmountWithDiscount) × 0.882` (trừ ~11.8% voucher/system fee)
- **Covers** = `SUM(GuestCount) WHERE OrderType != 'Split Order'` (loại bill chia bàn)
- **Tickets** = `COUNT(*)` (tổng hóa đơn)
- **Store filter:** `DepartmentCode IN ('LSLTT','LU5','LU7') AND OrderDeleted='NOT_DELETED' AND Storned='FALSE'`
- **Khớp OCR PowerBI 99.7%** (verified W29 2026-07-24)

## 🟡 HARD RULE 3: Month Constraint

**Target Achv / monthly budget CHỈ tính tháng 5-12.** File `Budget_vs_Actual.md` CHỈ có cột May-Dec.

- Bug đã fix: `month_idx = m - 5` không guard → tháng 1-4 lấy sai cell (âm index).
- Fix: `if m < 5: return {}` → tháng 1-4 trả `—` (không lỗi, không crash).

## 🧹 HARD RULE 4: Post-Build Review (Warren explicit)

Sau MỌI build feature/parser/script → CHẠY:
1. `code-review-and-quality` (5-axis: correctness, readability, architecture, security, performance)
2. `improve-codebase-architecture` (deep module check, YAGNI)
3. `code-simplification` (dedup, remove dead code)

Warren: *"dùng code review và improve-codebase-architecture và code simplification (sub) từng task/slice"*.

**Verify behavior không đổi sau simplify:** chạy `--dry` so sánh số với bản cũ (W29 reference: ALL=683.7M, Covers=2,590, Target Achv 82/77/87/83%).

## 🔄 HARD RULE 5: Resume Rule (Warren 2026-07-24)

**"tiếp tục nào" / "tiếp tục" sau API retry/interrupt = RESUME trực tiếp.**
- KHÔNG re-explain context, KHÔNG hỏi lại "Bố muốn làm gì?".
- Đọc lại file đích, tiếp tục bước dở dang. Autonomous continuation expected.

## Pitfalls

- **VPN required:** SQL chỉ accessible qua DrayTek TLG VPN (10.28.15.63:9433)
- **`.env` MSSQL_DATABASE=iikoAPI** — file từng trống, gây connect sai DB (master)
- **stdout rebind:** SQL parser import OCR parser → save/restore `sys.stdout` trước/sau import
- **Dry run first:** Always `--dry` trước live run
- **🔴 HARDCODED WEEK TRAP (2026-07-27):** Script regen mà hardcode `WEEKS=[W26,W27,W28,W29]` → cron chạy mỗi tuần → regen y nguyên tuần cũ mãi, KHÔNG lấy W mới → automation vô nghĩa. Phát hiện thực tế: `_regen_all_hourly.py` hardcode W26-W29, HANDOFF ghi "script KHÔNG đổi" nhưng thực tế PHẢI đổi thành dynamic. → **FIX:** tính 4 tuần gần nhất ĐỘNG từ `datetime.date.today()` (xem `cron-job-ops` §12.5 cho code `compute_last_4_weeks`). Test: `compute_last_4_weeks(date(2026,7,27))` → `[W30,W29,W28,W27]`.

## Verification

- [ ] Query qua `sqlclient.run_query()` (không pyodbc trực tiếp)
- [ ] Công thức ×0.882 + filter Split Order
- [ ] Month < 5 → return {} (không crash)
- [ ] Code-review + simplify đã chạy, behavior không đổi
- [ ] VPN + .env checked
