# Long-Running Process Pitfalls - Session Reference

## Session Context
**Date:** 2026-06-19
**Task:** Fix Vietnamese slug generation in L'Usine case management Telegram bot
**Root Cause:** Long-running Telegram bot process had stale bytecode in memory

## Problem
Bot was generating broken Vietnamese slugs:
- Input: "phần 5 trái ổ cỏ trái bơ..."
- Broken: `2026-06-19_ph-n-5-tr-i-o-c-o-tr-i-b-b-v-mi-ng-n-m-m-a-xu-n`
- Correct: `2026-06-19_phan-5-trai-o-co-trai-bo-bo-vo-mieng-nem-mua-xua`

## Root Cause Analysis

### 1. Stale Bytecode in Long-Running Process
- Telegram bot runs continuously as a polling process
- Loads `case_brain_nl_handler.py` at startup
- Code fixes in `vault/scripts/` not picked up until process restart
- Python bytecode cached in `__pycache__/` directories

### 2. Multi-Profile Skill Distribution
- Skill deployed to 3 Hermes profiles:
  - `warren-profile` (main)
  - `lusine-profile`
  - `personal_profile`
- Each profile has its own copy of the skill
- All copies must be synced + caches cleared

### 3. VAULT_ROOT Path Resolution
- Skill runs from `~/.hermes/profiles/*/skills/lusine-cases/`
- `Path(__file__).resolve().parents[1]` points to skill dir, not vault
- Fixed by hardcoding absolute vault path:
  ```python
  VAULT_ROOT = Path(os.getenv("VAULT_ROOT", r"C:\Users\khoans\Documents\Warren_OS_Local\vault"))
  ```

### 4. Environment Variable Loading
- `.bat` launcher didn't load `.env` file
- Bot couldn't find `TELEGRAM_BOT_TOKEN`
- Fixed by adding `for /f` loop to load `.env` variables

## Fix Sequence (Nuclear Reset)
```powershell
# 1. Kill ALL python processes
taskkill /F /IM python.exe

# 2. Clear ALL caches
Remove-Item "$env:APPDATA\Local\hermes\profiles\warren-profile\skills\lusine-cases\__pycache__" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "C:\Users\khoans\Documents\Warren_OS_Local\vault\scripts\__pycache__" -Recurse -Force -ErrorAction SilentlyContinue

# 3. Sync all profiles (vault → profiles)
cp -r vault/scripts/skill-name/* ~/.hermes/profiles/warren-profile/skills/skill-name/
cp -r vault/scripts/skill-name/* ~/.hermes/profiles/lusine-profile/skills/skill-name/
cp -r vault/scripts/skill-name/* ~/.hermes/profiles/personal_profile/skills/skill-name/

# 4. Restart bot
Start-Process "cmd.exe" -ArgumentList "/c", "`"C:\Users\khoans\Desktop\Start L'Usine Bot.bat`""
```

## Key Lessons for Future
1. **Long-running processes need explicit restart** after code changes
2. **Clear `__pycache__` everywhere** - vault + all profile skill dirs
3. **Vault is single source of truth** - fix there, deploy to profiles
4. **Long-running bots need explicit restart protocol** - not just file sync
5. **Environment variables (.env) need explicit loading** in Windows batch
6. **Path resolution must use absolute VAULT_ROOT** when skill runs from profile dir

## Vietnamese Slug Fix Details
```python
def _slugify(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[-\s]+", "-", text).strip("-")
    return text[:48]
```

## Verification
All 30 tests pass:
- 8 orchestrator tests
- 8 NL parser/handler tests  
- 7 vault resolver tests
- 6 smoke tests (3 profiles × 2 tests)