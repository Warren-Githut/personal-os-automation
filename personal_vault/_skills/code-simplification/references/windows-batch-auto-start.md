# Windows Batch File Auto-Start for Python Applications

## Overview
Simple `.bat` file in Windows Startup folder - runs on login, restarts on crash, no admin rights needed.

## Template

```bat
@echo off
title My App Bot
cd /d C:\Path\To\Project
set PYTHONPATH=C:\Path\To\Project;C:\Path\To\Deps

:loop
echo [%date% %time%] Starting bot...
python -m my_module.bot
echo [%date% %time%] Bot stopped. Restarting in 5s...
timeout /t 5 >nul
goto loop
```

## How It Works

| Feature | Implementation |
|---------|----------------|
| Auto-restart | `goto loop` after crash |
| Delay between restarts | `timeout /t 5 >nul` |
| Logging | Console output + timestamps |
| Environment isolation | `set PYTHONPATH=...` |
| Runs on login | Place in Startup folder |

## Setup (30 seconds)

1. **Create `.bat` file** on Desktop
2. **Save as** `Start My Bot.bat` (must end with `.bat`)
3. **Add to startup:**
   - `Win + R` → `shell:startup` → Enter
   - Copy `.bat` file → Paste in Startup folder

## Auto-Start Behavior

| Event | Behavior |
|-------|----------|
| User logs in | `.bat` runs automatically |
| Bot crashes | Restarts in 5 seconds |
| Windows restarts | Bot starts when user logs in |
| Manual stop | Click **X** on console window |

## Python Path Configuration

```bat
:: Activate specific Python (recommended)
"C:\Users\user\AppData\Local\Programs\Python\Python312\python.exe" -m my_module

:: Or use PATH python with explicit PYTHONPATH
set PYTHONPATH=C:\Project;C:\Deps
python -m my_module
```

## Loading .env Securely

```bat
:: Load .env from secure location (outside project)
for /f "tokens=1* delims==" %%a in ('type "C:\Users\user\AppData\Local\MyApp\.env" 2^>nul ^| findstr /r /v "^#" ^| findstr "="') do set %%a=%%b

:: Then use %TELEGRAM_BOT_TOKEN% in Python
python -m my_module
```

## File Structure
```
Desktop/
  Start My Bot.bat          # Click to start
  
AppData\Local\MyApp\
  .env                      # Secrets (not in repo)
  
Project\
  my_module/
  main.py
```

## Key Benefits

| Benefit | How |
|---------|-----|
| No admin rights | Runs as current user |
| Auto-restart | `goto loop` + `timeout` |
| Secure secrets | `.env` in AppData, not repo |
| Debug visible | Console shows all logs |
| Zero deps | Built-in Windows batch |
| Works off-path | Uses full Python path |

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `python` not found | Use full path: `C:\Python312\python.exe` |
| Module not found | Check `PYTHONPATH` in batch file |
| `.env` not loading | Check path in `type "..."` command |
| Bot stops immediately | Check `bot_error.log` for traceback |

## Startup Folder Path
```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
```
Or run: `Win+R` → `shell:startup` → Enter