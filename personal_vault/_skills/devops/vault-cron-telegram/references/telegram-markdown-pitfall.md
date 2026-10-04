# Telegram Markdown 400 Pitfall (vault cron scripts)

## Symptom
A `no_agent` cron that calls `send_telegram(text)` returns:
```
TG_RESULT:FAIL|HTTP Error 400: Bad Request
```
but a plain-text message (no `_`) sends fine.

## Root cause
`vault/.scripts/_send_telegram.py` (and the warren-profile copy) hardcodes:
```python
data = urllib.parse.urlencode({'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'Markdown'}).encode()
```
Telegram's **legacy** `Markdown` parse mode treats `_` as an *italic* delimiter.
Ops messages contain file names with underscores — `OPERATION_INDEX`,
`12_Wage`, `14_Menu_GP_Monthly_Tracker`, `cron_receipts` — so the parser hits an
unmatched `_` and returns:
```
400 Bad Request: can't parse entities: Can't find end of the entity starting at byte offset 86
```
(byte offset points at the first `_` in the message).

## Debug recipe (get Telegram's REAL error)
The cron `error` string only says "Bad Request". To see the `description`, run a
temp script (NOT `python3 -c` — write a file, then clean up):
```python
import sys, urllib.request, urllib.parse, json, os
sys.path.insert(0, r"C:/Users/khoans/AppData/Local/hermes/profiles/warren-profile/scripts")
env_path = os.path.expanduser(r"~/AppData/Local/LUsineWorkBot/.env")
token = None
for line in open(env_path, "rb").read().decode("utf-8-sig").split("\n"):
    line = line.strip()
    if line.startswith("TELEGRAM_BOT_TOKEN=") and len(line) > 22:
        token = line[len("TELEGRAM_BOT_TOKEN="):]; break
text = "🔎 Vault Consistency — 2026-07-19\n🟡 orphan: Log file không có trong OPERATION_INDEX: README.md"
data = urllib.parse.urlencode({"chat_id": "2117653672", "text": text, "parse_mode": "Markdown"}).encode()
try:
    req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=data)
    print("OK", urllib.request.urlopen(req).read().decode()[:200])
except urllib.error.HTTPError as e:
    print("HTTP", e.code, e.read().decode()[:400])
```

## Fix — local plain-text sender (do NOT edit shared `_send_telegram.py`)
Add to the cron script (other crons depend on Markdown mode in the shared file):
```python
import os as _os, urllib.request, urllib.parse, json as _json
_ENV_PATH = _os.path.expanduser(r"~/AppData/Local/LUsineWorkBot/.env")
def _load_token():
    try:
        for line in open(_ENV_PATH, "rb").read().decode("utf-8-sig").split("\n"):
            line = line.strip()
            p = "TELEGRAM_BOT_TOKEN="
            if line.startswith(p) and len(line) > len(p) + 5:
                return line[len(p):]
    except Exception:
        return None
def send_telegram_plain(text):
    """Plain-text send (no parse_mode) — ops notifications contain '_' in file
    names which break Telegram legacy Markdown. Bulletproof for cron alerts."""
    token = _load_token()
    if not token:
        return {"ok": False, "error": "NO_TOKEN"}
    data = urllib.parse.urlencode({"chat_id": "2117653672", "text": text}).encode()
    try:
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage", data=data)
        return {"ok": True, "result": _json.loads(urllib.request.urlopen(req).read())}
    except Exception as e:
        return {"ok": False, "error": str(e)}
```
Use `send_telegram_plain(...)` everywhere in the cron; reserve Markdown mode for
human-formatted digests that intentionally use `_`/`*` as formatting.

## When this bites
Seen 2026-07-19 in `vault_consistency_nightly.py` after adding a heartbeat that
included `OPERATION_INDEX` in the finding text. First fix attempt (strip `*`
bold) still 400'd because `_` remained. Plain-text send resolved it.
