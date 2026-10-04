# capture-sleep root causes (concrete recipes)

Source: 2026-08 session debugging `telegram_health_poller.py` + `process_sleep.py`.

## Repro harness (mock side-effects, no real writes)
```python
import sys, io
from pathlib import Path
from unittest import mock
sys.path.insert(0, r"C:\Users\khoans\Documents\Personal_OS\personal_vault\scripts")
import telegram_health_poller as p

captured = []
def fake_send_msg(text, reply_to=None, chat_id=None):
    captured.append({"text": text, "reply_to": reply_to})
    return 999
p.send_msg = fake_send_msg

update = {"update_id": 1, "message": {
    "message_id": 777, "reply_to_message_id": None,
    "chat": {"id": 2117653672}, "from": {"id": 2117653672, "is_bot": False},
    "text": "[capture-sleep] Health log aug 09: 🏥 Health: 7h30 | quality 90 | 62kg | 20h | Huyết áp: 97/71",
}}
buf = io.StringIO(); old = sys.stdout; sys.stdout = buf
try: p.process_new_message(update)
finally: sys.stdout = old
print(buf.getvalue())
for c in captured: print(c)
```
Assert: `reply_to=None` on the Draft call → message shows standalone on Telegram.

## Root cause A — standalone "ok" dropped
`process_reply` matched only `reply_to_message_id == proposal_msg_id`. Bố typed
"ok" standalone (no reply thread) → `getUpdates` consumed the update → no match →
pending stuck forever. Fix: match reply OR standalone msg from Bố in same 1-1 chat
(normalize ok/skip variants; 30-min timeout auto-approve).
Telegram Bot API has NO `getChatHistory` (404) — never use it.

## Root cause B — draft sent as reply, invisible
`send_msg(draft, reply_to=message_id)` → landed as a reply, hidden on Telegram.
Bố saw the standalone test msg but not the draft. Fix: `send_msg(draft)` (no reply_to).
ACK can stay as reply (harmless).

## Root cause C — GSheet OAuth expired, silent skip
`get_credentials()` used InstalledAppFlow; refresh token expired →
`google.auth.exceptions.RefreshError: invalid_grant` → swallowed by try/except →
"sync GSheet" claimed but never happened. Fix: **Service Account** (long-lived).

### Service Account setup (Warren / personal vault)
1. GCP Console → project `warren-os` → IAM → Service Accounts → create
   `hermes-sleep-sync`, add Key (JSON).
2. Save JSON to `personal_vault/scripts/config/gsheet_sa.json` (git-ignored via `.gitignore: scripts/config/`).
3. In `google_api.py` `get_credentials()`, add branch: if SA json exists →
   `service_account.Credentials.from_service_account_file(path, scopes=[SHEETS])`.
   NOTE: `~/.hermes/profiles/.../google-workspace/scripts/google_api.py` is NOT git-tracked.
4. Share the GSheet (tab `W-capture-sleep`) with SA email `hermes-sleep-sync@warren-os.iam.gserviceaccount.com` as Editor.
5. Enable **Google Sheets API** for project `warren-os`.
Verify: `process_sleep.sync_to_gsheet()` returns rows>0; read-back shows the date.

## Cron window gotcha
`telegram-capture-sleep` schedule `*/2 6-13 * * *` → only 06:00–13:00.
Outside that, a manual force-run (`python telegram_health_poller.py --once`) is required;
do NOT tell Bố "auto" if he sent outside the window.
