# Automation — Telegram Capture Sleep

## Mục đích
Bắt health log Warren post qua Telegram (1-1 @LUsinePersonalBot, tag `[capture-sleep]`)
→ gửi draft xác nhận → Bố reply `ok` → ghi `10_PULSE/051_Sleep_Log.md` + sync GSheet.

## Flow
Warren post: `[capture-sleep] Health log jul 25: 🏥 Health: 7h30 | quality 88 | 62kg | 18h | Huyết áp: 99/71`
→ con gửi draft → Bố reply `ok` → ghi vault + sync GSheet.

## Cơ chế hoạt động (2 lớp)

| Lớp | Tần suất | Durable? | Mô tả |
|-----|----------|----------|-------|
| **Cron** `telegram-capture-sleep` | `*/2 6-13 * * *` | ✅ Có (cron độc lập) | Poll mỗi 2 phút trong khung 6-13. Script: `telegram_capture_sleep_runner.py` |
| **Watchdog** (Hermes session) | Long-poll 60s | ❌ Chỉ khi Hermes mở | Real-time, phản hồi trong vài giây. Script: `telegram_capture_sleep_watchdog.py` |

## Delegation Zones
- **Telegram path** 🟢: poller tự chạy, tự sync GSheet khi Bố reply ok
- **Hermes chat path** 🟡: Hermes phải hỏi Bố trước khi dùng `--sync-gsheet`

## Files tracked (trong Git)
| File | Vai trò |
|------|---------|
| `scripts/process_sleep.py` | Parse + write vault + GSheet sync (core) |
| `scripts/telegram_notify.py` | Gửi Telegram (token từ ngoài repo) |
| `scripts/telegram_health_poller.py` | Core poller logic (draft + state machine) |
| `scripts/telegram_capture_sleep_watchdog.py` | Long-poll watchdog (real-time, Hermes session) |
| `automation/telegram_capture_sleep_runner.py` | Wrapper cho cron |
| `automation/cron-telegram-capture-sleep.yaml` | Cron spec |

## Restore trên máy mới
1. Clone repo Personal_OS
2. Copy `automation/telegram_capture_sleep_runner.py` → `~/.hermes/scripts/` (cho cron)
3. Setup bot token: `AppData/Local/LUsinePersonalBot/.env` với `TELEGRAM_BOT_TOKEN=...`
4. Tạo cron: xem `cron-telegram-capture-sleep.yaml`
   ```
   hermes cron create --schedule "*/2 6-13 * * *" --name "telegram-capture-sleep" \
     --script telegram_capture_sleep_runner.py --no-agent --deliver local \
     --enabled-toolsets terminal
   ```

## Notes
- Token KHÔNG nằm trong Git (chỉ path hardcode trong code).
- Pending state: `.telegram_pending.json` (local, ignored).
- Offset: `.telegram_offset.json` (local, ignored).
- Duplicate check: nếu date đã có trong vault → skip, không tạo draft.
