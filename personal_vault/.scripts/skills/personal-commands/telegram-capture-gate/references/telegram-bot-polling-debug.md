# Telegram Bot Polling Debug — Real Session Recipe (2026-07-31)

Condensed from a 30+ turn debug where "Bố gửi ok mà bot ko thấy" turned out to be
a SECOND process consuming the bot's updates, NOT poller logic.

## Hard facts (non-negotiable)
- Telegram Bot API has NO `getChatHistory`. Calling it → `HTTP 404: Not Found`.
  Bot API only: `getUpdates` (long-poll) + webhooks. User-account history is MTProto only.
- Multiple processes calling `getUpdates` with the SAME bot token → Telegram
  round-robins updates between them. One consumer starves the others.
  → Only ONE consumer per bot token. Ever.
- `getUpdates(offset=0)` returns ONLY un-consumed updates. If it returns 0 but the
  user insists they sent a message, another process already ate it.

## Diagnosis sequence (run in order)
```powershell
# 1. Confirm token valid + which bot
python -c "import urllib.request,json; ... getMe ..."

# 2. Count un-consumed updates
#    getUpdates(offset=0, timeout=0, limit=50) -> result[]
#    COUNT=0 but user sent? -> ANOTHER PROCESS consumed it.

# 3. Find who holds Telegram TCP connections
netstat -ano | findstr "149.154"
#   e.g. TCP 10.28.15.82:51551  149.154.166.110:443  ESTABLISHED  27076

# 4. Resolve PID -> command line
powershell -Command "Get-CimInstance Win32_Process -Filter 'ProcessId = 27076' | Select-Object ProcessId,CommandLine"
#   -> C:\...\pythonw.exe C:\...\LUsineWorkBot\launch_bot.py  (or any script using the token)

# 5. Check if that script shares the bot token
#    grep TELEGRAM_BOT_TOKEN in its .env / source
```

## Fix options (pick one)
- Kill the duplicate consumer (if it's a stray script).
- Give the capture-sleep poller its OWN bot token (separate @BotFather bot).
- Switch the poller to webhook mode (`setWebhook`) — webhooks deliver each update
  exactly once, no round-robin race.

## Verify gate discipline
- Ad-hoc verify scripts that stub `tg_api` / `getUpdates` give FALSE PASS.
- Must hit the REAL Telegram API (getMe / getUpdates) to claim verification.
- Resetting `offset.json` to `{"offset":0}` only helps if updates are un-consumed;
  if already eaten, reset is useless — kill the competing process first.
