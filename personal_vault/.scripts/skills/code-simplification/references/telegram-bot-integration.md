# Telegram Bot Integration with aiogram 3.x

## Overview
Built a polling Telegram bot using aiogram 3.x that integrates with the existing NL case management system.

## Architecture

```
Telegram → aiogram (polling) → handle_message() → NL pipeline → vault/scripts/
```

## Key Components

### 1. Bot Entry Point (`telegram_bot.py`)
```python
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import asyncio

# NL handler integration
from case_brain_nl_handler import handle_message

# Config
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_USERS = {int(uid.strip()) for uid in os.getenv("TELEGRAM_ALLOWED_USERS", "").split(",") if uid.strip()}

async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(handle_text, F.text)
    
    await dp.start_polling(bot)
```

### 2. Message Handler
```python
async def handle_text(message: types.Message):
    if not is_allowed(message.from_user.id):
        await message.answer("⛔ Not authorized")
        return
    
    text = message.text or ""
    if text.startswith("/"):
        return
    
    result = handle_message(text)  # Existing NL handler
    if result:
        for chunk in [result[i:i+4000] for i in range(0, len(result), 4000)]:
            await message.answer(chunk, parse_mode=ParseMode.HTML)
```

### 3. Commands Handled
| Command | Description |
|---------|-------------|
| `/start` | Show help & syntax |
| `/help` | Same as /start |
| `[new case] ...` | Create new case |
| `[update case ...] ...` | Append thread entry |
| `[edit case ...] ...` | In-place edit |
| `[close case ...]` | Close with lesson learned |

## Configuration (.env)
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_ALLOWED_USERS=123456789,987654321  # Optional allowlist
```

## Key Implementation Details

### 1. Optional Dependencies
```python
try:
    from aiogram import Bot, Dispatcher, types, F
    _AIOGRAM_AVAILABLE = True
except ImportError:
    _AIOGRAM_AVAILABLE = False
```

### 2. Message Chunking
Telegram limit: 4096 chars. Split long responses:
```python
for chunk in [result[i:i+4000] for i in range(0, len(result), 4000)]:
    await message.answer(chunk, parse_mode=ParseMode.HTML)
```

### 3. User Authorization
```python
def is_allowed(user_id: int) -> bool:
    return not ALLOWED_USERS or user_id in ALLOWED_USERS
```

### 4. Environment Variable Loading
```python
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_USERS = {int(uid.strip()) for uid in os.getenv("TELEGRAM_ALLOWED_USERS", "").split(",") if uid.strip()}
```

## Quick Start
```bash
# 1. Install
pip install aiogram

# 2. Configure .env
cp .env.example .env
# Edit .env with your BOT_TOKEN

# 3. Run
python -m lusine_ops.telegram_bot
```

## Quick Commands for Testing
```bash
# Direct run
python -m lusine_ops.telegram_bot

# With custom .env
TELEGRAM_BOT_TOKEN=xxx PYTHONPATH=path python -m lusine_ops.telegram_bot
```

## Common Issues

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError: aiogram` | `pip install aiogram` |
| `TokenValidationError` | Check `TELEGRAM_BOT_TOKEN` format |
| `ModuleNotFoundError: case_brain_nl_handler` | Add vault/scripts to PYTHONPATH |
| Module import errors in service | Set PYTHONPATH in service config |