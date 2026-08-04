---
name: telegram-capture-gate
description: >-
  Capture data from Telegram brain dumps into Personal OS vault with a confirmation gate.
  Polls @personal_life_bot for tagged messages (e.g. [capture-sleep]) → parses → proposes
  draft back to Warren → waits for "ok" / "edit ..." / "skip" → writes to vault only after
  explicit approval. Tag-based routing for multi-domain support.
  Built with spec-driven-development, incremental-implementation, 5-axis code review,
  code-simplification, battle-test, and debugging-and-error-recovery methodology stack.
version: 1.1
tags: [telegram, capture, ingest, confirmation-gate, personal_os]
---

# Telegram Capture Gate — Brain Dump with Confirmation

## Purpose
Allow Warren to brain dump health / sleep data (and future domains) into Telegram,
then have Hermes auto-process with a confirmation gate — propose draft, get approval,
only write to vault when confirmed.

Designed for **non-interactive cron execution** — polls Telegram every 2 minutes,
maintains a pending state file between cycles.

## Architecture

```
Warren gửi Telegram: "[capture-sleep] Health log jun 30: 🏥 Health: 5h40 | ..."
        ↓
[telegram_health_poller.py] chạy cron mỗi 2 phút
        ↓
Phát hiện message mới (offset tracking) → parse tag + metrics
        ↓
Gửi draft về Telegram: "📋 Draft entry này, anh OK?
           Sleep: 5h40 | Quality: 54/100 | ...
           👉 Reply: 'ok' / 'edit [nội dung]' / 'skip'"
        ↓
Lưu pending state vào .telegram_pending.json
        ↓
Lần poll kế → thấy Warren reply:
  • "ok"       → append vào 051_Sleep_Log.md
  • "edit X"   → update draft → append
  • "skip"     → huỷ, ko ghi
        ↓
Gửi xác nhận Telegram: "✅ Done!" hoặc "⏭️ Skipped"
```

## Tag-Based Routing

| Tag | Domain | Target File | Notes |
|-----|--------|-------------|-------|
| `[capture-sleep]` | health | `10_PULSE/051_Sleep_Log.md` | Same format/code as `capture-sleep` skill |
| `[capture-stock]` | _planned_ | `10_PULSE/020_VNStock_Weekly_Outlook.md` | Future |
| `[capture-note]` | _planned_ | `_inbox/01_unprocessed/` | Future |

## Confirmation Gate Flow

1. **New message detected** → parse tag + metrics → generate draft entry → send proposal to Telegram
2. **Pending state saved** → status=`awaiting_approval`
3. **Next poll** → check reply to proposal_msg_id:
   - Reply = "ok" → status=`approved` → write to target file → send ✅
   - Reply = "edit [text]" → merge edit into draft → status=`edited` → write → send ✅
   - Reply = "skip" → status=`skipped` → clean up → send ⏭️
   - No reply yet → do nothing (keep waiting)
4. **Timeout**: pending >30 min → status=`timed_out` → notify Warren via Telegram
5. **Duplicate guard**: check if same date already in target file → skip + notify

## Script

**Canonical script:** `C:\Users\khoans\Documents\Personal_OS\personal_vault\scripts\telegram_health_poller.py`

```bash
# Dry run — parse + show, ko ghi file, ko send Telegram
python3 scripts/telegram_health_poller.py --dry-run

# One-shot (single poll cycle, no loop)
python3 scripts/telegram_health_poller.py --once
```

## State Machine

States: `awaiting_approval` → `approved` / `edited` / `skipped` / `timed_out`

State file: `.telegram_pending.json` in scripts/ directory (auto-created, never committed).

## Parsing

Pattern: `Health log <month> <day>: :hospital: Health: <sleep>h | quality <N> | <weight>kg | <fasting>h | Huyết áp: <sys>/<dia>`

Insight generation (same as process_sleep.py):
- Sleep vs baseline 7h — flag if <6h or >9h
- Quality threshold — <60 = "cần cải thiện"
- BP range — bình thường / cao
- Fasting hours — consistent / inconsistent
- Weight trend — ổn định / thay đổi

## Quality Gates (for extending/modifying this skill)

Every change follows the methodology stack:

### 1. Spec-Driven Development
Before code: write spec (Objective, Commands, Project Structure, Code Style, Testing Strategy, Boundaries). Surface assumptions. Get Warren approval before implementing.

### 2. Planning & Task Breakdown
Decompose into thin vertical slices (<5 files each). Map dependency graph. Each task has acceptance criteria + verification step.

### 3. Incremental Implementation
One slice at a time: implement → test → verify → commit. Each slice leaves system working. No slice >100 lines.

### 4. Code Simplification (pre-review)
Apply 5 principles:
- Preserve behavior exactly (--dry-run still passes)
- Follow project conventions (stdlib urllib, not requests)
- Prefer clarity over cleverness (no nested comprehension)
- Maintain balance (extract helpers, don't inline all)
- Scope to change (don't refactor unrelated code)

### 5. 5-Axis Code Review
1. **Correctness** — edge cases, error paths, all inputs tested
2. **Readability** — naming, control flow, no dead code
3. **Architecture** — module boundaries, state machine clean
4. **Security** — token never logged, input untrusted
5. **Performance** — no unbounded loops, 2-min cycle OK

### 6. Debugging & Error Recovery (Stop-the-Line)
1. STOP adding features
2. PRESERVE evidence (error, state file, offset)
3. REPRODUCE with --dry-run
4. LOCALIZE (poll? parse? state? write?)
5. REDUCE to minimal case
6. FIX root cause (not symptom)
7. GUARD with regression check
8. RESUME after verification

## Battle Test Checklist

Before production-ready:
- [ ] Message without tag → ignored silently
- [ ] Malformed `[capture-sleep]` data → polite error, no crash
- [ ] Same date as existing entry → duplicate notification
- [ ] Network failure mid-poll → state file preserved, next cycle recovers
- [ ] Two tagged messages in succession → both queued
- [ ] Gibberish reply (not ok/edit/skip) → ignored, no crash
- [ ] Pending timeout >30 min → auto-cleanup + notify
- [ ] Crash mid-write → atomic write (.tmp→rename) prevents corruption

### A/B Test (when changing format/logic)
- Run `--dry-run` on same input through BOTH old and new code
- Compare output: exact match required
- Check target file: same format, same insight quality

## Pitfalls

- **Offset tracking bắt buộc** — ko track offset → xử lý lại message cũ mỗi lần poll. Lưu offset sau mỗi lần poll, dù có message mới hay ko.
- **Reply_to_message_id** — cách duy nhất match reply với proposal. Ko dùng text matching.
- **Rate limit**: Telegram API ~30 msg/s cho getUpdates. Poll 2 phút là an toàn.
- **Bot ko đọc được message cũ** — getUpdates chỉ trả về sau lần poll cuối. Nếu bot offline, message trong khoảng đó bị skip.
- **Duplicate detection**: Check target file TRƯỚC khi propose. Nếu date đã tồn tại → thông báo thay vì propose.
- **Edit handling**: "edit ngủ 6h, quality 60" → chỉ thay metrics user đề cập, giữ phần còn lại.
- **Cron 2 phút**: script phải nhanh (timeout <60s). Ko gọi heavy API trong poll cycle.
- **`getChatHistory` KHÔNG tồn tại trong Telegram Bot API** — gọi trả `HTTP 404: Not Found`. Bot API chỉ có `getUpdates` (long-poll) và webhook. Đừng bao giờ dùng `getChatHistory` trong bot script (chỉ user account qua MTProto mới có). Mọi fallback "quét lịch sử chat" = sai thiết kế.
- **2 consumer cùng 1 bot token = race condition ăn update** — Telegram round-robin update giữa các process gọi `getUpdates` chung token. 1 thằng nhận "ok", thằng kia nhận null → pending treo vĩnh viễn. Đây là root cause phổ biến của "user gửi ok mà bot ko thấy". Chỉ 1 process được phép poll 1 bot token (cron HOẶC manual, không cả hai; không script nào khác share token).
- **Verify gate bị "game" bởi mock** — test mock `tg_api` trả về history giả → `RESULT: PASS` giả. Phải verify với REAL API (getMe / getUpdates thật) trước khi claim PASS. Mock chỉ hợp lệ khi test pure logic, không cho network call.
- **Reset offset vô dụng nếu update đã bị consume** — `offset.json → {"offset":0}` chỉ có tác dụng khi update CHƯA bị process khác eat. Nếu đã bị eat → reset không giúp, phải diệt process kia.

## Debugging & Root-Cause (quy trình chuẩn khi bot "ko nhận tin")

Khi Bố báo "gửi rồi mà bot im", làm THEO THỨ TỰ này (đừng code ngay):

1. **Xác nhận token/polling cơ bản:** `getMe` → bot id đúng? Token canonical đọc từ đâu?
2. **`getUpdates(offset=0)` count bao nhiêu?**
   - `COUNT > 0` → bot thấy tin, lỗi ở parse/match logic (sửa script).
   - `COUNT = 0` MÀ Bố khẳng định đã gửi → **update đã bị process khác consume**. Đây là 99% trường hợp "im lặng".
3. **Tìm process eat update:** `netstat -ano | grep 149.154` → lấy PID → `Get-CimInstance Win32_Process -Filter "ProcessId=PID"` → đọc CommandLine. Tìm pythonw/chrome đang long-poll cùng token.
4. **Single-consumer fix:** tắt process dư, hoặc đổi bot token riêng cho poller, hoặc chuyển sang webhook (webhook deliver 1 lần, không race).
5. **Reset offset** (`offset.json` → `{"offset":0}`) chỉ thử SAU khi confirm không có process dư.

⚠️ Đừng viết code mới (TDD slice, fallback) trước khi xong bước 1-4. Triệu chứng "im lặng" hầu hết là infra, không phải logic.
▶ Chi tiết command + transcript thực tế: `references/telegram-bot-polling-debug.md`

## Cron

```bash
hermes cron create --schedule "*/2 * * * *" \
  --name "telegram-health-poller" \
  --prompt "Poll Telegram for new [capture-sleep] messages and process with confirmation gate" \
  --skills telegram-capture-gate \
  --deliver local
```

## Overlap Note

`capture-sleep` and `telegram-capture-gate` share target file `051_Sleep_Log.md` and parse logic. `capture-sleep` handles inbox/direct-paste input; `telegram-capture-gate` handles Telegram input with confirmation gate. Consider consolidation if overlap grows.

## Related Skills

- `capture-sleep` — health log capture (same target file, same parse logic, alternative input paths)
- `personal-inbox-routing` — inbox processing (alternative input path)
- `telegram-notify` — send Telegram messages (reused)

## Support Files

- `references/telegram-bot-routing.md` — bot token priority and config (shared with capture-sleep)
- `references/telegram-brain-dump-spec.md` — full session spec (assumptions, architecture, success criteria)

## MANDATORY VERIFY GATE (rule: never trust LLM, verify everything)

After EVERY parser run that reads Excel/CSV/PDF ([DOMAIN: telegram capture (brain dump)]), MUST run verify-parser-output gate BEFORE reporting numbers or committing.

1. Independent recompute (fresh script, different method).
2. Cross-assert EVERY number (giá, P&L, room, %Δ, số dư, headcount) vs LLM output.
3. Category-drop scan: count raw rows vs filtered; flag dropped (mã rỗng, dòng tổng, Loc=NaN).
4. Emit VERIFY_RESULT: PASS|FAIL + dropped count. Temp hermes-verify-*.py, clean after.
5. FAIL → LLM wrong until proven. Fix logic, re-run, re-verify.
