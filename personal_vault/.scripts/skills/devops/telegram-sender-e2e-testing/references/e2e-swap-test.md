# E2E Swap-Test for no_agent Telegram Queue Senders

> Pattern for safely testing a `no_agent=True` script that reads a shared queue file (e.g. `review_telegram_sender.py`) and sends to Telegram, WITHOUT touching live data.

## Why
These scripts mutate shared state (queue file) and call the Telegram API. Running them against the live queue risks sending test messages to Warren's real chat AND corrupting real review entries. The swap-test isolates the script against a disposable queue.

## Recipe (Windows / git-bash)

```bash
cd "$LOCALAPPDATA/hermes/profiles/warren-profile"

# 1. Backup live queue
Q="C:/Users/khoans/Documents/Warren_OS_Local/vault/_inbox/review_queue.json"
cp "$Q" /tmp/review_queue_backup.json

# 2. Build a minimal TEST queue (one entry with the fields the script reads)
python3 - << 'PYEOF'
import json, os
tmp = os.path.join(os.environ['TEMP'], 'test_queue.json')
test = {
  "pending": [{
    "id": "TEST-E2E",
    "status": "pending",
    "raw_text": "test",
    "source": "Telegram",
    "received_at": "2026-07-26T08:00:00",
    "platform": "google",
    "store": "LU3",
    "reviewer": "E2E Test",
    "rating": 2,
    "path": "Path 1 Complaint",
    "approval_message": "APPROVAL TEST - ignore",
    "insight_message": "## Review Insight - 2026-07-26 08:00\n- Sentiment: 1 Negative\n- Negative rate: 100% (crisis)\n- Store LU3: 1 review, avg 2.0"
  }],
  "history": []
}
json.dump(test, open(tmp,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
print("TEST QUEUE at", tmp)
PYEOF

# 3. Swap: move live aside, put test in place
mv "$Q" /tmp/review_queue_real.json
cp "$LOCALAPPDATA/../Temp/test_queue.json" "$Q"

# 4. Run the script
python3 scripts/review_telegram_sender.py
echo "EXIT=$?"

# 5. Verify state
python3 -c "
import json
d=json.load(open(r'$Q',encoding='utf-8'))
e=d['pending'][0]
print('status:',e.get('status'))
print('sent_at:',e.get('sent_at'))
print('insight_sent_at:',e.get('insight_sent_at'))
print('approval_message removed:', 'approval_message' not in e)
print('insight_message removed:', 'insight_message' not in e)
"

# 6. Restore live queue, clean up
mv /tmp/review_queue_real.json "$Q"
rm -f "$LOCALAPPDATA/../Temp/test_queue.json" /tmp/review_queue_backup.json
```

## Verify delivery
Webhook-configured bots return empty `getUpdates`, so do NOT rely on it. Instead send a tiny confirmation ping and check the API response:

```python
import os, urllib.request, urllib.parse, json
p = os.path.join(os.environ['LOCALAPPDATA'],'LUsineWorkBot','.env')
token = next(line[len('TELEGRAM_BOT_TOKEN='):] for line in open(p,encoding='utf-8')
             if line.strip().startswith('TELEGRAM_BOT_TOKEN=') and len(line.strip())>30)
chat = "2117653672"
data = urllib.parse.urlencode({"chat_id":chat,"text":"[E2E OK] test"}).encode()
req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=data)
res = json.loads(urllib.request.urlopen(req, timeout=15).read())
print("ok:", res.get("ok"), "msg_id:", res.get("result",{}).get("message_id"))
# Expect: ok: True, msg_id: <int>  -> message actually delivered
```

## New Telegram field via no_agent forwarder (pattern)
To add ANY new LLM-generated content that must reach Telegram (insight block, digest, alert):
1. LLM writes content into a NEW queue field (e.g. `insight_message`) — never gets the token.
2. Extend the no_agent sender: scan that field when `<field>_sent_at` absent → `send_telegram()` → stamp `<field>_sent_at` + `<field>_message_ids` → pop the field.
3. Silent when the field is absent (no NOOP spam).

This preserves the "LLM cron never sends Telegram" invariant from `ops-review` skill architecture.
