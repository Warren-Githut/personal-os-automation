---
name: warren-sql-parser-build
description: "Use to build IKKO SQL vault parsers via read-only sqlclient."
version: 1.0.0
author: Hermes
category: data-science
tags: [parser, sql, ikko, lusine, tdd, vault, build]
related_skills: [lusine-sql-pipeline-discipline, verify-parser-output, reviewer-node, incremental-implementation, test-driven-development, ikko-sql-firewall-patterns, lusine-sql-revenue, lusine-sql-scripting, sqlserver-ikkopos-client]
---

# Warren SQL Parser Build (class-level)

Recurring class of work: Warren vault parsers that hit IKKO SQL directly.
Instances: `revenue_sql_parser.py` (weekly), `lto_sql_parser.py` (promo windows),
`hourly_cover_sql_parser.py` v6.0 (hourly covers/rev). This skill carries the
**canonical build skeleton + TDD harness** so each new build reuses, not re-derives.
Discipline rules live in `lusine-sql-pipeline-discipline` — this skill is the
concrete *how to scaffold + test* complement.

## When to use
- Bố duyệt thay thế 1 nguồn GSheet/OCR bằng IKKO SQL query.
- Build mới 1 parser đọc `dbo.Orders` (covers/net/rev) cho vault SSOT.
- Reuse pattern khi mở rộng query (theo store / day / hour / daypart).

## Hard rules (from ANCHORS / WARREN_MEMORY — non-negotiable, KHÔNG tự sửa)
- QUA `sqlclient.run_query()` (read-only firewall). **KHÔNG** pyodbc thẳng (bypass firewall).
- `NET_FACTOR = 0.882` áp dụng ĐÚNG 1 LẦN (tại query agg: `SUM(AmountWithDiscount)*0.882`).
  Double = bug class P1 (baseline lệch 0.882×).
- Covers = `SUM(GuestCount) WHERE OrderType != 'Split Order'`.
- Revenue format = `M` (1 decimal) CHỈ ở display; internal = VND. **Fixture net = VND**,
  `/1e6` lúc show (P2 trap: green unit với net ĐÃ M sẽ che 2 bug).
- Dotfolder: parser ở `vault/10_OPERATION_DATA/.parsers/`; import `sqlclient` từ
  `VAULT/.scripts/sqlserver_client`. `search_files` BLIND dotfolder → dùng `terminal ls`.
- Verify gate (`verify-parser-output`) + `reviewer-node` BẮT BUỔC trước báo xong.

## Build sequence (slice-by-slice + TDD) — proven 2026-07-26 (hourly_cover_sql_parser v6.0)
1. **RED trước**: viết harness test TRƯỚC code. pytest absent trên py3.14 → dùng
   `scripts/tdd_harness.py` (minimal: collect `test_*` + assert + GREEN/RED print).
   ⚠️ Không `exec(open(__file__).read().split(...))` — self-exec raises SyntaxError.
2. **GREEN helpers (P1/T1-T3)**: implement pure functions (`classify_daypart`, `rollup_daypart`,
   `rollup_weekly`, `mtd_day_based`, `peak_flag`) + `query_X()` GROUP BY → test pass.
3. **GREEN block (P2/T4-T5)**: `build_block_v6()` N sections (reuse v5.0 template) + peak-flag +
   MTD-day + straddle badge.
4. **GREEN cross-check/write (P3/T6-T7)**: `cross_check_ssot()` INDEPENDENT parse `01_SSOT`
   (A9), threshold **2%** (hourly per handoff D6 — NOT 5%) + internal `verify_gate` (hourly Σ ==
   weekly) + `write_log_atomic` newest-on-top + `refresh_dashboard` (`.replace()` JS, `node --check`).
5. **Sweep (P4/T9)**: grep+patch stale 5%→2% cross-source across skills/memory/ANCHORS.
6. **E2E gate**: `--dry` W29 thực tế (VPN Bố mở, qua `sqlclient.run_query`) TRƯỚC ghi thật.
   Bố duyệt `--apply` (zone 🟡). GREEN unit ≠ live correct → LUÔN E2E dry trước.
7. **Verify + reviewer**: `verify-parser_output` gate + `reviewer-node` (fresh context).

> Independent SSOT cross-check recipe (parse + 2% threshold + exact-label match):
> `references/ssot_crosscheck.md`.

## Canonical skeleton (abbreviated)
```python
HERE = Path(__file__).resolve().parent
VAULT = HERE.parents[1]                       # .parsers -> 10_OPERATION_DATA -> vault
SQLCLIENT_DIR = VAULT / ".scripts" / "sqlserver_client"
NET_FACTOR = 0.882
STORE_MAP = {"LSLTT": "LU3", "LU5": "LU5", "LU7": "LU7"}

def _setup_sql_env():
    sys.path.insert(0, str(SQLCLIENT_DIR))
    import sqlclient
    sqlclient.load_env()
    os.environ["MSSQL_DATABASE"] = "iikoAPI"
    return sqlclient

def _run_sql(sql): return _setup_sql_env().run_query(sql)

def query_hourly(start, end):
    sql = f"""SELECT DepartmentCode,
              DATEPART(WEEKDAY, OpenTime) as dow, DATEPART(HOUR, OpenTime) as hr,
              SUM(CASE WHEN OrderType!='Split Order' THEN GuestCount ELSE 0 END) as covers,
              SUM(AmountWithDiscount) as gross_rev
            FROM dbo.Orders
            WHERE ShiftDate>='{start}' AND ShiftDate<='{end}'
              AND DepartmentCode IN ('LSLTT','LU5','LU7')
              AND OrderDeleted='NOT_DELETED' AND Storned='FALSE'
            GROUP BY DepartmentCode, DATEPART(WEEKDAY, OpenTime), DATEPART(HOUR, OpenTime)"""
    cols, rows = _run_sql(sql)
    dow_to_day = {1:"sun",2:"mon",3:"tue",4:"wed",5:"thu",6:"fri",7:"sat"}  # SQL: 1=Sun..7=Sat
    # ... remap, net = gross*NET_FACTOR ONCE, drop hr<7 or hr>21
```
Full hourly GROUP BY + weekday remap: `references/ikko_hourly_query.md`.

## TDD harness (no pytest)
`scripts/tdd_harness.py` — copy, rename tests, run `python scripts/tdd_harness.py`.
Collects `test_*` globals, runs each, prints `GREEN/RED`, exits 1 on fail.
Use this instead of `pytest` (absent on warren-profile py3.14 numpy ABI).

## Pitfalls (Warren env — caught & fixed building hourly_cover_sql_parser v6.0)
- **pytest absent** → harness script, not `pytest -v`.
- **Green unit ≠ live**: LUÔN `--dry` W29 E2E trước ghi thật (P2 fixture trap).
- **Channel split**: Bố quyết gộp (hourly_cover v6) — confirm trước làm split theo channel.
- **Weekday remap**: SQL `DATEPART(WEEKDAY)` = 1=Sun..7=Sat, KHÔNG phải Mon-first →
  phải map sang DAY_ORDER Mon-first, nếu không lệch 1 ngày toàn bộ.
- **SSOT label-substring false match**: parse `01_SSOT` `| Covers |` bằng `startswith("Covers")`
  cũng match `| Covers W/W% |` → đọc sai value (W30 trả covers=2 thay 2583). FIX: exact
  `cells[0] == "Covers"` (sau strip). Áp dụng mọi parse bảng SSOT — match exact label, không prefix.
- **Fixture key-type mirror**: production `query_hourly()` key giờ là STRING `"12"`; fixture dùng
  int `12` → bảng hourly render RỖNG (không lỗi, silent). FIX: fixture MUST mirror production key
  types (string hour). Thêm test assert cell rendered chứa data thật.
- **Internal verify_gate là defense-in-depth**: per-store Σ hourly[hr][day] MUST == `rollup_weekly()`
  trong tol → bắt SQL GROUP BY / hour-map bug trước write. KHÔNG optional.
- **Cross-source threshold**: hourly cross-check vs `01_SSOT` = **2%** (handoff D6), KHÔNG 5%
  (5% là threshold chung cũ; weekly pipeline internal verify giữ 0.3%/0.5%). Parse SSOT ĐỘC LẬP (A9),
  phân biệt "SSOT thiếu (DATA GAP)" vs "SSOT có lệch >2% (mismatch 🔴)".
- **Peak-hour share <15% 🔴**: flag báo khi KHÔNG có giờ nào chiếm ≥15% net — verify là data thật
  (W29 peak 4% là thực) không phải logic bug trước khi report.

## References
- `references/ikko_hourly_query.md` — hourly GROUP BY SQL + weekday remap detail
- `scripts/tdd_harness.py` — reusable minimal TDD harness (copy + rename)
