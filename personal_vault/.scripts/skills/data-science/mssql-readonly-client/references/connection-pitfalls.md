# Connection Pitfalls — error transcripts + fixes

## 1. Dual interpreter (Windows, Warren's machine)
Symptom: `pip install pyodbc` succeeds but `python3 -c "import pyodbc"` → ModuleNotFoundError.
Cause: `python3`=3.14 (WindowsAppStore), bare `pip`=3.12 Hermes venv.
Fix: `python3 -m pip install pyodbc`. Verify: `python3 -c "import pyodbc; print(pyodbc.__version__)"`.

## 2. Legacy driver + Encrypt attribute
Symptom:
```
pyodbc.OperationalError: ('08001', '[08001] ...Invalid connection string attribute (0)')
```
Cause: driver name `SQL Server` (legacy, ships with Windows) does NOT accept `Encrypt=`/`TrustServerCertificate=`.
Fix: only append those attrs when driver name contains `ODBC DRIVER`:
```python
if "ODBC DRIVER" in drv.upper():
    cs += f"Encrypt={enc};TrustServerCertificate={tc};"
```

## 3. Port closed / server unreachable
Symptom:
```
[08001] SQL Server does not exist or access denied (17)
ConnectionOpen (Connect()). (53)
[WinError 10061] No connection could be made because the target machine actively refused it
```
Check order:
1. `python3 -c "import socket;s=socket.socket();s.settimeout(3); s.connect(('HOST',PORT)); print('OPEN')"` → refused = server down / wrong host / firewall.
2. Is SQL Server installed on that host? `sc query`, Program Files, registry, Docker — all empty = not installed.
3. **127.0.0.1 = THIS machine.** "Runs locally" from a non-IT user often means "locally at the store", NOT "on my laptop". Need the store/server LAN IP (192.168.x.x / 10.x.x.x), not 127.0.0.1.
4. Remote login may be restricted to local connections — ask IT to whitelist the analyst machine IP or issue a separate remote login.

## 4. Read-only login still needs code firewall
Even with a SELECT-only SQL login, enforce `is_readonly()` in code: blocks pasted DROP/UPDATE and stacked `SELECT 1; DROP TABLE x`. Defense-in-depth.

## 5. VPN required for store LAN access (different subnet)
**Symptom:** server IP correct but `connect()` times out — `[WinError 10060]` host unreachable.
**Cause:** analyst machine on DIFFERENT subnet (home/office `192.168.x.x`) than store LAN (`10.28.15.x`).
**Check:** `ipconfig` → if IP NOT in `10.28.15.x` range, VPN needed.
**Fix:** DrayTek Smart VPN Client → profile `TLG VPN` → Connect. Verify `ipconfig` shows `10.28.15.x` → port `10.28.15.63:9433` reachable.
**Pitfall:** VPN silently disconnects after idle. Re-check port before each query batch.
