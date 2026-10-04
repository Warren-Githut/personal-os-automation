# Warren Review Pipeline — Actual Flow (verified 2026-07-28)

> Captured because an agent misread SKILL.md doc-drift and built a duplicate
> "ok review" bot. The REAL pipeline already existed. Read this before touching
> anything review-related.

## Intake / approval vocabulary (BỐ confirmed)
- `[review]` → gửi review MỚI (intake). Bot → `review_intake.py` writes `raw_pending`.
- `[col]` → gửi COL mới (intake).
- `ok review` → APPROVE review đang chờ (không tạo mới).
- `ok col` → APPROVE COL đang chờ.
- `ok 01` → revenue weekly approve. `ok 09` → hourly regen approve. `ok rv` → google-review weekly.

## Real components (on disk, DO NOT rebuild)
- Intake: `vault/.scripts/review_intake.py` (writes raw_pending to review_queue.json)
- Handler: `vault/.scripts/review_response_handler.py`
  - `_append_to_gsheet(csv_row, raw_text)` → appends to GSheet tab
    `05_Google_Review_Weekly_Log` (SHEET_ID `1ZtIocc_Ic1z...`, not markdown log)
  - `handle_review_message(text, user_id)` → routes ok review/ok col, appends GSheet
- Bot: `vault/.scripts/lusine-ops/lusine_ops/telegram_bot.py`
  - `handle_text()` calls `handle_review_message` on plain text (line ~390)
- Cron `review-queue-watcher` (5b989c1b38b4): LLM, processes raw_pending →
  parse/classify/draft → writes approval_message + csv_row, status=pending
- Cron `review-telegram-sender` (97c05046989a): no_agent, sends approval_message
  to Telegram for Bố duyệt (script = `profile/scripts/review_telegram_sender.py`)

## End-to-end (verified live 2026-07-28)
1. BỐ gửi `[review] L'Usine Lê Thánh Tôn ...` → raw_pending
2. `review-queue-watcher` runs (force via cronjob run) → LU3/5★/Arzu Başman/Path4
3. `review-telegram-sender` runs → nháp gửi TG (status=notified)
4. BỐ gõ `ok review` trên TG → bot → handle_review_message → _append_to_gsheet
5. Review lên GSheet Row 256 (NOT markdown log — grep markdown sẽ không thấy)

## Pitfalls
- `posted_to_log` field stays None/False even after success — system appends to
  GSheet, not the markdown log. Don't grep markdown to verify.
- `review_telegram_sender.py` is SYSTEM (cron 97c05 depends on it). An agent
  deleted it thinking it was self-built → broke pipeline → restored via
  `git show 0a0c4d5:scripts/review_telegram_sender.py`.
- ops-review SKILL.md has DOC-DRIFT (describes bot that doesn't exist). The
  build plan `review-approval-build-2026-07-28.md` was approved but the real
  flow already covered it. Trust disk over SKILL.md.
