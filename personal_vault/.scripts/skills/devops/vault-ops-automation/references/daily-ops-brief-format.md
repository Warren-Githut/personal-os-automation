# Daily Ops Brief — Telegram Format

> Warren-approved format (2026-06-30). Gửi mỗi sáng 09:30 qua lusine_work_bot.

## ⚠️ Important: File Auto-Sent by Script

`generate_today_revenue.py` tự động gửi `today.md` dưới dạng file đính kèm qua Telegram (với caption basic "📋 Today Revenue & COL — DD/MM/YYYY"). Agent **không cần gửi lại file** — chỉ gửi phân tích caption riêng.

## Delivery Pattern

2 Telegram messages, gửi riêng:
1. **📎 File (tự động):** `today.md` — gửi bởi `generate_today_revenue.py` (caption: "📋 Today Revenue & COL — DD/MM/YYYY")
2. **📝 Caption (agent gửi):** HTML rich text — phân tích + calendar + weekly focus

→ Gửi message riêng qua `sendMessage`, **KHÔNG gửi lại file** (ko dùng `sendDocument`).

### ⚠️ Double-Send Trap (đã xảy ra 02/07/2026)

When Step 6 says "Send file today.md + caption", the agent might send **another** `sendDocument` with the same `today.md` — resulting in 2 duplicate file messages in Telegram.

**Root cause:** The script (`generate_today_revenue.py`) already sends the file via Telegram in Step 1. The agent in Step 6 should ONLY send the analysis caption, not the file.

**Fix pattern in Step 6:** Use `sendMessage`, not `sendDocument`:
```python
# ❌ Sai: sends file AGAIN
url = f"https://api.telegram.org/bot{token}/sendDocument"
requests.post(url, files={'document': open('today.md','rb')}, data={'chat_id': X, 'caption': caption})

# ✅ Đúng: caption only
url = f"https://api.telegram.org/bot{token}/sendMessage"
requests.post(url, json={'chat_id': X, 'text': caption, 'parse_mode': 'HTML'})
```

**Cách detect:** Check Telegram chat history — nếu thấy 2 messages với cùng file `today.md` trong vòng 1 phút → double-send. Fix prompt Step 6: "Gửi caption qua sendMessage (ko gửi lại file vì script đã gửi ở Step 1)".

## Caption Structure

```
📊 <b>Daily Ops Brief — DD/MM (Thứ)</b>

<b>📊 WTD Revenue (N days)</b>
┌──────┬───────────┬──────────┬───────────┐
│ Store│   Rev (tr)│  COL%    │   SPLH    │
├──────┼───────────┼──────────┼───────────┤
│ LU3  │ XX.Xtr 🔻│ XX.X% 🔴│ XXX.Xk 🔻│
│ LU5  │ XX.Xtr 🔺│ XX.X% 🟢│ XXX.Xk 🔺│
│ LU7  │ XX.Xtr 🔻│ XX.X% 🔴│ XXX.Xk 🔻│
└──────┴───────────┴──────────┴───────────┘
<i>WXX vs WXX: LU3 ±X% | LU5 ±X% | LU7 ±X%</i>
⚠️ Note if data too thin (e.g. only 1 day)

<b>🎯 Weekly Focus — 3 Priorities</b>
🔴 Priority 1 — short context + decision needed
🔴 Priority 2 — short context + decision needed
🔴 Priority 3 — short context + decision needed

<b>📅 Calendar hôm nay</b>
🕐 HH:MM—HH:MM • Event title
🕐 HH:MM—HH:MM • Event title

<i>today.md đã gửi kèm file đính kèm.</i>
```

## Telegram Bot API Pattern (Python, urllib)

```python
import json, urllib.request, uuid

# Đọc token từ LUsineWorkBot/.env (dùng đường dẫn đầy đủ, ko dùng grep)
with open(r'C:\Users\khoans\AppData\Local\LUsineWorkBot\.env') as f:
    for line in f:
        if 'TELEGRAM_BOT_TOKEN' in line:
            token = line.split('=', 1)[1].strip().strip('"').strip("'")
            break

caption = """<b>Daily Ops Brief...</b>"""

# 🤖 Pattern: sendMessage — dùng khi file đã được script gửi tự động
# Không gửi lại file qua sendDocument (tránh double-send)
req = urllib.request.Request(
    f'https://api.telegram.org/bot{token}/sendMessage',
    data=json.dumps({
        'chat_id': '2117653672',
        'text': caption,
        'parse_mode': 'HTML'
    }).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
resp = urllib.request.urlopen(req)
result = json.loads(resp.read())
```

## ⚠️ Pitfalls

| Issue | Fix |
|-------|-----|
| File hiện ra web preview (SSP/classifieds) | `Content-Type: text/markdown` → đổi thành `application/octet-stream` |
| Caption bị truncate | Telegram caption giới hạn 1024 ký tự — giữ brief, file chứa chi tiết |
| Token bị mask trong terminal output | Dùng Python `open().read()` thay vì `cat`/`grep` — xem `references/cron-credential-extraction.md` |
| Cron job `execute_code` bị block | Dùng `terminal` với inline `python3 -c "..."` cho mọi logic trong cron |

## Cron Job Config

```yaml
name: daily-ops-brief
schedule: "30 9 * * *"        # 09:30 daily
type: LLM-driven
deliver: local                  # Output log local — Telegram do agent gửi qua API
workdir: C:\Users\khoans\Documents\Warren_OS_Local
```

Prompt gồm 7 steps:
1. Run `generate_today_revenue.py` (fetch GSheet → write today.md → send its own Telegram)
2. Read `vault/today.md`
3. Query Google Calendar today events (via SA key)
4. Read CONTEXT.md §5 for weekly focus
5. Compose HTML caption
6. Send analysis caption via Telegram (today.md đã tự động gửi bởi script ở step 1 — không gửi lại file)
7. Report
