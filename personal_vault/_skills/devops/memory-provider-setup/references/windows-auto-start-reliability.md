# Windows Auto-Start Reliability — Ollama + Hermes Gateway

> **Problem:** On Windows boot, Hermes Gateway starts before Ollama is ready. The mem0 plugin initializes, can't reach Ollama, caches a permanent "not initialized" error. Even if Ollama starts later, mem0 stays broken until gateway restarts.

## Root Cause

Startup folder items run in parallel — no guaranteed order:

```
Boot → Startup folder fires:
  ├── Hermes_Gateway.cmd     (starts pythonw.exe → mem0 plugin init → Ollama DOWN → PERMANENT ERROR)
  └── Ollama_AutoStart.bat   (starts ollama serve — but TOO LATE)
```

The mem0 plugin initializes ONCE at session start and never retries. A `/new` session doesn't help — the gateway process itself must restart.

## Fix (Two-Part)

### Part 1: Ollama Auto-Start via Startup Folder

Create `Ollama_AutoStart.bat` in `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\`:

```batch
@echo off
rem Auto-start Ollama tray app (keeps ollama serve running)
start "" "C:\Users\khoans\AppData\Local\Programs\Ollama\ollama app.exe"
```

The `ollama app.exe` is the system tray app. It manages the `ollama serve` process — keeps it alive, survives crashes better than bare `ollama.exe serve`.

### Part 2: Hermes Gateway Wait-for-Ollama Loop

Modify `Hermes_Gateway.cmd` to poll for Ollama before launching:

```batch
@echo off
rem Hermes Agent Gateway - Messaging Platform Integration

rem === Wait for Ollama to be ready before starting Hermes ===
echo Waiting for Ollama server...
:wait_ollama
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    timeout /t 5 >nul
    goto wait_ollama
)
echo Ollama is ready. Starting Hermes Gateway...

rem === Start Hermes Gateway ===
cd /d C:\Users\khoans\AppData\Local\hermes
set "HERMES_HOME=C:\Users\khoans\AppData\Local\hermes"
set "PYTHONIOENCODING=utf-8"
set "HERMES_GATEWAY_DETACHED=1"
set "VIRTUAL_ENV=C:\Users\khoans\AppData\Local\hermes\hermes-agent\venv"
C:\Users\khoans\AppData\Local\hermes\hermes-agent\venv\Scripts\pythonw.exe -m hermes_cli.main gateway run
exit /b 0
```

## Manual Restart (when mem0 breaks mid-session)

**Desktop shortcut** (`Restart_Hermes_Gateway.bat` on Desktop):

```batch
@echo off
echo Dang restart Hermes Gateway...
taskkill /F /IM pythonw.exe >nul 2>&1
timeout /t 3 >nul
start "" /min cmd.exe /d /c "C:\Users\khoans\AppData\Local\hermes\gateway-service\Hermes_Gateway.cmd"
echo Xong! Gateway da duoc restart.
timeout /t 2 >nul
```

**Important:** After restart, current Hermes session's mem0 stays broken. Open `/new` session for mem0 to work.

## MSYS/git-bash Path Mangling Pitfall

When running Windows commands from git-bash (Hermes `terminal` tool on Windows), MSYS auto-converts paths:

| Command | What you type | What MSYS sends | Result |
|---------|--------------|-----------------|--------|
| `taskkill /F /PID 123` | `/F` | `F:/` | ❌ "Invalid argument/option - 'F:/'" |
| `cmd.exe /c ...` | `/c` | `C:/` | ❌ Path mangled |
| `cmd.exe //c ...` | `//c` | `/c` | ✅ Works for simple commands |
| `powershell.exe -Command "..."` | n/a | n/a | ✅ **Most reliable** — no path mangling |

**Rule:** When running Windows-native commands from git-bash, use PowerShell:

```bash
# ❌ Breaks in git-bash
taskkill /F /IM pythonw.exe

# ✅ Works everywhere
powershell.exe -Command "Stop-Process -Name pythonw -Force"
```

## Verification Checklist

After setting up auto-start:

1. Reboot machine
2. Wait 30 seconds
3. Open Hermes → `/new` session
4. Run `mem0_search(query="test")` → should return results or "No relevant memories" (not "not initialized")
5. If "not initialized": double-click `Restart_Hermes_Gateway.bat` on Desktop → `/new` → retry
