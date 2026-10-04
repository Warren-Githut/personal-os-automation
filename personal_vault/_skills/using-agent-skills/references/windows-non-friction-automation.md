# Windows Non-Friction Automation Patterns

## Session Context
**Date:** 2026-06-19
**Task:** Deploy Telegram bot with zero-friction startup for non-technical user
**Constraint:** User is non-IT, prefers click-to-run, no Windows services complexity

---

## Windows Service vs .bat Startup

| Approach | Pros | Cons |
|----------|------|------|
| **NSSM Service** | Runs as SYSTEM, auto-start on boot | Requires admin, password, SYSTEM account can't access user AppData |
| **.bat in Startup** | Runs as user, accesses AppData, zero-config | Must login first |

**Decision:** `.bat` in Startup folder → zero friction for non-IT user

---

## .bat Launcher Pattern (Single Bot)

```bat
@echo off
title L'Usine Telegram Bot
cd /d %SKILL_DIR%
set PYTHONPATH=%SKILL_DIR%;%VAULT_SCRIPTS_DIR%

:: Load .env file before starting bot
for /f "tokens=1,2 delims==" %%a in ('type "path\.env" ^| findstr /r /v "^#" ^| findstr "="') do set %%a=%%b

:loop
echo [%date% %time%] Starting bot...
python -m lusine_ops.telegram_bot
echo [%date% %time%] Bot stopped. Restarting in 5s...
timeout /t 5 >nul
goto loop
```

### Key Elements

| Element | Purpose |
|---------|---------|
| `cd /d %SKILL_DIR%` | Set working directory to skill dir (/d for cross-drive) |
| `set PYTHONPATH=...` | Add skill + vault scripts to Python path |
| `for /f ...` | Load `.env` file variables into environment |
| `:loop` + `goto loop` | Auto-restart on crash (5s delay) |
| `timeout /t 5` | Prevent rapid restart loops |

## .env File Loading in Batch

```bat
for /f "tokens=1,2 delims==" %%a in ('type "path\.env" ^| findstr /r /v "^#" ^| findstr "="') do set %%a=%%b
```

| Component | Explanation |
|-----------|-------------|
| `type "path\.env"` | Read .env file content |
| `findstr /r /v "^#"` | Exclude comment lines (starting with #) |
| `findstr "="` | Only lines containing = (key=value) |
| `tokens=1,2 delims==` | Split on = into %%a (key) and %%b (value) |
| `set %%a=%%b` | Set environment variable |

## Startup Folder Auto-Launch

```powershell
# Open startup folder
start shell:startup

# Or get path
[Environment]::GetFolderPath('Startup')
# C:\Users\khoans\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
```

1. Create `.bat` on Desktop
2. Copy to `shell:startup` folder
3. Auto-runs on user login
4. Runs as user (accesses AppData, network drives)

## Secure .env Location

**Don't** put `.env` in skill or vault directory (git risk)

**Do** put in user AppData:
```
C:\Users\khoans\AppData\Local\LUsineBot\.env
```

Load in .bat:
```bat
for /f "tokens=1,2 delims==" %%a in ('type "C:\Users\khoans\AppData\Local\LUsineBot\.env" ^| findstr /r /v "^#" ^| findstr "="') do set %%a=%%b
```

---

## Multi-Bot Pattern (NEW)

For multiple isolated bots (work + personal vaults), each with its own .bat, .env, and vault:

### Work Bot Launcher (Start L'Usine Work Bot.bat)
```bat
@echo off
title L'Usine Work Bot
cd /d C:\Users\khoans\AppData\Local\hermes\profiles\warren-profile\skills\lusine-cases
set PYTHONPATH=C:\Users\khoans\AppData\Local\hermes\profiles\warren-profile\skills\lusine-cases;C:\Users\khoans\Documents\Warren_OS_Local\vault\scripts
set VAULT_ROOT=C:\Users\khoans\Documents\Warren_OS_Local\vault

:: Load .env file
for /f "tokens=1,2 delims==" %%a in ('type "C:\Users\khoans\AppData\Local\LUsineWorkBot\.env" ^| findstr /r /v "^#" ^| findstr "="') do set %%a=%%b

:loop
echo [%date% %time%] Starting L'Usine Work Bot...
C:\Users\khoans\AppData\Local\Programs\Python\Python312\python.exe -m lusine_ops.telegram_bot
echo [%date% %time%] Bot stopped. Restarting in 5s...
timeout /t 5 >nul
goto loop
```

### Personal Bot Launcher (Start L'Usine Personal Bot.bat)
```bat
@echo off
title L'Usine Personal Bot
cd /d C:\Users\khoans\AppData\Local\hermes\profiles\personal_profile\skills\lusine-cases
set PYTHONPATH=C:\Users\khoans\AppData\Local\hermes\profiles\personal_profile\skills\lusine-cases;C:\Users\khoans\Documents\Personal_OS\stock_vault\scripts
set VAULT_ROOT=C:\Users\khoans\Documents\Stock_OS\stock_vault

:: Load .env file
for /f "tokens=1,2 delims==" %%a in ('type "C:\Users\khoans\AppData\Local\LUsinePersonalBot\.env" ^| findstr /r /v "^#" ^| findstr "="') do set %%a=%%b

:loop
echo [%date% %time%] Starting L'Usine Personal Bot...
C:\Users\khoans\AppData\Local\Programs\Python\Python312\python.exe -m lusine_ops.telegram_bot
echo [%date% %time%] Bot stopped. Restarting in 5s...
timeout /t 5 >nul
goto loop
```

---

## Bot Process Management (Multi-Bot)

### Kill All Instances
```powershell
taskkill /F /IM python.exe
taskkill /F /FI "WINDOWTITLE eq *L'Usine*"
```

### Clear Caches
```powershell
Remove-Item "$env:APPDATA\Local\hermes\profiles\warren-profile\skills\lusine-cases\__pycache__" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$env:APPDATA\Local\hermes\profiles\lusine-profile\skills\lusine-cases\__pycache__" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$env:APPDATA\Local\hermes\profiles\personal_profile\skills\lusine-cases\__pycache__" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "C:\Users\khoans\Documents\Warren_OS_Local\vault\scripts\__pycache__" -Recurse -Force -ErrorAction SilentlyContinue
```

### Restart Both Bots
```powershell
Start-Process "cmd.exe" -ArgumentList "/c", "`"C:\Users\khoans\Desktop\Start L'Usine Work Bot.bat`""
Start-Process "cmd.exe" -ArgumentList "/c", "\"C:\Users\khoans\Desktop\Start L'Usine Personal Bot.bat`""
```

---

## Secure .env Location

**Don't** put `.env` in skill or vault directory (git risk)

**Do** put in user AppData:
```
C:\Users\khoans\AppData\Local\LUsineWorkBot\.env      # Work bot
C:\Users\khoans\AppData\Local\LUsinePersonalBot\.env  # Personal bot
```

Load in .bat:
```bat
for /f "tokens=1,2 delims==" %%a in ('type "C:\Users\khoans\AppData\Local\LUsineWorkBot\.env" ^| findstr /r /v "^#" ^| findstr "="') do set %%a=%%b
```

---

## Bot Process Management (Multi-Bot)

### Kill All Instances
```powershell
taskkill /F /IM python.exe
taskkill /F /FI "WINDOWTITLE eq *L'Usine*"
```

### Clear Caches
```powershell
Remove-Item "$env:APPDATA\Local\hermes\profiles\warren-profile\skills\lusine-cases\__pycache__" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$env:APPDATA\Local\hermes\profiles\lusine-profile\skills\lusine-cases\__pycache__" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$env:APPDATA\Local\hermes\profiles\personal_profile\skills\lusine-cases\__pycache__" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "C:\Users\khoans\Documents\Warren_OS_Local\vault\scripts\__pycache__" -Recurse -Force -ErrorAction SilentlyContinue
```

### Restart Both Bots
```powershell
Start-Process "cmd.exe" -ArgumentList "/c", "`"C:\Users\khoans\Desktop\Start L'Usine Work Bot.bat`""
Start-Process "cmd.exe" -ArgumentList "/c", "`"C:\Users\khoans\Desktop\Start L'Usine Personal Bot.bat`""
```

---

## Secure .env Location

**Don't** put `.env` in skill or vault directory (git risk)

**Do** put in user AppData:
```
C:\Users\khoans\AppData\Local\LUsineWorkBot\.env      # Work bot
C:\Users\khoans\AppData\Local\LUsinePersonalBot\.env  # Personal bot
```

Load in .bat:
```bat
for /f "tokens=1,2 delims==" %%a in ('type "C:\Users\khoans\AppData\Local\LUsineWorkBot\.env" ^| findstr /r /v "^#" ^| findstr "="') do set %%a=%%b
```

---

## Non-Friction Checklist for Non-IT Users

- [ ] Separate `.bat` file per bot on Desktop (click to run)
- [ ] Auto-start via `shell:startup` (optional)
- [ ] Separate `.env` per bot in secure AppData location (not in repo)
- [ ] Auto-restart on crash (5s delay)
- [ ] Clear logs with timestamps
- [ ] No admin rights needed
- [ ] No Windows service configuration
- [ ] No NSSM/password/service account complexity

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ModuleNotFoundError` | PYTHONPATH wrong | Check `set PYTHONPATH` in .bat |
| `TELEGRAM_BOT_TOKEN not set` | .env not loaded | Check .env path + `for /f` loop |
| `Token is invalid` | Placeholder token | Update .env with real token from @BotFather |
| Bot crashes immediately | Syntax error in skill | Check bot.log / bot_error.log |
| No restart on crash | Missing `:loop` | Add `goto loop` in .bat |
| Both bots write to same vault | VAULT_ROOT wrong | Check `set VAULT_ROOT` in each .bat |
| **WinError 64 — `[WinError 64] The specified network name is no longer available`** | Transient Windows TCP drop (WiFi fluctuation, firewall timeout, sleep/wake cycle). aiogram retries but logs ERROR. | Add `TransientNetworkFilter` in `telegram_bot.py` to downgrade to WARNING (see `telegram-bot-pattern.md` → Windows Known Issues). Bot may silently exit after repeated drops — use `.bat` launcher with `:loop` auto-restart. |

## Startup Folder Pitfalls

### ⚠️ Path Resolution in Startup Scripts

When placing a Python script directly in `shell:startup` (not a `.bat`), path resolution via `Path(__file__).resolve().parents[2]` will be **wrong** — it resolves relative to the Startup folder (e.g. `C:\Users\khoans\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\`), NOT your project directory.

**Fix:** Always use a `.bat` launcher in Startup that:
1. `cd /d` to the correct working directory
2. Sets `PYTHONPATH` explicitly
3. Loads `.env` from `AppData\Local\`
4. Calls `python -m module_name` (not a standalone `.py` script)

**Never** put a standalone `.py` script directly in the Startup folder — use a `.bat` wrapper instead.