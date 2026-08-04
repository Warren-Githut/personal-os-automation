---
name: lusine-sql-scripting
description: "Safe patterns for writing vault Python scripts that query IKKO SQL (iikoAPI). Covers the read-only firewall rule, env loading, store mapping, and budget month guard. Use when building/refactoring any L'Usine SQL parser/script (revenue, best-seller, labour, etc)."
version: 1.0.0
trigger: Viết script Python query IKKO SQL / dùng sqlclient / gặp lỗi pyodbc / cần firewall read-only / tháng 1-4 target trả rỗng.
category: data-science
tags: [sql, ikko, firewall, sqlserver, lusine, scripting]
related_skills: [sqlserver-ikkopos-client, verify-parser-output, weekly-revenue-sql, ikko-sql-firewall-patterns, lusine-sql-revenue, warren-sql-parser-build]
created: 2026-07-24
---

# L'Usine SQL Scripting — Safe Patterns

> Durable lessons từ session 2026-07-24 (xây `revenue_sql_parser.py`). Áp dụng cho MỌI script vault query IKKO SQL.

## 🚨 HARD RULE 1 — Dùng `sqlclient.run_query()`, KHÔNG raw pyodbc

Mọi query PHẢI qua `sqlclient.run_query()` — nó có firewall `is_readonly()` chặn INSERT/UPDATE/DELETE/MULTI-STATEMENT.

```python
# ĐÚNG
import sys
from pathlib import Path
SQLCLIENT_DIR = Path(__file__).resolve().parents[N] / ".scripts" / "sqlserver_client"
sys.path.insert(0, str(SQLCLIENT_DIR))
import sqlclient
sqlclient.load_env()
os.environ["MSSQL_DATABASE"] = "iikoAPI"

def _run_sql(sql: str):
    return sqlclient.run_query(sql)   # firewall enforced
```

```python
# SAI — bypass firewall, CRITICAL security finding khi review
import pyodbc
cs = f"DRIVER={{SQL Server}};SERVER=...;DATABASE=...;UID=...;PWD=..."
conn = pyodbc.connect(cs); cur = conn.cursor(); cur.execute(sql)
```

**Pitfall thực tế:** `revenue_sql_parser.py` v1 viết raw pyodbc → code-review bắt sửa lại `run_query()`. Luôn reuse tool.

## HARD RULE 2 — Env + DB phải đúng

- Gọi `sqlclient.load_env()` trước `run_query` (đọc `.env` cùng thư mục).
- Set `os.environ["MSSQL_DATABASE"] = "iikoAPI"` — không có thì connect `master` (không có `dbo.Orders`).
- VPN DrayTek TLG bắt buộc (`10.28.15.63:9433`).

## HARD RULE 3 — Store mapping

`LSLTT` = LU3, `LU5` = LU5, `LU7` = LU7. Dùng `STORE_MAP = {"LSLTT":"LU3",...}` khi parse kết quả. KHÔNG query bằng `LU3`.

## HARD RULE 4 — Budget month guard

`Budget_vs_Actual.md` chỉ có May–Dec (m=5..12). Khi parse target:
```python
if m < 5:
    return {}   # tháng 1-4 không có target, đừng lấy sai cell
month_idx = m - 5   # May=0 ... Dec=7
```
Không bỏ guard này.

## HARD RULE 5 — stdout rebind khi import OCR parser

Nếu script import hàm từ `revenue_screenshot_parser.py` (nó rebind `sys.stdout` ở module level):
```python
_orig = sys.stdout
from revenue_screenshot_parser import build_payload, verify_gate, ...
sys.stdout = _orig   # restore ngay sau import
```
Và in dry-run ra `sys.stderr.write(...)`, không `print(...)` (vì stdout bị wrapper).

## Review discipline (Warren 2026-07-24)

Sau mọi build script → chạy `code-review-and-quality` + `improve-codebase-architecture` + `code-simplification` (incremental-implementation). Checklist hay quên:
- [ ] Dead imports/constants/vars (grep `import` + `pass$`)
- [ ] Lặp code → extract helper
- [ ] Firewall bypass (grep `pyodbc.connect`)
- [ ] Hardcode month index không guard

## Verification

Sau sửa script:
```bash
grep -n "pyodbc.connect" your_script.py   # phải = 0 kết quả
python3 your_script.py --dry 2>&1 | grep -E "verify|Net Revenue"
# so sánh output với bản reference (W29: 82/77/87/83% target achv)
```

## 🔴 IKKO `run_query` quirks thực chiến (2026-07-27, COL W30 SQL fix)

### Q1 — QUÊN `load_env()` → lỗi `(53) SQL Server does not exist`
`run_query` đọc cred từ `os.environ` (MSSQL_SERVER/MSSQL_PASSWORD/MSSQL_DATABASE). Nếu KHÔNG gọi `sqlclient.load_env()` đầu script → env rỗng → conn_string `SERVER=None` → lỗi `(53) SQL Server does not exist or access denied`. **Trông giống lỗi VPN NHƯNG KHÔNG PHẢI** (socket test B1 vẫn OK). FIX: luôn `import sqlclient; sqlclient.load_env()` trước mọi query. Driver `SQL Server` cũ tự bỏ qua `Encrypt=` (chỉ thêm khi driver = `ODBC Driver 1x/17/18`).

### Q2 — Return shape: header + data row
`run_query(sql)` trả list: `row[0]` = header `['DepartmentCode','gross',...]`, `row[1]` = data tuple. Bỏ qua `row[0]`. Scalar query: `d = sqlclient.run_query(sql)[1][0]` rồi `float(d[0])`.

### Q3 — GROUP BY nhiều store COLLAPSE thành tuple (NGUY HIỂM)
`SELECT DepartmentCode, SUM(...) ... GROUP BY DepartmentCode` → `run_query` trả `row[1][0]` = `(('LSLTT','LU5','LU7'), (gross_l,gross_5,gross_7), ...)` — mỗi cột là tuple của 3 store, KHÔNG phải 1 row/store. Parse sai → `TypeError: float not subscriptable`. **FIX (chuẩn): query TỪNG store riêng**, rồi cộng dồn:
```python
STORES=[('LSLTT','LU3'),('LU5','LU5'),('LU7','LU7')]
for code,name in STORES:
    sql=f"""SELECT SUM(AmountWithDiscount) gross,
      SUM(CASE WHEN OrderType<>'Split Order' THEN GuestCount ELSE 0 END) covers,
      COUNT(*) tickets FROM dbo.Orders
      WHERE ShiftDate>='{start}' AND ShiftDate<='{end}'
        AND DepartmentCode='{code}' AND OrderDeleted='NOT_DELETED' AND Storned='FALSE'"""
    d=sqlclient.run_query(sql)[1][0]
    net=float(d[0])*0.882   # NET_REVENUE chuẩn
    cov=int(float(d[1])); tk=int(float(d[2]))
```
SUM-CHECK: tổng 3 store net phải = sys net (diff <100 VND). Lệch lớn = sai query.

### Q4 — Windows path
Chạy script: absolute Windows path (`C:/Users/...`), KHÔNG `C:/c/Users/...` (MSYS double-prefix lỗi). VPN = DrayTek TLG (IP 10.28.15.x), port 9433.
