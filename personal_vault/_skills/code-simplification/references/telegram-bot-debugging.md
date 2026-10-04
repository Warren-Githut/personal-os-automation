# Telemetry Bot Debugging Guide

## Common Issues & Fixes

### 1. ModuleNotFoundError: lusine_ops.telegram_bot

**Symptom:**
```
ModuleNotFoundError: No module named 'lusine_ops'
```

**Cause:** Python can't find the module because PYTHONPATH doesn't include the skill directory.

**Fix:**
```bash
# Option 1: Set PYTHONPATH explicitly
PYTHONPATH=/path/to/skill:/path/to/vault/scripts python -m lusine_ops.telegram_bot

# Option 2: Run from skill directory
cd /path/to/skill
python -m lusine_ops.telegram_bot

# Option 3: In batch file
set PYTHONPATH=C:\Path\To\Skill;C:\Path\To\Vault\Scripts
python -m lusine_ops.telegram_bot
```

### 2. ModuleNotFoundError: case_brain_nl_handler

**Symptom:**
```
ModuleNotFoundError: No module named 'case_brain_nl_handler'
```

**Cause:** The handler is in `vault/scripts/` but not in PYTHONPATH.

**Fix:**
```python
# In telegram_bot.py
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).parent
VAULT_SCRIPTS = SKILL_ROOT.parent.parent / "scripts"
sys.path.insert(0, str(VAULT_SCRIPTS))

from case_brain_nl_handler import handle_message
```

### 3. ModuleNotFoundError: aiogram

**Symptom:**
```
ImportError: cannot import name 'aiogram'
```

**Fix:**
```bash
pip install aiogram
# Windows specific
C:\Users\user\AppData\Local\Programs\Python\Python312\python.exe -m pip install aiogram
```

### 4. TokenValidationError: Token is invalid

**Symptom:**
```
aiogram.utils.token.TokenValidationError: Token is invalid!
```

**Cause:** Bot token missing or invalid format.

**Fix:**
```bash
# In .env file
TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIJKlmNoP...

# Or in batch file
set TELEGRAM_BOT_TOKEN=your_token_here
```

### 5. ModuleNotFoundError push_gcal

**Symptom:**
```
ModuleNotFoundError: No module named 'push_gcal'
```

**Fix:** Optional dependency (see optional-dependency-pattern.md)
```python
try:
    from push_gcal import load_env
    _CALENDAR_AVAILABLE = True
except ImportError:
    _CALENDAR_AVAILABLE = False
```

### 6. NSSM Service Won't Start

**Symptom:**
```
Can't open service! OpenService(): Access is denied.
```

**Causes & Fixes:**
| Cause | Fix |
|-------|-----|
| Not running as Admin | Run PowerShell as Administrator |
| Service runs as SYSTEM | Set ObjectName to user account |
| Python path wrong | Set PYTHONPATH in service config |
| Crash on startup | Check bot_error.log |

**Fix with NSSM:**
```powershell
& $nssm set $svcName ObjectName "username" "PASSWORD"
& $nssm set $svcName AppEnvironmentExtra "PYTHONPATH=path1;path2"
```

### 7. .env File Not Loading

**Symptom:** `TELEGRAM_BOT_TOKEN not set in environment`

**Fix:** Load .env in bot code or batch file.

**Batch file (.bat):**
```bat
for /f "tokens=1* delims==" %%a in ('type "C:\path\to\.env" 2^>nul ^| findstr /r /v "^#" ^| findstr "="') do set %%a=%%b
```

**Python:**
```python
from dotenv import load_dotenv
load_dotenv()  # Loads from .env in current directory

# Or explicit path
load_dotenv("C:/path/to/.env")
```

### 8. Access Denied to AppData

**Symptom:** Service can't access `C:\Users\...\AppData\Local\...`

**Cause:** Service runs as SYSTEM account.

**Fix:** Run service as user account:
```powershell
& $nssm set $svcName ObjectName "username" "PASSWORD"
```

### 9. Bot Crashes on Startup - Check Logs

```bat
@echo off
:loop
echo [%date% %time%] Starting bot...
python -m lusine_ops.telegram_bot
echo [%date% %time%] Bot stopped. Restarting in 5s...
timeout /t 5 >nul
goto loop
```

**Check logs:**
```powershell
Get-Content "C:\Path\To\bot_error.log" -Tail 50
```

### 9. PYTHONPATH Issues in Service

**Problem:** Service can't import modules that work in terminal.

**Fix:**
```powershell
& $nssm set $svcName AppEnvironmentExtra "PYTHONPATH=C:\Path\To\Skill;C:\Path\To\Vault\Scripts"
```

### 10. Bot Works in Terminal But Not as Service

**Checklist:**
- [ ] PYTHONPATH set in service
- [ ] .env file accessible (not in user profile)
- [ ] Service runs as correct user (not SYSTEM)
- [ ] Dependencies installed for that Python
- [ ] Logs show actual error (check bot_error.log)

## Debug Checklist

```bash
# 1. Test import manually
PYTHONPATH=/path/to/skill:/path/to/scripts python -c "import lusine_ops.telegram_bot; print('OK')"

# 2. Test with token
TELEGRAM_BOT_TOKEN=xxx PYTHONPATH=... python -m lusine_ops.telegram_bot

# 3. Run manually as user
cd /skill/dir && python -m lusine_ops.telegram_bot

# 4. Check service config
nssm get MyBot AppDirectory
nssm get MyBot AppEnvironmentExtra
nssm get MyBot ObjectName

# 5. View live logs
Get-Content bot.log -Wait
```