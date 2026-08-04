# Telegram Chat ID Resolution

> Khi cron gửi Telegram fail với "chat not found" (HTTP 400) hoặc `getUpdates` rỗng.

## Problem

Bot `lusine_work_bot` chưa từng nhận tin trong phiên → `getUpdates` rỗng → không biết chat_id để gửi.

## Solution

Các no_agent script hiện có trong `<profile>/scripts/` đã hardcode CHAT_ID đúng. Grep:

```bash
grep -r 'CHAT_ID' /c/Users/khoans/AppData/Local/hermes/profiles/warren-profile/scripts/*.py
```

Warren's chat_id = **2117653672** (lusine_work_bot).

## Fallback

Nếu tất cả script đều mới (không có CHAT_ID) → start bot, send 1 tin từ account Warren, check `getUpdates`.
