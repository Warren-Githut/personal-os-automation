---
name: mssql-readonly-client
description: "Build a safe SQL Server (MSSQL) read-only Python client for ad-hoc data analysis — connect via pyodbc, enforce a code-level read-only firewall (defense-in-depth even on read-only logins), handle legacy-driver connection-string quirks, debug connection failures, and clarify localhost-vs-remote confusion for non-IT users. Use when a user wants to query a SQL Server directly instead of via Power BI / a BI tool, or says 'read-only login', 'Power BI source DB', 'liệt kê schema', 'data analyst on SQL Server'."
version: 1.1.0
author: Hermes
updated: 2026-07-24 — Bố confirmed store mapping; Cost column discovered (Dishes.Cost → GP% direct); GP% analysis patterns added.
trigger: "user wants to connect to / query a SQL Server, 'read-only login', 'Power BI source DB', 'liệt kê schema', 'data analyst on SQL Server', 'GP%', 'best seller + cost'"
category: data-science
tags: ['sql-server', 'mssql', 'pyodbc', 'read-only', 'data-analysis', 'safe-client']
related_skills: ['verify-parser-output', 'interview-me']
---

# mssql-readonly-client — Safe SQL Server Read-Only Client

> Build a Python client that connects to SQL Server and ONLY runs SELECT/WITH. Even if the login is already read-only, the code-level firewall protects the user from pasting a destructive query by accident and from stacked-statement injection.

## When to use
- User has a SQL Server login (often the same one Power BI uses) and wants to query data directly.
- Non-IT user wants to ask "how much did we sell yesterday" without opening Power BI.
- You need to list schemas / tables / views and run analysis (sales, inventory, period comparison).

## Prereqs
1. Install pyodbc into the SAME interpreter you run the script with:
   `python3 -m pip install pyodbc`  ← use `python3 -m pip`, NOT bare `pip` (see Pitfalls: dual-interpreter).
2. Check drivers: `python3 -c "import pyodbc; print([d for d in pyodbc.drivers()])"`.
   - Modern: `ODBC Driver 17 for SQL Server`, `ODBC Driver 18 for SQL Server`.
   - Legacy: `SQL Server` (ships with Windows, limited — see Pitfalls).

## The client pattern (see scripts/sqlclient.py)
- Credentials from a `.env` file beside the script (gitignored — never hardcode, never paste into chat).
- `is_readonly(sql)`: allow only statements starting with `SELECT` or `WITH`; block any containing INSERT/UPDATE/DELETE/DROP/ALTER/CREATE/TRUNCATE/MERGE/GRANT/REVOKE/EXEC/EXECUTE/BEGIN/COMMIT/ROLLBACK/USE/SET/RESTORE/BULK; block multi-statement (`;`).
- `conn_string()`: build from env; only append `Encrypt=`/`TrustServerCertificate=` when driver name contains `ODBC DRIVER` (legacy driver rejects them).
- Subcommands: `list-db`, `list-tables <db>`, `schema <db> <table>`, `query "<sql>"`.

## Credential handling
- `.env`: `MSSQL_SERVER`, `MSSQL_DATABASE`, `MSSQL_USER`, `MSSQL_PASSWORD`, `MSSQL_DRIVER`, `MSSQL_ENCRYPT`, `MSSQL_TRUST_CERT`.
- Keep `.env` in `.gitignore`. Provide `templates/.env.example` so the user fills their own.
- NEVER print the password back into chat.

## Connection debugging (do this BEFORE blaming credentials)
Many "login failed" errors are actually "server unreachable". Check in order:
1. Port reachable? `python3 -c "import socket;s=socket.socket();s.settimeout(3); s.connect(('HOST',PORT)); print('OPEN')"` — if refused → server down / wrong IP / firewall.
2. Is SQL Server even installed on that host? Check services (`sc query`), Program Files, registry, Docker.
3. **localhost vs remote**: `127.0.0.1` means *this machine*. If the DB is on a store/server machine, you need that machine's LAN IP (e.g. `192.168.x.x`), NOT 127.0.0.1. Non-IT users often say "it runs locally" meaning "locally at the store", not "locally on my laptop" — clarify (see Interview below).
4. Remote login may be restricted to local connections only → ask IT to whitelist the analyst machine's IP or issue a separate remote login.

## Interview non-IT users (clarify what only they/IT know)
Ask one at a time (see `interview-me`):
- Goal: ad-hoc single numbers? automated period-comparison reports? realtime view? or just a "bridge" for any future question?
- Connection details — they may only have user/pass, not server/db (hidden in Power BI). Give them a copy-paste message to send IT requesting server IP, port, database name, and whether remote login is allowed.
- Where the tool runs — agent runs it from chat (best for non-IT) vs user runs a script themselves.

## Pitfalls
- **Dual interpreter (Windows)**: `python3` is 3.14 (WindowsAppStore path), `pip` targets the 3.12 Hermes venv. `pip install pyodbc` → ModuleNotFoundError under `python3`. FIX: `python3 -m pip install pyodbc`. (Also patched into `pip-install-governance`.)
- **Legacy driver + Encrypt attribute**: driver `SQL Server` does NOT accept `Encrypt=`/`TrustServerCertificate=` → `Invalid connection string attribute`. FIX: only add those attrs when driver name contains `ODBC DRIVER`.
- **127.0.0.1 confusion**: user says "runs locally" → verify whether they mean this machine or the store/server machine. Port-closed error almost always means wrong host or server not running.
- **Read-only login ≠ safe from accidents**: still enforce the code firewall; a pasted DROP or stacked statement is a real risk.
- **Remote login restriction**: a login that works from the store machine may be rejected from the analyst's laptop even with correct IP/port. Confirm with IT.

## References
- `references/connection-pitfalls.md` — detailed error transcripts + fixes.
- `references/lusine-iikoapi-schema.md` — L'Usine IKKO POS schema, store mapping, analysis patterns.
- `scripts/sqlclient.py` — ready-to-use read-only client.
- `templates/.env.example` — credential template.
