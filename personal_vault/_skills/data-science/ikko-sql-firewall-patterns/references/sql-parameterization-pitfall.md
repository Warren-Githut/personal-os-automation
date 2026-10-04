# SQL Parameterization Pitfall (IKKO sqlclient) — 2026-07-25

`sqlserver_client/sqlclient.py` firewall `is_readonly()` blocks INSERT/UPDATE/DELETE/...
BUT does NOT block `UNION` or `--` comment. So f-stringing any value into the SQL
string is a real (if low-exploit) injection gap.

## Fix
`run_query(sql, params=())` was patched to forward `params` to `cur.execute(sql, params)`.
Always use `?` placeholders for parsed input (date from dump header, DepartmentCode):

```python
sql = ("SELECT SUM(AmountWithDiscount) revenue FROM dbo.Orders "
       "WHERE ShiftDate=? AND DepartmentCode IN {codes} "
       "AND OrderDeleted='NOT_DELETED' AND Storned='FALSE'")
cols, rows = sqlclient.run_query(sql, (sql_date,))
```

- `IN (...)` with a CONSTANT allowlist (`'LSLTT','LU5','LU7'`) is safe to interpolate.
- Only DYNAMIC input needs `?`. Date is regex-locked by parse_brain_dump; dept comes
  from the allowlist — so gap is theoretical, but parameterize anyway (defense in depth).

## Verification
- grep the new query for `ShiftDate='{` (f-string) → must be absent.
- Confirm `run_query` signature now accepts `params`.
