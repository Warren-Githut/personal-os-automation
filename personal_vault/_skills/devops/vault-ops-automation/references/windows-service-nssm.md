# Windows Service Management with NSSM

## Overview

NSSM (Non-Sucking Service Manager) is the recommended way to run Python scripts as Windows Services for 24/7 background operation. This replaces cron on Windows for long-running processes like Telegram bots, webhook servers, and polling workers.

## Why NSSM over Cron on Windows

| Aspect | Cron (Linux) | NSSM Service (Windows) |
|--------|--------------|------------------------|
| Process lifecycle | Runs, exits | Runs continuously |
| Auto-restart on crash | Manual | Built-in (`AppExit Default Restart`) |
| Auto-start on boot | Via cron `@reboot` | Built-in (`Start SERVICE_AUTO_START`) |
| Logging | stdout/stderr | Redirected to files (`AppStdout`, `AppStderr`) |
| Resource limits | Manual | `AppThrottle`, `AppPriority` |

## Installation

### 1. Install NSSM
```powershell
# One-time setup (Run as Administrator)
$nssmDir = "C:\NSSM"
New-Item -ItemType Directory -Force -Path $nssmDir | Out-Null

$zipUrl = "https://nssm.cc/release/nssm-2.24.zip"
$tempZip = "$env:TEMP\nssm.zip"
$extractDir = "$env:TEMP\nssm"

Invoke-WebRequest -Uri "https://nssm.cc/release/nssm-2.24.zip" -OutFile "$env:TEMP\nssm.zip"
Expand-Archive -Path "$env:TEMP\nssm.zip" -DestinationPath "$env:TEMP\nssm" -Force

$sourceExe = Get-ChildItem "$env:TEMP\nssm\*\win64\nssm.exe" | Select-Object -First 1
Copy-Item $sourceExe.FullName "C:\NSSM\nssm.exe" -Force

# Verify
& "C:\NSSM\nssm.exe" version
```

### 2. No PATH Required
Use full path `C:\NSSM\nssm.exe` directly — no PATH modification needed.

## Service Template for Herkes Skills

### Template: Skill Service Setup
```powershell
$svcName = "LUsineBot_MySkill"
$skillPath = "C:\Users\khoans\AppData\Local\hermes\profiles\warren-profile\skills\my-skill"
$vaultScripts = "C:\Users\khoans\Documents\Warren_OS_Local\vault\scripts"
$logFile = Join-Path $skillPath "bot.log"
$errFile = Join-Path $skillPath "bot_error.log"
$pythonPath = "$skillPath;C:\Users\khoans\Documents\Warren_OS_Local\vault\scripts"

$nssm = "C:\NSSM\nssm.exe"

# Helper to run nssm with Admin
function Invoke-Nssm {
    param($Arguments)
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "C:\NSSM\nssm.exe"
    $psi.Arguments = $Arguments
    $psi.Verb = "runas"
    $psi.UseShellExecute = $true
    $psi.WindowStyle = "Hidden"
    $proc = [System.Diagnostics.Process]::Start($psi)
    $proc.WaitForExit()
    return $proc.ExitCode
}

# Clean up old
if (Get-Service "MyService" -ErrorAction SilentlyContinue) {
    Invoke-Nssm "stop MyService"
    Invoke-Nssm "remove MyService confirm"
}

# Install
Invoke-Nssm "install MyService `\"python.exe`\" `\"-m my_module.my_entrypoint`\""

# Configure
Invoke-Nssm "set MyService AppDirectory `$skillPath"
Invoke-Nssm "set MyService AppStdout `$logFile"
Invoke-Nssm "set MyService AppStderr `$errFile"
Invoke-Nssm "set MyService AppNoConsole 1"
Invoke-Nssm "set MyService AppPriority HIGH_PRIORITY_CLASS"
Invoke-Nssm "set MyService Start SERVICE_AUTO_START"
Invoke-Nssm "set MyService AppExit Default Restart"
Invoke-Nssm "set MyService AppThrottle 1500"
Invoke-Nssm "set MyService AppStopMethodSkip 60000"
Invoke-Nssm "set MyService AppEnvironmentExtra `\"PYTHONPATH=$pythonPath`\""
Invoke-Nssm "set MyService Description `\"My Skill Service`\""

# Start
Invoke-Nssm "start MyService"
```

### Required Environment Variables for Skill Services

| Variable | Value | Purpose |
|----------|-------|---------|
| `PYTHONPATH` | `skill_path;vault/scripts` | Find both skill modules and vault shared modules |
| `VAULT_ROOT` | (optional) | Override auto-detection |

### Critical: Python Path Setup

**Problem:** Skill runs from its directory but needs to import vault modules.

**Fix:** Set `AppEnvironmentExtra` with `PYTHONPATH`:
```
$skillPath;C:\Users\khoans\Documents\Warren_OS_Local\vault\scripts
```

This allows imports like:
```python
from case_brain_nl_handler import handle_message  # from skill
from ops_cases_cli import create_case  # from vault/scripts
```

## Service Management Commands

| Action | Command |
|--------|---------|
| Status | `& "C:\NSSM\nssm.exe" status SvcName` |
| Start | `Start-Service SvcName` or `& "C:\NSSM\nssm.exe" start SvcName` |
| Stop | `Stop-Service SvcName` or `& "C:\NSSM\nssm.exe" stop SvcName` |
| Restart | `Restart-Service SvcName` |
| Logs (stdout) | `Get-Content "path\bot.log" -Wait` |
| Logs (stderr) | `Get-Content "path\bot_error.log" -Wait` |
| Remove | `& "C:\NSSM\nssm.exe" remove SvcName confirm` |

## Configuration Reference (NSSM Registry Keys)

| Setting | Registry Key | Recommended Value |
|---------|--------------|-------------------|
| `AppDirectory` | Working directory | Skill root path |
| `AppStdout` | Stdout log file | `skill_path\bot.log` |
| `AppStderr` | Stderr log file | `skill_path\bot_error.log` |
| `AppNoConsole` | Hide console | `1` |
| `AppPriority` | Process priority | `HIGH_PRIORITY_CLASS` |
| `Start` | Startup type | `SERVICE_AUTO_START` |
| `AppExit` | Exit action | `Default Restart` |
| `AppThrottle` | Restart throttle (ms) | `1500` |
| `AppStopMethodSkip` | Stop timeout (ms) | `60000` |
| `AppEnvironmentExtra` | Extra env vars | `PYTHONPATH=...` |
| `ObjectName` | Service account | `LocalSystem` (default) |

## Troubleshooting

### Service Won't Start
1. Check `bot_error.log` for Python traceback
2. Run manually: `cd skill_path && python -m module.entrypoint`
3. Check `PYTHONPATH` includes both skill and vault/scripts
4. Verify `python.exe` in system PATH or use full path

### Access Denied on NSSM
- Use `Start-Process -Verb RunAs` for NSSM commands
- Or run PowerShell as Administrator

### Service Stops Immediately
- Check `AppThrottle` (default 1500ms restart delay)
- Check `AppExit Default Restart` is set
- Check stderr log for import errors

## Example: L'Usine Telegram Bot Service

See `scripts/lusine-ops/install_all_profiles.sh` for the actual deployment script that installs `lusine-cases` skill as a service across 3 profiles.

## Migration from Cron

| Cron Pattern | NSSM Equivalent |
|--------------|-----------------|
| `@reboot` | `Start SERVICE_AUTO_START` |
| `* * * * *` (polling) | Continuous process with sleep |
| `0 9 * * *` (daily) | Keep service running, internal scheduler |
| `*/5 * * * *` (every 5 min) | Continuous process with 5-min sleep |

For scheduled tasks inside a service, use Python `schedule` library or `asyncio.sleep()` loops rather than external cron.