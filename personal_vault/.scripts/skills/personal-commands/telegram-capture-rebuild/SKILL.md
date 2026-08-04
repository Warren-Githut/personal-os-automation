---
name: telegram-capture-rebuild
description: "Rebuild Telegram capture; avoid 409, split offset per flow."
version: 1.0
tags: [telegram, capture, polling, ops, personal_os, rebuild]
---

# Telegram Capture Rebuild

> Class-level pattern cho việc xây lại một luồng Telegram capture (vd tách `capture-health` khỏi `capture-sleep`). Rút ra từ session 2026-07-31 khi Bố báo luồng `telegram-capture-sleep` "không ổn định".

## Cái sai của luồng cũ (fact con tự tra được)

Luồng `telegram-capture-sleep` (job `200706218440`):
- Cron `*/2 6-13` chạy `automation/telegram_capture_sleep_runner.py` (no_agent) → gọi `scripts/telegram_health_poller.py --once`.
- (Đã xóa 2026-08-03) Watchdog `scripts/telegram_capture_sleep_watchdog.py` (bg long-poll 60s) — redundant + gây 409 với cron, bị dọn theo Option B.
- **CẢ 2 cùng gọi `getUpdates` trên 1 bot + 1 offset file (`.telegram_offset.json`).**
- → Watchdog thắng → cron trả **409** → `last_status: error`.
- `deliver: local` + error → Bố KHÔNG nhận notify → thấy "lởm" mà không rõ lý do.

**Skill `telegram-polling-ops` claim cũ ("cron silent fail vô hại, chia sẻ offset idempotent") là SAI** — xem `references/telegram-multi-flow-2026-07-31.md`.

## 2 Quy tắc cứng khi rebuild

### Rule 1 — Offset file PHẢI unique per flow
`getUpdates` consumes update. Poller nào đọc trước "ăn" message → poller kia (kể cả tag khác) không bao giờ thấy.
→ Chia sẻ 1 offset file = **message loss cross-flow**.
→ Đặt tên: `.telegram_<flow>_offset.json` + `.telegram_<flow>_pending.json` (vd `.telegram_health_offset.json`).

### Rule 2 — Bỏ watchdog nếu muốn triệt 409
Pattern B (single consumer): chỉ 1 cron poll định kỳ (5-10p) chạy `--once`, route nhiều tag trong 1 poller. Không watchdog → không 409.
- Bố nghiêng hướng này cho rebuild `capture-health` (2026-07-31).
- Nếu giữ watchdog: phải split offset riêng (Pattern A) + mỗi poller chỉ xử lý tag của nó, bỏ qua tag khác.

## Rebuild checklist (capture-health)

1. Tạo `scripts/capture_health_poller.py` — parse tag `[capture-health]`, draft gửi Telegram, chờ `ok`/`skip`.
2. Tái dùng từ `process_sleep.py`: `parse_duration`, `is_duplicate`, `append_to_sleep_log` (generic prepend), `sync_to_gsheet` (param hóa tab). Viết `process_health.py` mới vì regex `SLEEP_PATTERN` gộp sleep+quality → health không bắt buộc sleep.
3. Offset/pending file riêng: `.telegram_health_offset.json`, `.telegram_health_pending.json`.
4. File pulse riêng (vd `10_PULSE/052_Health_Log.md`) — tách khỏi `051_Sleep_Log.md`.
5. Cron: `no_agent: true`, `deliver: local`, schedule `*/5 6-22` (hoặc theo Bố duyệt). KHÔNG tạo watchdog.
6. **Error visibility:** cron gửi Telegram notify khi `last_status: error` (để Bố không bị "lởm mà không rõ lý do").
7. Verify gate: `--dry-run` test parse (không gọi API, không conflict) trước khi deploy.

## Related Skills
- `telegram-polling-ops` (warren-profile, PROTECTED — có claim cũ SAI; recommend `hermes curator adopt telegram-polling-ops` để patch)
- `capture-sleep` (warren-profile, PROTECTED — consumer của luồng cũ; recommend `hermes curator adopt capture-sleep` để ghim correction)
- `personal-inbox-routing` — routing inbox → capture skill
