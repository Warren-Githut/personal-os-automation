---
name: telegram-polling-ops
description: "Telegram polling debug: 409, watchdog, offset, pending."
version: 1.0
tags: [telegram, polling, ops, debugging, personal_os]
---

# Telegram Polling Operations

> Companion to `telegram-capture-gate` (capture flow) — covers operational pitfall patterns for running Telegram polling safely.

## Architecture: Primary + Backup

```
Watchdog (long-poll, 60s timeout) → PRIMARY consumer (real-time, ~2s latency)
  Cron (every 2 min)              → BACKUP consumer (when watchdog is down)
```

- Cả 2 chia sẻ offset file (`.telegram_offset.json`) → idempotent
- Chỉ 1 instance active tại 1 thời điểm (do 409 conflict)
- Khi watchdog chạy → cron silent fail → vô hại, lần sau OK
- Khi watchdog down → cron bắt message trong vòng 2 phút

## 409 Conflict — Singleton Rule

Telegram Bot API `getUpdates` chỉ cho 1 instance. Gọi đồng thời → HTTP 409, inst cũ chết.

| Tình huống | Effect |
|------------|--------|
| Watchdog (60s) + cron chạy | Watchdog có retry (exp backoff 10-60s) → tự phục hồi |
| Debug poller thủ công | "Ăn cắp" update — poller không thấy message đó nữa |
| Cron chạy trong lúc watchdog đang long-poll | Silent fail (exit 0) → lần sau OK |

## Safe Debug Protocol

Before manually polling when watchdog is active:

1. **Kill watchdog**: `process(action='kill', session_id='proc_...')`
2. **Debug**: `--dry-run` (parse sample, ko gọi API) > `--once` (gọi getUpdates)
3. **Restart watchdog**: `terminal(bg, command='...watchdog.py')`

**Dùng `--dry-run` để test parse** — không cần getUpdates, không conflict.

## Offset Management

File: `.telegram_offset.json` (scripts/)

| Action | When |
|--------|------|
| Check current | `cat .telegram_offset.json` — xem poller đã đọc tới đâu |
| Rollback (N) | `echo '{"offset":N}' > .telegram_offset.json` — để re-xử lý (không recommend, cache Telegram có thể đã hết hạn) |
| Clear pending | `rm -f .telegram_pending.json` — khi bị stuck awaiting_approval |

⚠️ Rollback offset KHÔNG recover message đã consumed khỏi cache Telegram (getUpdates chỉ trả về 1 lần trong ~24h).

## Stuck Pending Recovery

| Problem | Root cause | Fix |
|---------|-----------|-----|
| Poller silent, offset frozen | Pending chờ "ok"/"skip" | `rm .telegram_pending.json` |
| Bố nói "skip" nhưng pending vẫn đó | Gõ tin nhắn mới, không reply vào draft | Clear pending |
| Duplicate draft mỗi lần | Pending cũ chưa clear | Clear pending + reset offset |

## Duplicate Spam Protection

- **Watchdog**: có `ALREADY_NOTIFIED` set — 1 cảnh báo / date / session
- **Cron poller**: không có — tối giản, single-cycle

## Related Skills

- `telegram-capture-gate` — capture flow (tag parsing, draft, confirmation)
- `capture-sleep` — health log capture (same target file)
