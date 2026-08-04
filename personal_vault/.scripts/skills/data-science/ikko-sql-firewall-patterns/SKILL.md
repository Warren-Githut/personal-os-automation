---
name: ikko-sql-firewall-patterns
description: "Hard rule + patterns khi viết script query IKKO SQL (iikoAPI) — LUÔN qua sqlclient.run_query() (firewall read-only), KHÔNG connect thẳng pyodbc. Pitfalls: .env MSSQL_DATABASE trống, stdout rebind, Target May-Dec constraint. Dùng khi build/refactor bất kỳ parser/script query IKKO SQL."
version: 1.0.0
category: data-science
tags: [sql, ikko, firewall, pyodbc, sqlserver, patterns]
related_skills: [sqlserver-ikkopos-client, weekly-revenue-sql, lusine-sql-revenue, lusine-sql-scripting, warren-sql-parser-build]
created: 2026-07-24
---

# IKKO SQL Firewall & Integration Patterns

> Bài học từ code review `revenue_sql_parser.py` (2026-07-24, C1 CRITICAL).
> Áp dụng cho MỌI script query IKKO SQL trong vault.

## 🔴 HARD RULE — LUÔN qua `sqlclient.run_query()`

`vault/.scripts/sqlserver_client/sqlclient.py` có firewall `is_readonly()`
chặn mọi INSERT/UPDATE/DELETE/MERGE/DROP/ALTER/CREATE/TRUNCATE/GRANT/REVOKE/EXEC/...

**KHÔNG** connect thẳng `pyodbc.connect()` — bypass firewall = rủi ro ghi IKKO.

### ❌ SAI
```python
import pyodbc
cs = f"DRIVER={{SQL Server}};SERVER={srv};DATABASE={db};UID={uid};PWD={pwd};"
conn = pyodbc.connect(cs); cur = conn.cursor(); cur.execute(sql)
```

### ✅ ĐÚNG
```python
sys.path.insert(0, str(SQLCLIENT_DIR))
import sqlclient
sqlclient.load_env()
os.environ["MSSQL_DATABASE"] = "iikoAPI"   # force, không依赖 .env
cols, rows = sqlclient.run_query(sql)      # firewall check ở đây
```

## Lazy-load pattern (tránh re-import)
```python
_sqlclient = None
def _setup_sql_env():
    global _sqlclient
    if _sqlclient is not None:
        return _sqlclient
    sys.path.insert(0, str(SQLCLIENT_DIR))
    import sqlclient
    sqlclient.load_env()
    os.environ["MSSQL_DATABASE"] = "iikoAPI"
    _sqlclient = sqlclient
    return sqlclient
```

## Pitfalls (đã gặp & fix 2026-07-24)

| # | Pitfall | Fix |
|---|---------|-----|
| P1 | `.env` `MSSQL_DATABASE=` trống → `load_env()` dùng `setdefault` không ghi đè → default `master` → sai DB (không có `dbo.Orders`) | Sửa `.env` thành `iikoAPI` HOẶC force `os.environ["MSSQL_DATABASE"]="iikoAPI"` sau load_env |
| P2 | Parser import OCR parser có `sys.stdout = io.TextIOWrapper(...)` ở module level → chiếm stdout script gọi | Save `_orig=sys.stdout` trước import, restore ngay sau; hoặc ghi dry-run vào `sys.stderr` |
| P3 | Target Achv parse: `month_idx = m-5` không guard → tháng 1-4 lấy sai cell (budget chỉ có May-Dec) | `if m < 5: return {}` |
| P4 | Target regex non-greedy `\|(.*?)\|` chỉ bắt 1 cell | Dùng greedy `\|(.*)` bắt hết đến cuối dòng |
| P5 | Dead imports (`importlib.util`, `defaultdict`) / dead const (`DB_STORES`) | Chạy grep trước commit |

## Verify sau mỗi fix
- [ ] Script vẫn qua `sqlclient.run_query()` (grep không có `pyodbc.connect`)
- [ ] `--dry` chạy ra số khớp OCR 99.x%
- [ ] Target Achv đúng cho tháng 5-12, `—` cho 1-4
