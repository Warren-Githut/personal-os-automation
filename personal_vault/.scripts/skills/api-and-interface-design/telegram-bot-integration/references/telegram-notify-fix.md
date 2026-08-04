# Telegram Notify Fix – Minimal Wrapper for Hermes

## Why this fix exists
The stock‑capture pipeline imports `telegram_notify` to send Telegram updates.  
When the module is missing, the pipeline crashes with:

```
ModuleNotFoundError: No module named 'telegram_notify'
```

This file documents the lightweight wrapper that was created to resolve the issue and to remind future agents of the correct pattern.

## Created Files
- `telegram_notify.py` – placed under `scripts/` in the *stock‑capture* vault.
- The script reads `TELEGRAM_BOT_TOKEN` and `TELEGRAM_ALLOWED_USERS` from the environment.
- It gracefully returns `False` if credentials are missing or if the HTTP request fails.

## Content of `telegram_notify.py`

```python
import os
import urllib.request
import urllib.parse

def send_telegram(message: str) -> bool:
    """
    Minimal Telegram notification wrapper.
    - Reads TELEGRAM_BOT_TOKEN and TELEGRAM_ALLOWED_USERS from environment.
    - Sends a basic text message via Telegram Bot API.
    - Returns True on success, False on any error.
    """
    try:
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        allowed = os.getenv('TELEGRAM_ALLOWED_USERS')
        if not token or not allowed:
            return False

        # Extract first user ID from the comma‑separated list
        chat_id = allowed.split(',')[0].strip()

        # Build the Telegram API URL
        import urllib.request, urllib.parse, json
        url = f'https://api.telegram.org/bot{urllib.parse.quote(token)}/sendMessage'
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        data = urllib.parse.urlencode(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                return True
        return False
    except Exception:
        return False
```

## Integration Steps
1. **Create the file**  
   `C:\Users\khoans\Documents\Stock_OS\stock_vault\scripts\telegram_notify.py`  
   (or the equivalent path under the Hermes profile).

2. **Verify environment variables**  
   - `TELEGRAM_BOT_TOKEN` – token for the bot that will send messages.  
   - `TELEGRAM_ALLOWED_USERS` – comma‑separated list of Telegram user IDs allowed to receive messages.

3. **Confirm the correct bot is targeted**  
   - Tokens are stored per‑profile (e.g., `LUsineWorkBot/.env`).  
   - The first token found alphabetically is **not** guaranteed to be the intended bot.  
   - Hard‑code the correct profile path or manually verify with:  

   ```bash
   curl -s "https://api.telegram.org/bot<TOKEN>/getMe" | grep username
   ```

4. **Call from the pipeline**  
   ```python
   from telegram_notify import send_telegram
   if send_telegram("Your message here"):
       print("Telegram sent")
   else:
       print("Telegram send failed")
   ```

## Common Pitfalls & Fixes
- **Missing credentials** – The wrapper returns `False` silently; ensure the `.env` files are present and variables are spelled correctly.
- **Wrong bot token** – Auto‑discovery scans all `.env` files; verify the bot’s `username` via `getMe` before sending.
- **UTF‑8 encoding issues** – Never pass Vietnamese text through shell variables (`$MSG`). Use a Python here‑doc or read the message directly from `os.getenv`/files.
- **Orphaned `.bat` loops** – The wrapper is just a function; the calling script must manage its own execution context (e.g., via the Hermes cron watchdog).

## Checklist for Future Agents
- [ ] `telegram_notify.py` exists in `scripts/`.
- [ ] Environment variables are loaded before the first call.
- [ ] Token verification step is performed in any manual test.
- [ ] Code calls `send_telegram` and handles the Boolean return value.
- [ ] No hard‑coded token values appear in the source; all tokens come from environment.

---  
*This fix was introduced on 2026‑07‑18 after a stock‑capture run failed due to a missing `telegram_notify` module. The wrapper ensures graceful degradation and eliminates the hard crash, allowing the pipeline to continue or fail cleanly with a logged message.*