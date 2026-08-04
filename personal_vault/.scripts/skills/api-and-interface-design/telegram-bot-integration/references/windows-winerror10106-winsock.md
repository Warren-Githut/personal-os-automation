# WinError 10106 — Winsock LSP Failure in Subprocess Context (Windows)

## Symptom

Bot crashes immediately on startup with:

```
OSError: [WinError 10106] The requested service provider could not be loaded or initialized

During handling of the above exception, another exception occurred:
  File "C:\...\asyncio\windows_events.py", line 8, in <module>
    import _overlapped
OSError: [WinError 10106] ...
```

## Root Cause

| Layer | Detail |
|-------|--------|
| **OS error** | `WinError 10106` = `WSAEPROVIDERFAILEDINIT` — Winsock LSP DLL failed to load |
| **Python impact** | `_overlapped` (C extension, wraps Windows IOCP) cannot import → `asyncio` fails → bot can't start |
| **Trigger** | Error occurs **only when spawned via subprocess** (`subprocess.Popen`, `cmd.exe`). Direct terminal execution works fine. |

**Not a Python/bot code bug.** Windows Winsock issue limited to subprocess/new-console environments.

## Common Environment

- Company-managed laptops locked down (no admin for `netsh winsock reset`)
- VPN/antivirus installed an LSP filter that corrupted the catalog
- Direct process inherits working Winsock; new process doesn't

## Workaround (No Admin Required)

DO NOT use subprocess, .bat, or cmd.exe. Use Hermes `terminal(background=true)` with Python inline (`-c` NOT `-m`):

### Exact Working Command

```bash
cd /c/Users/khoans/Documents/path/to/scripts/lusine-ops && \
PYTHONPATH="/c/Users/khoans/Documents/path/to/vault/scripts" \
/c/Users/khoans/AppData/Local/Programs/Python/Python312/python.exe -c "
import os, sys
for line in open(r'C:\Users\khoans\AppData\Local\LUsineWorkBot\.env', encoding='utf-8-sig'):
    line = line.strip()
    if line and not line.startswith('#') and '=' in line:
        k, v = line.split('=', 1)
        os.environ[k.strip()] = v.strip()
os.environ['PYTHONPATH'] = r'C:\Users\khoans\Documents\path\to\vault\scripts'
sys.path.insert(0, r'C:\Users\khoans\Documents\path\to\vault\scripts')
from lusine_ops.telegram_bot import main
import asyncio
asyncio.run(main())
"
```

**Key details:**
- Uses `-c` (inline code), NOT `-m lusine_ops.telegram_bot` (which fails via subprocess)
- Env vars loaded inside Python before imports — avoids Winsock corruption from inherited env
- `PYTHONPATH` included inside the inline code as second line, not as shell env var
- Bot runs as child of Hermes terminal process tree, not as orphan subprocess
- Use `terminal(background=true)` — this creates a persistent background shell that keeps the bot alive

### Verification (Avoid WMIC Self-Match)

Wait 15 seconds after launch, then check exactly **one** instance:

```bash
sleep 15
powershell -Command "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { \$_.CommandLine -like '*lusine_ops*' } | Select-Object ProcessId | Format-Table -AutoSize"
```

→ Should show exactly 1 python.exe PID. Multiple instances mean orphan launcher still running.
→ Use PowerShell `Get-CimInstance`, NOT `wmic` (which suffers from self-referential matching on Hermes terminal).

### When to Use This Workaround

| Bot started via... | Works? | Notes |
|---|---|---|
| `terminal(background=true)` with inline `-c` | ✅ Yes | Reliable |
| `.bat` launcher | ❌ Fails | WinError 10106 on startup |
| `subprocess.Popen(['python', '-m', ...])` | ❌ Fails | Same Winsock issue |
| `os.system('start python ...')` | ❌ Fails | New console = new Winsock context |

## Detection

```bash
# Step 1: Test asyncio directly
python -c "import asyncio; print('OK')"
# Step 2: Test via subprocess
python -c "import subprocess,sys; r=subprocess.run([sys.executable,'-c','import asyncio'],capture_output=True); print('OK' if r.returncode==0 else r.stderr[:200])"
# Step 1 OK + Step 2 FAIL = WinError 10106 scenario
```

## Permanent Fix (Admin)

```batch
netsh winsock reset
:: Reboot required
```

## Relationship to WinError 64

| Error | Layer | Transient? | Workaround |
|:--|:--|:--|:--|
| WinError 64 | Network | Yes | TransientNetworkFilter (log noise) |
| WinError 10106 | Winsock | No | Subprocess avoidance |
