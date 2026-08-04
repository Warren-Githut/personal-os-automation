# Telegram Bot Integration Pattern (aiogram 3.x) — Proven Pattern

---

## Basic Pattern

For adding Telegram bot interfaces to existing NL pipelines:

```python
# telegram_bot.py
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
# Wire to existing NL handler
from existing_nl_handler import handle_message

async def handle_text(message: types.Message):
    if not is_allowed(message.from_user.id):
        return
    result = handle_message(message.text)  # reuse existing NL logic
    await message.answer(result)
```

Key points:
- Reuse existing NL handler (`handle_message`) — don't duplicate logic
- Use allowlist (`ALLOWED_USERS`) for authorization (empty = dev mode allow all)
- Split long messages (>4096 chars) for Telegram limits
- Graceful error handling with user-friendly messages

---

## Multi-Bot Pattern (NEW)

For multiple isolated bots (e.g., work + personal vaults):

### Architecture
```
@lusine_work_bot      → Work Vault (VAULT_ROOT=.../Warren_OS_Local/vault)
@personal_life_botbot → Personal Vault (VAULT_ROOT=.../Stock_OS/stock_vault)
```

### Per-Bot .env Files

```env
# LUsineWorkBot/.env
TELEGRAM_BOT_TOKEN=***  # From @BotFather → @lusine_work_bot
VAULT_ROOT=C:\Users\khoans\Documents\Warren_OS_Local\vault
TELEGRAM_ALLOWED_USERS=2117653672

# LUsinePersonalBot/.env
TELEGRAM_BOT_TOKEN=***  # Real token from @BotFather
VAULT_ROOT=C:\Users\khoans\Documents\Stock_OS\stock_vault
TELEGRAM_ALLOWED_USERS=2117653672
```

### Bot-Specific .bat Launchers

```bat
:: Work Bot Launcher (Start L'Usine Work Bot.bat)
@echo off
title L'Usine Work Bot
cd /d C:\Users\khoans\AppData\Local\hermes\profiles\warren-profile\skills\lusine-cases
set PYTHONPATH=C:\...\lusine-cases;C:\...\Warren_OS_Local\vault\scripts
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

```bat
:: Personal Bot Launcher (Start L'Usine Personal Bot.bat)
@echo off
title L'Usine Personal Bot
cd /d C:\Users\khoans\AppData\Local\hermes\profiles\personal_profile\skills\lusine-cases
set PYTHONPATH=C:\...\lusine-cases;C:\...\Personal_OS\stock_vault\scripts
set VAULT_ROOT=C:\Users\khoans\Documents\Stock_OS\stock_vault

:: Load .env file
for /f "tokens=1,2 delims==" %%a in ('type "C:\Users\khoans\AppData\Local\LUsinePersonalBot\.env" ^| findstr /r /v "^#" ^| findstr "="') do set %%a=%%b

:loop
echo [%date% %time%] Starting L'Usine Personal Bot...
...same...
```

---

## Single-Bot Template (Original)

```python
# telegram_bot.py
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_USERS = {int(uid.strip()) for uid in os.getenv("TELEGRAM_ALLOWED_USERS", "").split(",") if uid.strip()}

async def cmd_start(message: types.Message):
    if not is_allowed(message.from_user.id):
        return
    await message.answer("🤖 Bot ready...")

async def handle_text(message: types.Message):
    if not is_allowed(message.from_user.id):
        await message.answer("⛔ Not authorized")
        return
    # ... process via handle_message()

async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(handle_text, F.text)
    await dp.start_polling(bot)
```

---

## Key Patterns

### 1. Reuse Existing NL Handler
```python
from existing_nl_handler import handle_message

async def handle_text(message: types.Message):
    result = handle_message(message.text)  # reuse existing NL logic
    await message.answer(result)
```

### 2. Allowlist Authorization
```python
def is_allowed(user_id: int) -> bool:
    return not ALLOWED_USERS or user_id in ALLOWED_USERS
```

### 3. Long Message Splitting
```python
for chunk in [result[i:i+4000] for i in range(0, len(result), 4000)]:
    await message.answer(chunk, parse_mode=ParseMode.HTML)
```

### 4. Graceful Error Handling
```python
try:
    result = handle_message(text)
    await message.answer(result, parse_mode=ParseMode.HTML)
except Exception as e:
    await message.answer(f"⚠️ Error: {str(e)[:200]}")
```

### 5. .env Loading in Python (if not using .bat)
```python
from dotenv import load_dotenv
load_dotenv(r"C:\path\to\.env")  # or let .bat load it
```

---

## Deployment Checklist

- [ ] Separate .env files per bot (never share tokens)
- [ ] Separate VAULT_ROOT per bot (work vs personal)
- [ ] Separate .bat launchers per bot
- [ ] Separate desktop shortcuts for auto-start
- [ ] Clear __pycache__ on deploy
- [ ] Kill python processes before restart
- [ ] Test both bots independently
- [ ] Verify zero cross-contamination in vaults

---

## Windows Known Issues

### WinError 64 — Transient Network Drop (ERROR_NETNAME_DELETED)

**Symptom:** Bot logs `ERROR | Failed to fetch updates - TelegramNetworkError: HTTP Client says - ClientOSError: [WinError 64]` then recovers after ~11s.

**Cause:** Windows TCP connection to Telegram API server forcibly closed. Common triggers: WiFi fluctuation, firewall idle timeout, VPN reconnect, machine wakes from sleep. aiogram's built-in retry handles it automatically.

**Fix — Logging Filter:** Add a `TransientNetworkFilter` class to downgrade WinError 64 from ERROR to WARNING (reduces noise without affecting retry behavior):

```python
class TransientNetworkFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if "WinError 64" in record.getMessage() and record.levelno >= logging.ERROR:
            record.levelno = logging.WARNING
            record.levelname = "WARNING"
        return True

# Apply after logging.basicConfig()
logging.getLogger("aiogram").addFilter(TransientNetworkFilter())
```

Add filter directly in `telegram_bot.py` after `logging.basicConfig()`.

### Bot Process Dies After WinError 64

**Symptom:** Bot stops responding despite aiogram's retry appearing to reconnect.

**Root cause:** Underlying socket state can corrupt after repeated WinError 64 drops, causing the process to exit silently.

**Mitigation:** Use a `.bat` launcher with `:loop` + `goto loop` pattern (auto-restart on crash, 5s delay). See `windows-non-friction-automation.md` for the full pattern.