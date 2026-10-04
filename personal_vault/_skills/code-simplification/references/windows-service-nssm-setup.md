# Windows Service Setup with NSSM for Python Applications

## Overview
NSSM (Non-Sucking Service Manager) installs Python applications as Windows Services that run 24/7, auto-start on boot, and auto-restart on crash.

## Quick Install

### 1. Install NSSM
```powershell
# Download and install to C:\NSSM
$url = "https://nssm.cc/release/nssm-2.24.zip"
$zip = "$env:TEMP\nssm.zip"
$extract = "$env:TEMP\nssm"

Invoke-WebRequest -Uri $url -OutFile $zip
Expand-Archive -Path $zip -DestinationPath $extract -Force
$src = Get-ChildItem "$extract\*\win64\nssm.exe" | Select-Object -First 1
Copy-Item $src.FullName "C:\NSSM\nssm.exe" -Force
```

### 2. Create Service (Run as Administrator)
```powershell
$nssm = "C:\NSSM\nssm.exe"
$svcName = "MyPythonBot"

# Install
& $nssm install $svcName "python.exe" "-m my_module.bot"

# Configure
& $nssm set $svcName AppDirectory "C:\path\to\project"
& $nssm set $svcName AppStdout "C:\path\to\project\bot.log"
& $nssm set $svcName AppStderr "C:\path\to\project\bot_error.log"
& $nssm set $svcName AppNoConsole 1
& $nssm set $svcName AppPriority HIGH_PRIORITY_CLASS
& $nssm set $svcName Start SERVICE_AUTO_START
& $nssm set $svcName Description "My Python Bot"
& $nssm set $svcName AppExit Default Restart
& $nssm set $svcName AppThrottle 1500
& $nssm set $svcName AppStopMethodSkip 60000

# CRITICAL: Run as specific user (not SYSTEM) for file access
& $nssm set $svcName ObjectName "username" "PASSWORD"

# Start
& $nssm start $svcName
```

## Key Configuration Options

| Option | Value | Purpose |
|--------|-------|---------|
| `AppNoConsole 1` | Hide console window | Runs truly in background |
| `Start SERVICE_AUTO_START` | Auto-start on boot | Runs after Windows starts |
| `AppExit Default Restart` | Auto-restart on crash | Self-healing |
| `AppThrottle 1500` | 1.5s between restarts | Prevents restart loops |
| `AppStopMethodSkip 60000` | 60s graceful shutdown | Clean shutdown |
| `ObjectName "user" "pwd"` | Run as specific user | Access user files/AppData |

## Critical: Run as User Account

**Problem:** Windows Services run as SYSTEM by default, which cannot access user-specific paths like `AppData\Local`.

**Solution:** Set service to run as your user account:
```powershell
& $nssm set $svcName ObjectName "username" "YOUR_WINDOWS_PASSWORD"
```

## Managing Services

| Task | Command |
|------|---------|
| Check status | `Get-Service MyBot | Select Name, Status` |
| View log realtime | `Get-Content "C:\path\bot.log" -Wait` |
| Restart | `& $nssm restart MyBot` |
| Stop | `& $nssm stop MyBot` |
| Remove | `& $nssm remove MyBot confirm` |

## Complete Unattended Install Script

```powershell
# Run as Administrator
$ErrorActionPreference = "Stop"
$nssm = "C:\NSSM\nssm.exe"

# Install NSSM if needed
if (-not (Test-Path $nssm)) {
    $zip = Invoke-WebRequest "https://nssm.cc/release/nssm-2.24.zip" -OutFile "$env:TEMP\nssm.zip"
    Expand-Archive "$env:TEMP\nssm.zip" "$env:TEMP\nssm" -Force
    $exe = Get-ChildItem "$env:TEMP\nssm\*\win64\nssm.exe" | Select -First 1
    New-Item -ItemType Directory -Force -Path "C:\NSSM" | Out-Null
    Copy-Item $exe.FullName "C:\NSSM\nssm.exe" -Force
}

# Configure 3 profiles
$profiles = @(
    @{ Name = "warren-profile"; SkillPath = "C:\Users\khoans\AppData\Local\hermes\profiles\warren-profile\skills\lusine-cases" },
    @{ Name = "lusine-profile"; SkillPath = "C:\Users\khoans\AppData\Local\hermes\profiles\lusine-profile\skills\lusine-cases" },
    @{ Name = "personal_profile"; SkillPath = "C:\Users\khoans\AppData\Local\hermes\profiles\personal_profile\skills\lusine-cases" }
)

$nssmExe = "C:\NSSM\nssm.exe"
$vaultScripts = "C:\Users\khoans\Documents\Warren_OS_Local\vault\scripts"

function Invoke-Nssm { param($Args) 
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $nssmExe; $psi.Arguments = $Args
    $psi.Verb = "runas"; $psi.UseShellExecute = $true; $psi.WindowStyle = "Hidden"
    [System.Diagnostics.Process]::Start($psi).WaitForExit()
}

foreach ($p in $profiles) {
    $svcName = "LUsineBot_$($p.Name)"
    $pyPath = "$($p.SkillPath);$vaultScripts"
    
    if (Get-Service $svcName -ErrorAction SilentlyContinue) {
        Invoke-Nssm "stop $svcName"
        Invoke-Nssm "remove $svcName confirm"
    }
    
    Invoke-Nssm "install $svcName `\"python.exe`" `-m lusine_ops.telegram_bot`""
    Invoke-Nssm "set $svcName AppDirectory `"$($p.SkillPath)`""
    Invoke-Nssm "set $svcName AppEnvironmentExtra `\"PYTHONPATH=$pyPath`""
    Invoke-Nssm "set $svcName AppStdout `"$(Join-Path $p.SkillPath "bot.log")`""
    Invoke-Nssm "set $svcName AppStderr `"$(Join-Path $p.SkillPath "bot_error.log")`""
    Invoke-Nssm "set $svcName AppNoConsole 1"
    Invoke-Nssm "set $svcName AppPriority HIGH_PRIORITY_CLASS"
    Invoke-Nssm "set $svcName Start SERVICE_AUTO_START"
    Invoke-Nssm "set $svcName Description `\"L'Usine Case Bot for $($p.Name)`""
    Invoke-Nssm "set $svcName AppExit Default Restart"
    Invoke-Nssm "set $svcName AppThrottle 1500"
    Invoke-Nssm "set $svcName AppStopMethodSkip 60000"
    Invoke-Nssm "set $svcName ObjectName `\"khoans`" `\"YOUR_PASSWORD`""
    
    Invoke-Nssm "start $svcName"
}

Get-Service LUsineBot* | Select Name, Status
```

## Key Points

| Issue | Solution |
|-------|----------|
| `Can't open service! Access is denied` | Use `Start-Process -Verb RunAs` wrapper or run PowerShell as Admin |
| Service stops immediately | Check `bot_error.log` - usually missing PYTHONPATH or missing deps |
| Access denied to AppData | Set `ObjectName` to run as user account |
| Python module not found | Set `AppEnvironmentExtra PYTHONPATH=path1;path2` |