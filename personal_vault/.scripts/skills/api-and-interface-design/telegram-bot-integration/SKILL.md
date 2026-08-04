---
name: telegram-bot-integration
description: Pattern for integrating aiogram 3.x Telegram bot with existing NL handler pipeline. Covers .env loading in .bat, VAULT_ROOT resolution, multi-profile deployment, and graceful degradation.
---

# Telegram Bot Integration Pattern (aiogram 3.x)

## Overview
Integrate aiogram 3.x polling bot with existing NL case management handler.
Reuses existing `handle_message()` function from `case_brain_nl_handler.py`.

## Architecture
```
Telegram → aiogram (polling) → handle_message() → existing NL pipeline
                              ↓
                        case_brain_nl_handler.py
                              ↓
                        case_followup_orchestrator.py
                              ↓
                        vault/scripts/ (single source of truth)
```

## Key Components

### 1. Bot File Structure
```
lusine_ops/
├── telegram_bot.py      # aiogram polling bot
├── vault_resolver.py    # VAULT_ROOT discovery
├── cli.py               # ops-cases entry point
├── commands/            # 9 command wrappers
└── case_brain_nl_handler.py  # NL handler (shared with vault)
```

### 2. Bot Code Pattern
```python
# telegram_bot.py
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# NL handler import
sys.path.insert(0, VAULT_SCRIPTS_PATH)
from case_brain_nl_handler import handle_message

async def handle_text(message: types.Message):
    if not is_allowed(message.from_user.id):
        return
    result = handle_message(message.text)
    if result:
        for chunk in [result[i:i+4000] for i in range(0, len(result), 4000)]:
            await message.answer(chunk, parse_mode=ParseMode.HTML)
    else:
        await message.answer("❓ Không hiểu cú pháp. Gõ /help để xem hướng dẫn.")
```

### 3. .env Loading in .bat (Critical)
```bat
@echo off
title L'Usine Telegram Bot
cd /d %SKILL_DIR%
set PYTHONPATH=%SKILL_DIR%;%VAULT_SCRIPTS%

:: Load .env file - REQUIRED for env vars
for /f "tokens=1,2 delims==" %%a in ('type "%LOCALAPPDATA%\LUsineBot\.env" ^| findstr /r /v "^#" ^| findstr "="') do set %%a=%%b

:loop
echo [%date% %time%] Starting bot...
python.exe -m lusine_ops.telegram_bot
echo [%date% %time%] Bot stopped. Restarting in 5s...
timeout /t 5 >nul
goto loop
```

### 4. VAULT_ROOT Resolution (Multi-Profile)
```python
# vault_resolver.py
def get_vault_root() -> Path:
    # 1. Explicit env var (for CI/override)
    if vault := os.environ.get("VAULT_ROOT"):
        return Path(vault)
    # 2. Known fixed location (current machine)
    known = Path(r"C:\Users\khoans\Documents\Warren_OS_Local\vault")
    if known.exists():
        return known
    # 3. Fallback: from skill location
    skill_root = Path(__file__).resolve().parents[1]
    candidate = skill_root / "vault"
    if candidate.exists():
        return candidate
    raise RuntimeError("VAULT_ROOT not found. Set VAULT_ROOT env var.")
```

### 5. .env File Format
```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ
TELEGRAM_ALLOWED_USERS=2117653672,987654321
```

### 6. Multi-Profile Deployment
```bash
# install_all_profiles.sh
for profile in warren-profile lusine-profile personal_profile; do
    hermes skill install . --profile "$profile"
done
```

## Multi-Profile Deployment Pattern
- Single vault (shared source of truth)
- 3 profiles: warren-profile, lusine-profile, personal_profile
- Each profile has its own skill copy
- PYTHONPATH in .bat: `skill_dir;vault_scripts_dir`
- Skill is thin wrapper → vault/scripts is single source of truth

## Graceful Degradation Patterns

### Optional Dependencies
```python
try:
    from push_gcal import load_env, get_calendar_service
    _CALENDAR_AVAILABLE = True
except ImportError:
    _CALENDAR_AVAILABLE = False

def calendar_feature():
    if not _CALENDAR_AVAILABLE:
        print("[WARN] Google Calendar not available")
        return
    # ... use calendar
```

### .env Loading
```python
# In code - use python-dotenv or manual loading
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent.parent / "LUsineBot" / ".env")
```

## Testing Checklist
- [ ] `ops-cases` CLI works in all 3 profiles
- [ ] Telegram bot starts without .env errors
- [ ] NL commands work: `[new case] test`, `[update case ...]`, etc.
- [ ] Slug generation handles Vietnamese correctly
- [ ] All 30 tests pass (8+8+7+6)
- [ ] Bot restarts after crash (auto-restart loop)

## Stack Startup Order (2026-06-26)

The full L'Usine stack has a service dependency chain. See `references/lusine-stack-startup.md` for the complete procedure and `Khoi Dong LUsine Stack.bat` on Desktop.

**Short version:** Ollama → wait 30s → Qdrant → wait 5s → Hermes Gateway → wait 3s → L'Usine Work Bot. Skipping Qdrant causes Mem0 `No connection (10061)`.

## Key Pitfalls Avoided
1. **VAULT_ROOT resolution** - Hardcoded path + env override
2. **.env loading in .bat** - Required for Windows service
3. **PYTHONPATH in .bat** - skill_dir + vault_scripts_dir
4. **Python cache clearing** - Required after code changes
5. **Process restart** - Long-running bot must be killed/restarted
6. **Multi-profile sync** - Copy skill to all 3 profiles
7. **WinError 64 transient noise** - Windows TCP drops trigger ERROR logs in aiogram polling. Bot self-heals. See `references/windows-winerror64-aiogram.md` for logging filter fix + verification.
8. **WinError 10106 Winsock LSP failure** - On company-managed Windows laptops, subprocess-spawned bot may crash with `import _overlapped` failing. Direct terminal execution works. Workaround: use `terminal(background=true)` with inline Python env loading. See `references/windows-winerror10106-winsock.md`.
9. **MSYS path mangling with `cmd /c "start ..."`** — When launching the bot `.bat` via `cmd /c` from bash/MSYS, paths containing backslashes get mangled: `C:\Users\...` becomes `C:Users...` (backslashes stripped). This causes the `.bat` launcher to fail silently because `start /min "" "C:\Users\..."` points to a non-existent path.
   **Fix:** Use Python subprocess.Popen with native Windows paths instead:
   ```python
   import subprocess
   bat_path = r"C:\Users\khoans\AppData\Local\LUsineWorkBot\start_bot.bat"
   proc = subprocess.Popen(
       ['cmd', '/c', bat_path],
       cwd=r'C:\Users\khoans\Documents\Warren_OS_Local\vault\scripts\lusine-ops',
       creationflags=subprocess.CREATE_NO_WINDOW,
   )
   ```
   Or directly run the Python bot module from Python subprocess, bypassing the `.bat` entirely.
10. **Pydantic version conflict (aiogram import fails)** — When the Hermes agent venv's pydantic version differs from Python 3.12 site-packages, importing aiogram from a bash-spawned process may fail with `ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'`. This happens because sys.path picks up the wrong pydantic. **Fix:** Ensure the bot runs from a clean environment by using the `.bat` launcher (which sets PYTHONPATH correctly) or explicitly set `PYTHONPATH` to exclude the Hermes venv. The Hermes `terminal(background=true)` may inherit the agent's venv paths — verify with `import sys; print(sys.path)` before launching.

## Lazy Import Fallback (Extending handle_message)

When adding a new feature that should handle messages NOT matching existing prefixes, use lazy import to avoid hard dependency:

```python
def handle_message(text, *, dry_run=False):
    prefix, query, payload = detect_prefix(text)
    
    # Fallback: try new handler before giving up
    if not prefix:
        try:
            from new_feature_handler import handle_new_feature
            result = handle_new_feature(text)
            if result:
                print(result)
                send_telegram(result)
                return result
        except ImportError:
            pass  # Feature not deployed yet — graceful degradation
        return None
    
    # ... existing case handling ...
```

**Key properties:**
- Import happens at call time, not module load → new handler files work without restart (first unrecognized message triggers import)
- `ImportError` caught silently → bot doesn't crash if handler file missing
- BUT: if `handle_message()` ITSELF was patched (not just the imported module), bot restart IS required (bot loaded old `handle_message` at startup)

**Pitfall:** Long-running polling bots cache imported modules in memory. Patching `handle_message()` body requires:
1. `taskkill /PID <bot_pid> /F`
2. Restart via `.bat` auto-restart loop
3. Verify with `getMe` + test message

### Bot Restart (Windows)

```bash
# Find Python312 process (bot uses Python 3.12)
python3 -c "import subprocess; r=subprocess.run(['wmic','process','where','name=\"python.exe\"','get','processid,executablepath','/format:csv'],capture_output=True,text=True,shell=True); [print(l) for l in r.stdout.split('\n') if 'Python312' in l]"

# Kill
cmd //c "taskkill /PID <PID> /F"

# Restart (auto-restart loop in .bat picks up)
# Or manually: bash /c/Users/khoans/start_bot.sh
```

### Troubleshooting: Bot Not Responding

When the user reports "bot không phản hồi", diagnose systematically:

**Step 1 — Process health check (quickest)**
```bash
wmic process where "name='python.exe'" get ProcessId,CommandLine | findstr "telegram_bot"
# Empty → bot process dead. Not empty → bot is running.
```

**Step 2 — Check recent logs**
Look for the last timestamps in the bot's console output or agent log. If the last log was a `WinError 64` and the process is dead, the bot crashed after reconnect. If logs show successful message processing but no response, the handler is broken (not the network).

**Step 3 — Action by finding**

| Finding | Action |
|---------|--------|
| Process dead → | Restart bot (see Bot Restart section). If using .bat launcher, it auto-restarts — check if .bat is being used. |
| Process alive but unresponsive → | Kill + restart. Could be handler deadlock or queue corruption. |
| WinError 64 in logs → | Apply TransientNetworkFilter (see `references/windows-winerror64-aiogram.md`). Note: the process CAN die after WinError 64, not just the connection. |

**Step 4 — Prevent recurrence**
- Prefer **Python wrapper launcher** (`start_bot.py`) over `.bat` launcher when watchdog is in place. Python wrapper is detached, no auto-restart loop, controlled by cron.
- Keep the `.bat` launcher with `:loop` only for standalone deployment (no watchdog).
- Add TransientNetworkFilter to reduce noise (already done for L'Usine Work Bot).
- Set up a Hermes cron watchdog (`no_agent=True`, every 5m) as second-chance restart. See `references/windows-bot-watchdog.md`.

### ⚠️ WMIC Self-Referential Matching (Hermes Terminal Debugging)

When checking bot process health FROM a Hermes terminal command, the wmic query itself can match the running terminal command:

```bash
# BAD — the wmic query string is in this command's own argv!
wmic process where "(CommandLine like '%lusine_ops.telegram_bot%')" get ProcessId
# → bash.exe processes contain this literal query string in their command line
# → Returns false positives (counts Hermes terminal processes as "bot instances")
```

**Fix: Use PowerShell `Get-CimInstance` for accurate detection from Hermes terminal:**

```bash
powershell -Command "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { \$_.CommandLine -like '*lusine_ops*' } | Select-Object ProcessId,CreationDate | Format-Table -AutoSize"
```

**Why:**
- WMIC matches any process where ANY part of CommandLine contains the string
- The Hermes terminal's own bash command includes the wmic query text
- PowerShell has separate filter vs projection — avoids self-match
- Use `Where-Object` to filter AFTER getting results, not as part of the query string

**Alternative (no false positives):** Use `findstr` to filter wmic output:
```bash
wmic process where "name='python.exe'" get ProcessId,CommandLine | findstr "lusine_ops"
# Only matches python.exe command lines, not the bash parent
```

### ⚠️ Critical Pitfall: Orphan `.bat` Launcher Resurrection

When a `.bat` launcher with `:loop` is started via `start` command, it creates a persistent cmd.exe window. Killing `python.exe` does NOT kill the cmd window — the `:loop` immediately spawns a new python.exe after `timeout /t 5`. This creates an **infinite spawn loop** that survives all python.exe kills.

**Scenario:**
1. You run `cmd.exe /c "start start_bot.bat"` — opens new cmd window
2. Bot dies (e.g., WinError 64) → `.bat` loop spawns new instance after 5s
3. You kill all python.exe bot processes → `.bat` loop spawns them again
4. New instances keep appearing despite kill commands

**Fix: Kill the cmd.exe root, not just the python.exe leaves**
```bash
# Step 1: Find the orphan cmd.exe
powershell -Command "Get-CimInstance Win32_Process -Filter \"Name='cmd.exe'\" | Where-Object { \$_.CommandLine -like '*start_bot*' } | Select-Object ProcessId,CommandLine"

# Step 2: Kill it (WMI, not taskkill — avoids MSYS path conversion)
wmic process where "ProcessId='<PID>'" delete

# Step 3: Then kill all bot processes
wmic process where "(CommandLine like '%lusine_ops.telegram_bot%')" delete

# Step 4: Verify both are gone
powershell -Command "Get-CimInstance Win32_Process -Filter \"Name='cmd.exe'\" | Where-Object { \$_.CommandLine -like '*start_bot*' } | Select-Object ProcessId"
wmic process where "(CommandLine like '%lusine_ops.telegram_bot%')" get ProcessId
```

**Prevention:** Use Python wrapper launcher instead of .bat for watchdog-managed setups (see skill `§Hermes Cron Watchdog Pattern (Windows)` below).

### Python Wrapper Launcher Pattern (Watchdog-Managed)

For bots managed by Hermes cron watchdog, use a Python wrapper instead of .bat `:loop`:

> **Non-admin Windows (corporate laptops):** If subprocess-spawned bots crash with WinError 10106 (Winsock LSP failure), use `launch_bot.py` — a standalone Python script that loads `.env` internally (no `-m`, no `subprocess`). Deploy via:
> 1. Drop `launch_bot.py` in the app's local data dir
> 2. Create a `.bat` in `%APPDATA%\\...\\Startup\\` that calls `pythonw.exe launch_bot.py`
> 3. On logon → bot starts silently, no console window
> 4. `schtasks /create` is often blocked on corporate laptops → Startup folder is the zero-friction fallback
> 
> See `references\\windows-winerror10106-winsock.md` for detection + workaround.

**Preferred launch method (avoids MSYS path mangling and orphan cmd windows):**

From Hermes terminal, use Python `subprocess.Popen` directly — this avoids both `cmd /c` path mangling (pitfall #9) and orphan `.bat` loops:

```python
import subprocess, os
from pathlib import Path

ENV_PATH = Path(r"C:\Users\khoans\AppData\Local\LUsineWorkBot\.env")
BOT_DIR = r"C:\Users\khoans\Documents\Warren_OS_Local\vault\scripts\lusine-ops"
PYTHON = r"C:\Users\khoans\AppData\Local\Programs\Python\Python312\python.exe"

# Load .env vars
env = os.environ.copy()
for ln in open(ENV_PATH, encoding='utf-8-sig'):
    ln = ln.strip()
    if ln and not ln.startswith('#') and '=' in ln:
        k, v = ln.split('=', 1)
        env[k.strip()] = v.strip()
env['PYTHONPATH'] = r'C:\Users\khoans\Documents\Warren_OS_Local\vault\scripts'

# Launch as detached process
proc = subprocess.Popen(
    [PYTHON, '-m', 'lusine_ops.telegram_bot'],
    cwd=BOT_DIR, env=env,
    creationflags=subprocess.CREATE_NO_WINDOW,
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
)
print(f'Bot launched: PID={proc.pid}')
```

This approach:
- Avoids MSYS path mangling (paths stay in native Windows format)
- Avoids orphan `cmd.exe` windows and infinite `.bat` loops
- Captures stderr (or discards cleanly via DEVNULL)
- Works from Hermes terminal, `execute_code`, or cron scripts

```python
# start_bot.py — loads .env + starts bot as detached process
import os, subprocess
from pathlib import Path

ENV_PATH = Path(r"C:\Users\khoans\AppData\Local\LUsineWorkBot\.env")
BOT_DIR = Path(r"C:\Users\khoans\Documents\\path\\to\\scripts\\lusine-ops")
PYTHON = r"C:\Users\khoans\AppData\Local\Programs\Python\\Python312\\python.exe"

def load_env(env_path):
    env = os.environ.copy()
    with open(env_path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env

def start_bot():
    env = load_env(ENV_PATH)
    env["PYTHONPATH"] = str(BOT_DIR.parent)
    proc = subprocess.Popen(
        [PYTHON, "-m", "lusine_ops.telegram_bot"],
        cwd=str(BOT_DIR), env=env,
        creationflags=subprocess.CREATE_NO_WINDOW,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return proc
```

**No `:loop`** — the watchdog handles restarts. This avoids orphan cmd windows and infinite spawn loops.

### Hermes Cron Watchdog Pattern (Windows)

For auto-restart when process dies:

```python
# watchdog_lusine_bot.py — runs as no_agent=True cron job
# Silent when bot is alive; delivers notification only on restart

def is_bot_running() -> bool:
    result = subprocess.run(
        ['wmic', 'process', 'where', '(CommandLine like "%lusine_ops.telegram_bot%")', 'get', 'ProcessId'],
        capture_output=True, text=True, timeout=15
    )
    pids = [l for l in result.stdout.split() if l.isdigit()]
    return len(pids) >= 1

def restart_bot():
    subprocess.Popen([PYTHON, str(LAUNCHER)],
        creationflags=subprocess.CREATE_NO_WINDOW,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

Cron job config: `every 5m`, `no_agent=True`, `script=watchdog_lusine_bot.py`, deliver=`local`.

Warren runs 3 separate Telegram bots, each with its own token in `%LOCALAPPDATA%`:

| Directory | Token in | Bot username |
|:--|:--|:--|
| `LUsineBot/.env` | `TELEGRAM_BOT_TOKEN=...` | `@HORION910bot` |
| `LUsineWorkBot/.env` | `TELEGRAM_BOT_TOKEN=...` | `@lusine_work_bot` |
| `LUsinePersonalBot/.env` | `TELEGRAM_BOT_TOKEN=...` | `@personal_life_bot` |

**Critical pitfall:** When Hermes auto-discovers a bot token by scanning for `.env` files with `TELEGRAM_BOT_TOKEN`, the first alphabetical match may be the WRONG bot. Always verify before sending.

### Discovery + Verification Pattern

```bash
# Step 1: Find ALL bot configs
find /c/Users/khoans/AppData/Local -maxdepth 2 -name ".env" -type f \
  | xargs grep -l "TELEGRAM_BOT_TOKEN" 2>/dev/null

# Step 2: Verify each bot's identity via getMe
for token in $(grep -h "TELEGRAM_BOT_TOKEN" /c/Users/khoans/AppData/Local/LUsine*/.env | cut -d= -f2); do
  curl -s "https://api.telegram.org/bot${token}/getMe" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('result',{}).get('username','INVALID'))"
done

# Step 3: Always verify BEFORE sending
TOKEN=***
curl -s "https://api.telegram.org/bot${TOKEN}/getMe" | grep -o '"username":"[^"]*"'
# Must match expected bot username before proceeding
```

### Why This Matters

- Names are similar: `LUsineBot`, `LUsineWorkBot`, `LUsinePersonalBot`
- Directory scanning is order-dependent (alphabetical)
- Token extraction via `grep TELEGRAM_BOT_TOKEN` returns first match
- **Always hardcode the bot source** in skill config — never auto-discover at runtime
- For `ops-review-response`: token source is explicitly `LUsineWorkBot/.env` (bot: `@lusine_work_bot`)

---

## 🚀 Ready-to-Run Send Script (Hermes → Warren DM)

When Warren asks "gửi telegram cho tôi" with a message + optional file attachment, use this. Source bot = **`@lusine_work_bot`** (token in `LUsineWorkBot/.env`, NOT `LUsineBot`/`LUsinePersonalBot`).

**CRITICAL: UTF-8 pitfall.** Never pass Vietnamese text via shell `$MSG` variable + `curl --data-urlencode` — Telegram rejects with `400 Bad Request: strings must be encoded in UTF-8` because MSYS/bash mangle the encoding. Always send via a Python `here-doc` that reads `.env` and posts with `urllib` (UTF-8 native).

```python
# send_telegram.py — run via: python3 send_telegram.py
import os, json, urllib.request, urllib.parse
from pathlib import Path

ENV = Path(r"C:/Users/khoans/AppData/Local/LUsineWorkBot/.env")
env = {}
for ln in open(ENV, encoding="utf-8-sig"):
    ln = ln.strip()
    if ln and not ln.startswith("#") and "=" in ln:
        k, v = ln.split("=", 1); env[k.strip()] = v.strip()
TOKEN = env["TELEGRAM_BOT_TOKEN"]
CHAT = env["TELEGRAM_ALLOWED_USERS"].split(",")[0].strip()

def post(url, data=None, files=None):
    if files:
        boundary = "----hermesbot"; parts = []
        for k, v in data.items():
            parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode("utf-8"))
        for k, fp in files.items():
            fn = os.path.basename(fp)
            parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"; filename=\"{fn}\"\r\nContent-Type: application/octet-stream\r\n\r\n".encode("utf-8"))
            parts.append(open(fp,"rb").read()); parts.append(b"\r\n")
        parts.append(f"--{boundary}--\r\n".encode("utf-8"))
        req = urllib.request.Request(url, data=b"".join(parts), headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
        return json.loads(urllib.request.urlopen(req, timeout=30).read().decode("utf-8"))
    data = urllib.parse.urlencode(data).encode("utf-8")
    return json.loads(urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=30).read().decode("utf-8"))

base = f"https://api.telegram.org/bot{TOKEN}"
MSG = "your Vietnamese text here"
print(post(f"{base}/sendMessage", {"chat_id": CHAT, "text": MSG}))
# With file: post(f"{base}/sendDocument", {"chat_id": CHAT}, {"document": r"C:/path/to/file.md"})
```

**Verify-then-send (mandatory):** Always `curl -s "https://api.telegram.org/bot${TOKEN}/getMe"` → confirm `username: lusine_work_bot` BEFORE posting. Token auto-discovery by directory scan returns wrong bot (alphabetical first match). Hardcode `LUsineWorkBot/.env`.

**ZONE 🔴 gate for vault data changes:** Deleting/modifying queue files (`review_queue.json`, `col_queue.json`) or appending to GSheets = ZONE 🔴. Ask 2 gate questions BEFORE executing, even if Warren says "xóa đi"/"append đi" (those = prepare, not execute). See Warren memory correction 2026-07-17.

**Ready script:** `references/send_telegram_warren.py` — copy + run `python3 send_telegram_warren.py "msg" [file]`.

## Extending the Bot with Custom Data Handlers

When you need the bot to accept structured data messages (e.g. `"LU5 tối: 14"` for Quick Wins tracking) IN ADDITION to NL case commands, use the **handle-before-NL** pattern instead of modifying the NL handler.

### Architecture

```
Telegram → handle_text()
              │
              ├─ Quick Wins handler (parse + write to Google Sheets)
              │     → returns response string if matched
              │     → returns None if not a tracking message
              │
              └─ NL case handler (existing pipeline)
                    → [new case], [update case], etc.
```

### Pattern

```python
# In telegram_bot.py handle_text(), BEFORE the NL handler call:

# 1. Try quick wins handler first
from quick_wins_handler import handle_quick_wins_message

async def handle_text(message):
    text = message.text or ""
    
    # Quick Wins intercept — runs before NL pipeline
    qw_result = handle_quick_wins_message(text)
    if qw_result:
        await message.answer(qw_result, parse_mode=ParseMode.HTML)
        return
    
    # Fall through to NL handler (unchanged)
    result = handle_message(text)
    ...
```

### Handler Module Structure

Create a separate `.py` file in the same package as `telegram_bot.py`. Structure:

```
lusine_ops/
├── telegram_bot.py
├── quick_wins_handler.py   # <-- new handler module
├── ...
```

Key design principles:
1. **Self-contained** — the handler has its own `parse_message()` and `update_sheet()` functions
2. **Returns None for non-matching messages** — the bot falls through to the next handler
3. **Returns an HTML response string for matched messages** — sent directly as the bot reply
4. **Lazy dependencies** — Google API imports happen inside the handler, not at module load

### Message Parsing: Vietnamese Diacritics

When parsing Vietnamese text from Telegram messages, `\w+` in regex correctly matches characters with diacritics (tối, sáng, chiều). However, the matched value (e.g. `"tối"`) will NOT match a dict key `"toi"` (ASCII).

**Fix:** Normalize before dict lookup:

```python
# Character map for common Vietnamese diacritics
_VIETNAMESE_MAP = {
    'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
    'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
    'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
    'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
    'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
    'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
    'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
    'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
    'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
    'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
    'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
    'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
    'đ': 'd',
}

def strip_vietnamese_diacritics(text: str) -> str:
    return ''.join(_VIETNAMESE_MAP.get(c, c) for c in text)
```

### Structured Message Parsing Pattern

```python
import re

METRIC_ALIASES = {
    "toi": "Sunset Hour", "sunset": "Sunset Hour",
    "lunch": "POWER LUNCH", "power": "POWER LUNCH",
    "sang": "Morning Kickstart", "morning": "Morning Kickstart",
    "grab": "GrabFood", "grabfood": "GrabFood",
    "upsell": "Staff Upsell",
}

def parse_message(text: str) -> Optional[dict]:
    """Parse 'STORE metric: number' → {store, metric, value, label}"""
    m = re.match(
        r"(LU[357])\s+(\w+)\s*[:\-]?\s*(\d+\.?\d*)",
        text.strip(), re.IGNORECASE | re.UNICODE,
    )
    if not m:
        return None
    store = m.group(1).upper()
    metric_raw = m.group(2).lower().strip()
    metric_normalized = strip_vietnamese_diacritics(metric_raw)
    label = METRIC_ALIASES.get(metric_normalized)
    if not label:
        return None
    return {"store": store, "metric": metric_normalized, "value": int(float(m.group(3))), "label": label}
```

### Google Sheets Write Pattern (via Service Account)

For writing parsed data to Google Sheets from the bot:

```python
from google.oauth2 import service_account
from googleapiclient.discovery import build

SA_KEY = Path(os.environ["LOCALAPPDATA"]) / "hermes" / "google_service_account.json"
SHEET_ID = "1ZtIocc_Ic1z-tO1JGd4ZLnRB_7ZHHkvpJ5emaWJyeEE"

creds = service_account.Credentials.from_service_account_file(
    str(SA_KEY), scopes=["https://www.googleapis.com/auth/spreadsheets"])
service = build("sheets", "v4", credentials=creds)

# Write a single cell
body = {"values": [[14]]}
service.spreadsheets().values().update(
    spreadsheetId=SHEET_ID,
    range="'Quick Wins Tracker'!C3",  # tab!ColumnRow
    valueInputOption="RAW", body=body,
).execute()
```

**Pitfall:** The SA key can read/write EXISTING sheets but CANNOT create new spreadsheets (needs Drive API scope which this SA doesn't have). Solution: add new tabs to the existing LU_COL_ENGINE_V4 sheet which the SA has access to, or use OAuth to create new sheets.

### Registering Custom Commands

New slash commands (e.g. `/summary`) need three changes:

1. **Define handler function** in `telegram_bot.py`:
```python
async def cmd_summary(message: types.Message) -> None:
    if not is_allowed(message.from_user.id):
        return
    summary = get_summary()
    await message.answer(summary, parse_mode=ParseMode.HTML)
```

2. **Register in `main()`**:
```python
dp.message.register(cmd_summary, Command("summary"))
```

3. **Update /start message** to document the new command

### Multi-Format Message Parser (Template + Single Line)

For handlers that need to accept BOTH single-line messages (`"LU5 tối: 14"`) AND multi-line formatted templates (emoji + `[value]`), implement a **two-pass dispatch**:

```python
def handle_quick_wins_message(text: str) -> Optional[str]:
    # Pass 1: Try template format (looks for [value] brackets)
    parsed_list = parse_template(text)
    if parsed_list:
        results = [update_sheet(p) for p in parsed_list]
        return "\n".join(results)
    
    # Pass 2: Fall back to single line format
    parsed = parse_message(text)  # uses regex + Vietnamese diacritics
    if not parsed:
        return None
    return update_sheet(parsed)
```

**Why template first?** The `[value]` bracket pattern is unique to templates — single-line messages won't have brackets. This avoids false positives.

The template parser uses a display-label → (store, metric) mapping. Labels must be lowercase and matched as substrings (e.g. `"sunset hour lu5"` matches `"🌅 Sunset Hour LU5: [14] / 14"` after stripping emoji). See `references/custom-data-handler-pattern.md` for the full parser implementation.

### Testing Checklist for New Handlers

- [ ] Regex parses all expected message variants (`LU5 tối: 14`, `LU5 tối 14`, `lu3 lunch 8`)
- [ ] Vietnamese diacritics normalize to correct ASCII keys
- [ ] Handler returns None for non-matching messages (doesn't block NL pipeline)
- [ ] Handler returns HTML string for matched messages
- [ ] Sheet write lands in correct cell (verify via sheet UI)
- [ ] /summary command reads back today's values
- [ ] Bot restarts cleanly after killing old process
- [ ] .bat launcher works (auto-restart loop)