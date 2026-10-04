# Telegram Poller Pattern — Personal Vault

## Architecture Overview

Poll-based Telegram integration (ko webhook — Hermes chạy local desktop, ko public endpoint).

```
┌──────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Telegram  │ ←─→ │ poller script    │ ←─→ │ .pending.json   │
│ API       │     │ (cron every 2m)  │     │ (state machine) │
└──────────┘     └────────┬─────────┘     └─────────────────┘
                          │
                          ▼
                   ┌──────────────┐
                   │ target file  │
                   │ (051_Sleep   │
                   │  _Log.md)    │
                   └──────────────┘
```

## Tag-Based Triggering

Script chỉ xử lý message có prefix tag:

```
[capture-sleep] Health log june 30: 🏥 Health: 5h40 | quality 54 | 61kg | 18h | Huyết áp: 97/70
```

**Pattern:** `[tag-name]` ở đầu message → case-insensitive.

## State Machine

```
IDLE ──(message có tag + parse OK)──→ AWAITING_CONFIRM
  ↑                                          │
  │                              ┌───────────┼───────────┐
  │                              ▼           ▼           ▼
  │                           "ok"       "edit..."    "skip"
  │                              │           │           │
  │                              ▼           ▼           ▼
  │                          APPEND     UPDATE+APPEND   DISCARD
  └─────────────────────────────────────────────────────────┘
  (timeout 30ph → tự cleanup)
```

### Reply Format

Warren reply vào proposal message:
- `ok` → append draft nguyên bản
- `edit ngủ 6h, quality 60` → apply override → append
- `skip` → huỷ, ko ghi

### Edit Override Keywords

| Field | English | Tiếng Việt |
|-------|---------|------------|
| Sleep | `sleep 6h` | `ngủ 6h` |
| Quality | `quality 60` | `chất lượng 60` |
| Weight | `weight 62kg` | `cân 62` |
| Fasting | `fasting 16h` | `nhịn 16h` |
| Blood pressure | `bp 100/70` | `huyết áp 100/70` |

## Pending State File

```json
{
  "entries": [
    {
      "date": "2026-06-30",
      "draft": "### 2026-06-30\n...",
      "metrics": {"sleep": "5h40", ...},
      "status": "awaiting",
      "created_at": "2026-06-30T10:00:00",
      "original_message_id": 123,
      "proposal_message_id": 456
    }
  ]
}
```

## Error Recovery (Built-in)

| Mechanism | Implementation |
|-----------|----------------|
| Network failure | `try/except URLError` → return empty |
| API bad response | `try/except JSONDecodeError` |
| Corrupt state file | Auto-backup `.json.corrupt` + reset to `{entries:[]}` |
| Atomic write | `.tmp` → `.rename(parent)` — ko corrupt mid-write |
| Stale pending | Auto-cleanup sau 30 phút |
| Token missing | `sys.exit(1)` + clear message |
| Dry-run safety | `if DRY_RUN:` guard trên mọi mutation point |
| Input validation | Check source chat, check tag, parse format |
| Dedup | By date (trùng ngày → skip) + pending check |
| Offset idempotent | `read_offset` / `write_offset` — ko xử lý lại message cũ |

## File Layout

```
scripts/
├── telegram_poller.py           ← Main poller (imports helpers)
├── telegram_notify.py           ← Token + send functions
└── .telegram_pending.json       ← Auto state file (git-ignore)
```

## Key Design Decisions

1. **Poll over Webhook** — Hermes local desktop ko có public IP
2. **Python stdlib only** — urllib, json, re, pathlib — ko pip install
3. **Import existing helpers** — tận dụng `telegram_notify.get_telegram_token()`, `process_sleep.parse_all_sleep_logs()`
4. **State file over DB** — JSON file đủ cho 1 user, ko cần SQLite
5. **Reply via reply_to_message_id** — Warren reply vào proposal message → script match bằng message_id

## Usage Commands

```bash
# Dev / preview
python3 scripts/telegram_poller.py --dry-run

# Run one cycle
python3 scripts/telegram_poller.py --once

# Production (cron)
# Cron job: every 2m, no_agent=True, script mode
```
