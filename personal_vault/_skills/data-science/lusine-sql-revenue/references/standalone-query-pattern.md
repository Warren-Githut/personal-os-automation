# Standalone ad-hoc SQL query (temp script pattern)

When Bố asks a one-off SQL question and you need to run a quick query outside the pipeline/cron:

```python
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "sqlserver_client"))
import sqlclient
sqlclient.load_env()  # 🔴 MANDATORY before run_query — see Gotchas

NET = 0.882
cols, rows = sqlclient.run_query(
    "SELECT DepartmentCode, SUM(AmountWithDiscount) gross, COUNT(*) tickets "
    "FROM dbo.Orders WHERE ShiftDate BETWEEN '2026-07-20' AND '2026-07-26' "
    "AND DepartmentCode IN ('LSLTT','LU5','LU7') AND OrderDeleted='NOT_DELETED' AND Storned='FALSE' "
    "GROUP BY DepartmentCode")
for r in rows:
    print(r[0], float(r[1]) * NET, int(r[2]))
```

## Gotchas
- **Forgetting `sqlclient.load_env()`** → connection string builds with `SERVER=None` → `OperationalError 08001 [Microsoft][ODBC SQL Server Driver]SQL Server does not exist or access denied`. The `.env` is loaded lazily ONLY inside `main()`; importing the module does NOT auto-load it. Call `load_env()` explicitly after import.
- **MSYS path double-prefix**: when invoking Windows-native `python3` on a path, pass `C:/Users/khoans/...` (native forward-slash), NOT `/c/Users/khoans/...`. The latter gets re-converted by MSYS into `C:\c\Users\khoans\...` (double prefix) → `FileNotFoundError`. Symptom: `can't open file 'C:\\c\\Users\\...'`.
- **Write temp script INTO `vault/.scripts/`** (dotfolder, local), run it, then `rm` it — do NOT leave temp files in the SSOT dotfolder.
- **VPN required**: host `10.28.15.63` is LAN-only behind DrayTek TLG VPN. Pre-check: `ping -n 2 10.28.15.63` (reply = VPN up). No reply → start VPN, do not fall back to OCR.
- **Firewall**: `sqlclient.run_query` only allows SELECT/WITH (defense-in-depth). Never bypass with raw `pyodbc.connect`.
