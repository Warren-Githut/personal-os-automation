# Multi-Profile Skill Distribution - Session Reference

## Session Context
**Date:** 2026-06-19
**Task:** Deploy lusine-cases skill to 3 Hermes profiles (warren-profile, lusine-profile, personal_profile)
**Source:** `vault/scripts/lusine-ops/` → Single source of truth

## Distribution Architecture

```
vault/scripts/lusine-ops/          ← SINGLE SOURCE OF TRUTH
├── SKILL.md
├── pyproject.toml
├── lusine_ops/
│   ├── cli.py
│   ├── vault_resolver.py
│   ├── telegram_bot.py
│   └── commands/
├── tests/
└── install_all_profiles.sh
        ↓ deploy (cp -r)
~/.hermes/profiles/warren-profile/skills/lusine-cases/
~/.hermes/profiles/lusine-profile/skills/lusine-cases/
~/.hermes/profiles/personal_profile/skills/lusine-cases/
```

**⚠️ CRITICAL:** For multi-vault architecture, each profile points to a different VAULT_ROOT:
- `warren-profile` → `C:\Users\khoans\Documents\Warren_OS_Local\vault` (work vault)
- `lusine-profile` → `C:\Users\khoans\Documents\Warren_OS_Local\vault` (work vault)
- `personal_profile` → `C:\Users\khoans\Documents\Stock_OS\stock_vault` (personal vault)

See `references/multi-vault-multi-bot-architecture.md` for complete architecture.

---

## Deployment Protocol

```bash
# 1. Make changes in vault/scripts/lusine-ops/
# 2. Sync to all profiles
for profile in warren-profile lusine-profile personal_profile; do
  cp -r vault/scripts/lusine-ops/* \
    ~/.hermes/profiles/$profile/skills/lusine-cases/
done

# 2. Clear ALL Python caches (CRITICAL!)
find ~/.hermes/profiles -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find vault/scripts -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# 3. Kill all running processes
taskkill /F /IM python.exe

# 4. Restart all instances
# Each bot must be restarted per its profile's vault
./start_lusine_work_bot.bat      # warren-profile, lusine-profile
./start_lusine_personal_bot.bat  # personal_profile
```

---

## Key Files to Sync

| File | Purpose |
|------|---------|
| `case_brain_nl_handler.py` | Core NL handling + slug generation + VAULT_ROOT |
| `telegram_bot.py` | Aiogram 3.x polling bot |
| `cli.py` | CLI entrypoint (`ops-cases`) |
| `vault_resolver.py` | VAULT_ROOT discovery |
| `commands/*.py` | Thin command wrappers |
| `tests/` | Battle test suites |
| `SKILL.md` | Skill manifest |
| `pyproject.toml` | Package metadata |
| `install_all_profiles.sh` | Deployment script |

---

## Windows .bat Launcher for Non-Friction Startup

```bat
@echo off
title L'Usine Telegram Bot
cd /d %SKILL_DIR%
set PYTHONPATH=%SKILL_DIR%;%VAULT_SCRIPTS_DIR%

:: Load .env file before starting
for /f "tokens=1,2 delims==" %%a in ('type "path\.env" ^| findstr /r /v "^#" ^| findstr "="') do set %%a=%%b

:loop
echo [%date% %time%] Starting bot...
python -m lusine_ops.telegram_bot
echo [%date% %time%] Bot stopped. Restarting in 5s...
timeout /t 5 >nul
goto loop
```

**Per-Bot Launchers:**
- `Start L'Usine Work Bot.bat` → loads `LUsineWorkBot\.env`, sets work VAULT_ROOT
- `Start L'Usine Personal Bot.bat` → loads `LUsinePersonalBot\.env`, sets personal VAULT_ROOT

**Per-Profile .bat Mapping:**
- `warren-profile`, `lusine-profile` → `Start L'Usine Work Bot.bat`
- `personal_profile` → `Start L'Usine Personal Bot.bat`

---

## Key Environment Variables

```env
# .env file (secure location: C:\Users\khoans\AppData\Local\LUsineBot\.env)
TELEGRAM_BOT_TOKEN=***  # Real token from @BotFather
TELEGRAM_ALLOWED_USERS=2117653672  # Optional: comma-separated user IDs
VAULT_ROOT=C:\...\vault  # Or personal_vault
GOOGLE_CALENDAR_CREDENTIALS_PATH=C:\...json  # Optional
```

---

## Startup Shortcut

1. Create `.bat` file on Desktop
2. Copy to `shell:startup` for auto-launch on login
3. Click once to run; auto-restarts on crash

---

## VAULT_ROOT Resolution (Critical)

```python
# In handler, use absolute path or env var
import os
from pathlib import Path

VAULT_ROOT = Path(os.getenv("VAULT_ROOT", r"C:\Users\khoans\Documents\Warren_OS_Local\vault"))
# NOT: Path(__file__).resolve().parents[1]  # breaks when run from profile dir
```

**Per-Profile Defaults:**
- `warren-profile`, `lusine-profile` → `C:\Users\khoans\Documents\Warren_OS_Local\vault`
- `personal_profile` → `C:\Users\khoans\Documents\Stock_OS\stock_vault`

---

## Verification Checklist

After deployment:
- [ ] All 3 profiles have identical skill code
- [ ] All `__pycache__` directories cleared
- [ ] All python processes killed
- [ ] Bot starts without `TELEGRAM_BOT_TOKEN not set` error
- [ ] `[new case] test` generates proper Vietnamese slug
- [ ] All 30 tests pass (8 orchestrator + 8 NL + 7 resolver + 6 smoke)
- [ ] **Work bot** writes to `Warren_OS_Local\vault\_cases`
- [ ] **Personal bot** writes to `Personal_OS\stock_vault\_cases`
- [ ] Zero cross-contamination between vaults