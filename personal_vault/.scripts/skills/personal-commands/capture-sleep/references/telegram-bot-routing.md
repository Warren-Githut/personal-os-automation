# Telegram Bot Routing — Personal Vault

## Script: `telegram_notify.py`

**Path:** `C:\Users\khoans\Documents\Personal_OS\stock_vault\scripts\telegram_notify.py`

`capture-sleep` và các skill personal khác (như `stock-capture`) đều gọi `telegram_notify.send_telegram()` để gửi notification qua Telegram.

## Token Priority (đã fix 2026-06-27)

| Priority | Source | Bot | Trạng thái |
|----------|--------|-----|------------|
| 1 | `LUsinePersonalBot/.env` → `TELEGRAM_BOT_TOKEN` | **Personal Life Bot** (`@personal_life_bot`) | ✅ Active |
| 2 | `TELEGRAM_BOT_TOKEN` env var | HORION / LUsineWorkBot (cũ) | ⚠️ Fallback |

**Thứ tự trong code (`get_telegram_token()`):**
```python
# 1) Personal life bot token
personal_env = Path("C:/Users/khoans/AppData/Local/LUsinePersonalBot/.env")
# đọc TELEGRAM_BOT_TOKEN từ file này

# 2) Global env var (fallback)
token = os.getenv("TELEGRAM_BOT_TOKEN")
```

## Personal Bot Config

| Thông tin | Giá trị |
|-----------|---------|
| Bot username | `@personal_life_bot` |
| Token | `842657...HRlU` (file `.env` tại `LUsinePersonalBot/`) |
| Chat ID | `2117653672` (giống ops bot) |

## Lịch sử

- **Trước 2026-06-27:** Script đọc `TELEGRAM_BOT_TOKEN` từ `personal_profile/.env` → trúng HORION token (`890090...`) → **401 error** vì HORION bot token đã revoke
- **Fix:** Đổi thứ tự ưu tiên: personal bot `.env` trước, global env var fallback sau
- **Skill liên quan:** `stock-capture` cũng dùng `telegram_notify.py` — cùng cơ chế
