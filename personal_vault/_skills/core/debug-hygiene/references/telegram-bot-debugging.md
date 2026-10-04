# Telegram capture-sleep poller — debugging recipe

Concrete recipe for debugging `telegram_health_poller.py` (Personal_OS vault) without
dirtying real state. Earned from 2026-08 capture-sleep incident.

## Files
- Poller: `personal_vault/scripts/telegram_health_poller.py`
- Runner (cron): `~/.hermes/scripts/telegram_capture_sleep_runner.py` → calls poller `--once`
- Token: `C:/Users/khoans/AppData/Local/LUsinePersonalBot/.env` (TELEGRAM_BOT_TOKEN=)
- State: `scripts/.telegram_offset.json`, `scripts/.telegram_pending.json`

## Hard rules
1. NEVER call `write_vault` / `send_msg` / `sync_and_commit` FOR REAL during debugging.
   Use `unittest.mock.patch` on `send_msg` + `io.StringIO` to capture call args.
   Real test writes create fake vault entries → break `is_duplicate` → real messages dropped.
2. After any manual real write, `git checkout -- 10_PULSE/051_Sleep_Log.md` to restore.

## Diagnosis steps (real, read-only)
```python
import sys; from pathlib import Path
sys.path.insert(0, r'C:\Users\khoans\Documents\Personal_OS\personal_vault\scripts')
import telegram_health_poller as p

# 1. What offset is the poller using? (load_offset reads .telegram_offset.json)
print("load_offset:", p.load_offset())

# 2. What is actually in the Telegram queue right now?
ups = p.get_updates(0)
for u in ups:
    m = u.get("message", {})
    print(u["update_id"], m.get("message_id"), repr((m.get("text") or "")[:60]))

# 3. Is there a pending proposal?
print("pending:", p.load_pending())

# 4. Did send_msg actually fire? (MOCK it — no real send)
from unittest import mock
captured = []
with mock.patch.object(p, "send_msg", lambda text, reply_to=None, chat_id=None: captured.append((reply_to, text[:40])) or 999):
    p.process_new_message({"message": {"message_id": 259, "chat": {"id": 2117653672},
        "from": {"id": 2117653672, "is_bot": False},
        "text": "[capture-sleep] Health log aug 09: 🏥 Health: 8h00 | quality 90 | 62kg | 20h | Huyết áp: 97/71"}})
print("captured send_msg calls:", captured)
```

## Root causes found (2026-08)
- **Standalone "ok"**: Bố typed "ok" NOT as reply → `process_reply` only matched
  `reply_to_message_id` → update consumed + dropped. Fix: match standalone msg in same 1-1 chat.
- **Draft sent as reply_to**: `send_msg(draft, reply_to=msg_id)` → draft hidden under Bố's
  message on Telegram → Bố "didn't see reply". Fix: `send_msg(draft)` standalone.
- **Offset too high**: stale `.telegram_offset.json` (e.g. 581691583) makes `get_updates`
  skip new messages. Reset file to `{"offset": 0}` then re-run — but reset BEFORE the
  `--once` call, not in the same chained command that the poller then overwrites.
- **Duplicate masking**: fake entry from a real test `write_vault` made real message
  `is_duplicate` → silently dropped.

## Verify, don't claim
After a real sync: read back GSheet (date present?), grep vault (`### DATE`), confirm
`send_msg` returned int > 0. If you only ran the code, say "not yet verified".
