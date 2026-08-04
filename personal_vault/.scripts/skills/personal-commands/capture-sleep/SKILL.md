---
name: capture-sleep
description: "Process health/sleep logs from _inbox/01_unprocessed/ OR direct paste -> parse metrics (sleep hours, quality, weight, fasting, BP) -> generate insight -> prepend to 10_PULSE/051_Sleep_Log.md (newest on top). Supports 3 modes: inbox scan (default), --paste (direct), --watch (manual edit detection). Telegram notify optional."
version: 1.0
tags: [health, sleep, capture, personal_os]
---

# /capture-sleep — Sleep Log Capture

## Purpose
Process health/sleep logs from `_inbox/01_unprocessed/` OR direct paste input — parse metrics, generate insight, prepend to `10_PULSE/051_Sleep_Log.md` (newest on top).

## Usage

```bash
# Mode 1 — Scan inbox for health log files (*health*.md)
/capture-sleep

# Mode 2 — Direct paste (input trong chat)
/capture-sleep "Health log june 14: :hospital: Health: 6h50 | quality 92 | 63kg | 17h | Huyết áp: 98/71"

# Mode 3 — Watch mode (foreground, phát hiện manual edit)
/capture-sleep --watch
```

## Behavior

### Mode 1 — Inbox scan (default)
1. Scan `_inbox/01_unprocessed/` for files matching `*health*.md`
2. For each file: parse sleep metrics (hours, quality, weight, fasting, BP)
3. Check duplicate (same date) — skip if exists
4. Generate insight text (compare vs baseline 7h, quality threshold, BP range)
5. Prepend new entry to `10_PULSE/051_Sleep_Log.md` (newest on top)
6. Move processed file to `02_processed_archived/`
7. Send Telegram notification (optional, auto-enabled)

### Mode 2 — Direct paste
- Parse text for `Health log <month> <day>: :hospital: Health: <sleep> | quality <N> | <weight>kg | <fasting>h | Huyết áp: <BP>` pattern
- Same duplicate check + insight generation + prepend

### Mode 3 — Watch mode (--watch)
- Foreground file watcher: detects manual edits to `051_Sleep_Log.md`
- Sends Telegram notification on each new entry detected

## Output Summary
```
📋 Processing paste input...
✅ Parsed: 2026-06-14 (6h50)
✅ Added 1 sleep log(s)
```

## Entry Format (prepended to 051_Sleep_Log.md)
```markdown
### YYYY-MM-DD
**Source:** _inbox/01_unprocessed/<filename> | direct_paste
**Type:** text

Sleep: 6h50 | Quality: 92/100 | Fasting: 17h | Weight: 63kg | Blood pressure: 98/71

Insight:
Sleep 6h50 thấp hơn baseline 7h. Quality 92 vẫn ổn. BP 98/71 bình thường. Fasting 17h consistent. Weight 63kg ổn định. [MOD]

---
```

## Script
**Canonical script:** `C:\Users\khoans\Documents\Personal_OS\personal_vault\scripts\process_sleep.py`
(Không copy vào skill directory — single source of truth tại personal vault)

Script cũ (legacy): `C:\Users\khoans\Documents\Personal_OS\personal_vault\scripts\capture_sleep.py`
(Chỉ xử lý inbox, không có `--paste` mode)

## Dependencies
- `process_sleep.py` — main processing logic (inbox + paste + watch)
- `telegram_notify.py` — optional Telegram notification (try/except fallback)
- Personal vault: `10_PULSE/051_Sleep_Log.md` — target log file

## Support files
- `references/telegram-bot-routing.md` — Telegram bot token priority (personal bot → env fallback)

## Pitfalls
- **Script chạy bằng python3 (Hermes context):** Gọi qua `terminal` tool với absolute path. Không có `--auto` flag vì script không dùng `input()` — chạy non-interactive OK.
- **Hardcoded paths trong script:** `VAULT_ROOT = Path("C:/Users/khoans/Documents/Personal_OS/personal_vault")` — nếu personal vault move path, cần update script.
- **Telegram notification cần module `telegram_notify`:** Nếu import fail, script silent skip Telegram (không crash).
- **Duplicate detection:** Chỉ check trùng date (YYYY-MM-DD). Nếu cùng ngày nhưng sleep khác, entry thứ 2 bị skip.
- **Pattern matching:** Script dùng regex `SLEEP_PATTERN` với format cụ thể. Nếu thay đổi format Slack/Telegram, cần update regex.

## GSheet Confirmation Gate (MANDATORY — Hermes-level)

The GSheet sync to tab `W-capture-sleep` is a **Zone 🟡** action (writes to a shared workbook). Under Hermes the script runs **non-interactive**, so its built-in `input()` prompt is dead — it can NEVER reach Warren. Therefore:

1. **Hermes MUST ask Warren in the chat** whether to also sync to GSheet, BEFORE running the capture. This is a chat-level confirmation gate — not the script's stdin prompt.
2. Only pass `--sync-gsheet` when Warren explicitly says OK that turn.
3. NEVER run a test/real GSheet write with fabricated data — verify via the read-only idempotent path (`sync_to_gsheet(send_notify=False)` → 0 rows when up-to-date).
4. If Warren does NOT answer, default = vault only (no GSheet). Do NOT assume.
5. Set `HERMES_AGENT=1` in the run environment so the script never prints the dead interactive prompt under Hermes.

The script now: ignores the interactive prompt under `HERMES_AGENT=1` (or non-interactive), and only syncs when `--sync-gsheet` is passed. So the gate lives entirely in the agent's chat behavior.

## Related Skills
- `capture-stock` — stock market capture (cùng pattern inbox → pulse)
- `personal-vault-lint` — vault health check (đọc 051_Sleep_Log.md để check red-flag sleep <6h × 5 nights)
- `personal-inbox-routing` — routes inbox items to appropriate capture skills

## Cron
Hiện chưa có cron. Nếu muốn auto-process hàng ngày:
```
hermes cron create --schedule "0 10 * * *" \
  --name "capture-sleep-daily" \
  --prompt "Chạy capture-sleep (inbox scan) và báo kết quả" \
  --skills capture-sleep
```

## MANDATORY VERIFY GATE (rule: never trust LLM, verify everything)

After EVERY parser run that reads Excel/CSV/PDF ([DOMAIN: health/sleep log]), MUST run verify-parser-output gate BEFORE reporting numbers or committing.

1. Independent recompute (fresh script, different method).
2. Cross-assert EVERY number (giá, P&L, room, %Δ, số dư, headcount) vs LLM output.
3. Category-drop scan: count raw rows vs filtered; flag dropped (mã rỗng, dòng tổng, Loc=NaN).
4. Emit VERIFY_RESULT: PASS|FAIL + dropped count. Temp hermes-verify-*.py, clean after.
5. FAIL → LLM wrong until proven. Fix logic, re-run, re-verify.
