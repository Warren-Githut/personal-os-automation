# Automation — Telegram Capture Sleep

## Mục đích
Bắt health log Warren post qua Telegram (1-1 @LUsinePersonalBot, tag `[capture-sleep]`)
→ gửi draft xác nhận → Bố reply `ok` → ghi `10_PULSE/051_Sleep_Log.md` + sync GSheet + git push.

## File tracked (trong Git)
- `scripts/process_sleep.py` — parse + write vault + GSheet sync (core)
- `scripts/telegram_notify.py` — gửi Telegram (dùng token từ ngoài repo)
- `scripts/telegram_health_poller.py` — poller chính (poll + draft + state machine)
- `automation/telegram_capture_sleep_runner.py` — wrapper cho cron (copy vào `~/.hermes/scripts/`)
- `automation/cron-telegram-capture-sleep.yaml` — cron spec

## Restore trên máy mới
1. Clone repo Personal_OS
2. Copy `automation/telegram_capture_sleep_runner.py` → `~/.hermes/scripts/`
3. Setup bot token: `AppData/Local/LUsinePersonalBot/.env` với `TELEGRAM_BOT_TOKEN=...`
4. Tạo cron: xem `cron-telegram-capture-sleep.yaml` (schedule `*/30 7-10 * * *`, no_agent=True)

## Flow
Warren post: `[capture-sleep] Health log jul 25: 🏥 Health: 7h30 | quality 88 | 62kg | 18h | Huyết áp: 99/71`
→ con gửi draft → Bố reply `ok` → ghi vault + sync + push.

## Notes
- Token KHÔNG nằm trong Git (chỉ path hardcode trong code).
- Pending state: `.telegram_pending.json` (local, ignored).
- Offset: `.telegram_offset.json` (local, ignored).
