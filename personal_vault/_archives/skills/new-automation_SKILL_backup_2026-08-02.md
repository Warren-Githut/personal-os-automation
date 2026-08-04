---
name: new-automation
description: "Onboard workflow mới — phỏng vấn, phân zone, test, deploy. Warren nói 'làm cái này tự động' → Hermes handle từ A-Z."
version: 1.0.0
author: Hermes
trigger: "/new-automation"
---

# /new-automation — Onboard Workflow Mới

> **Khi nào:** Warren nói "làm cái này tự động giùm anh", "setup automation", hoặc gõ `/new-automation`.

---

## Detection — Đơn giản hay phức tạp?

Khi Warren nói "làm tự động", phân loại ngay:

| Loại | Dấu hiệu | Quy trình |
|------|----------|-----------|
| **Đơn giản** | 1 file, 1 API call, cron đơn giản | 5 bước bên dưới |
| **Phức tạp** 🆕 | Nhiều file, confirmation gate, Telegram poll, state machine, nhiều edge cases, hoặc Warren gõ tên methodology (spec-driven-development, planning, battle-test, etc.) | **Complex Automation Workflow** (Phần riêng bên dưới) |

> Nếu nghi ngờ → hỏi Warren "Anh muốn làm nhanh (5 bước) hay làm kỹ (full spec → plan → incremental)?"

---

## Process — 5 bước (Đơn giản)

### Bước 1: Hỏi (kèm gợi ý)

Hermes hỏi từng câu, mỗi câu kèm 3-4 multi-choice + recommend.

**Câu 1 — Việc gì?**
```
Hermes: "Anh muốn tự động hoá việc gì?
  A = Check số liệu mỗi sáng 📊 (recommend ✅ — 5 phút, dễ, ko rủi ro)
  B = Parse data từ file Excel/GSheet 
  C = Gửi báo cáo Telegram mỗi ngày
  D = Việc khác — anh nói em ghi"
```

**Câu 2 — Tần suất?**
```
Hermes: "Việc này lặp lại thế nào?
  A = Mỗi ngày (recommend ✅ — Cron daily)
  B = Mỗi tuần
  C = Khi có data mới (ad-hoc, ko cần cron)
  D = 1 lần duy nhất"
```

**Câu 3 — Hậu quả nếu sai?**
```
Hermes: "Nếu Hermes sai thì hậu quả thế nào?
  A = Ko sao — chỉ đọc số liệu (recommend ✅ → zone 🟢)
  B = Ghi sai file — sửa được (→ zone 🟡)
  C = Mất tiền / ảnh hưởng người khác (→ zone 🔴)
  D = Cần Warren quyết định (→ zone 🟠)" 
```

### Bước 2: Phân zone 🟢🟡🟠🔴

Dùng Delegation Zones framework để gán zone.

**Output:**
```
→ Task: [tên]
→ Zone: 🟡 (Draft → Warren approve)
→ Lý do: Lần đầu chạy, cần test trước
```

### Bước 3: Chạy test 1 lần

Hermes thực hiện task đó 1 lần, show kết quả cho Warren.

```
Hermes: "Chạy thử lần 1...
  ✅ Output: [kết quả]
  Anh check giúp — có đúng ko?
  → Nếu OK: qua bước 4
  → Nếu sai: em sửa"
```

### Bước 4: Lưu

| Tình huống | Làm gì |
|------------|--------|
| Task 1 lần, ko lặp | Dừng — đã chạy xong |
| Cần chạy lại (nhưng ko theo lịch) | Tạo skill → `/new-automation` có thể gọi lại |
| Chạy theo lịch | Tạo skill + cron job |
| Chạy khi có trigger | Tạo skill + ghi trigger vào description |

### Bước 5: Ghi zone vào SOUL.md §5.1

```
Cập nhật Delegation Zones trong SOUL.md:
→ [task]: zone 🟡 (lần đầu) / 🟢 (đã test ổn)
```

**Ghi chú:** Hỏi Warren trước khi patch SOUL.md.

---

## Guidelines cho Hermes

- Luôn kèm **gợi ý câu trả lời** — Warren ko cần nghĩ
- Mỗi lần chỉ hỏi **1 câu** — ko hỏi dồn
- Nếu Warren ko biết Hermes làm được gì → gợi ý bằng ví dụ cụ thể
- Luôn chạy **test 1 lần** trước khi deploy cron/skill
- Task nào chạy lần đầu → zone 🟡 mặc định

---

## Ví dụ thực tế

```
Warren: "Làm cái check KPI mỗi sáng tự động giùm anh"

Hermes: "Chọn giúp em:
  A = Check revenue hôm qua từ GSheet 📊 (recommend ✅)
  B = Check covers + Rev/Cover
  C = Check review queue có gì mới
  D = Việc khác"

Warren: "A"

Hermes: (chạy thử 1 lần) → show result
       → Warren OK
       → Tạo cron 8:00 sáng daily
       → Zone 🟡 (cần approve lần đầu → sau promote 🟢)
```

---

---

## Complex Automation Workflow 🏗️

> **Khi nào:** Automation phức tạp (Telegram poller, multi-file, state machine, confirmation gate) hoặc Warren gõ tên methodology (spec-driven-development, planning, battle-test, etc.)

### Phase 1: SPEC — Spec-Driven Development

Viết spec đầy đủ trước khi code. Gồm:

1. **List ASSUMPTIONS** — Warren fix trước khi đi tiếp
2. **Objective** — what + why, success criteria
3. **Architecture diagram** — data flow, components
4. **Commands** — dev (--dry-run), test, prod
5. **Project structure** — exact file paths
6. **Code style** — 1 snippet showing conventions
7. **Testing strategy** — test layers + tools
8. **Boundaries** — Always / Ask First / Never
9. **Success Criteria** — specific, testable, Warren-verifiable
10. **Open Questions**

Warren approve → qua Phase 2.

### Phase 2: PLAN — Planning & Task Breakdown

1. **Dependency graph** — component dependencies
2. **Vertical slices** — mỗi slice là 1 end-to-end feature
3. **Tasks** — bite-sized (2-5 phút), mỗi task có:
   - Acceptance criteria
   - Verification step (exact command + expected output)
   - Files touched
4. **Checkpoints** — sau mỗi 2-3 tasks
5. **Save plan** → `.hermes/plans/<date>-<slug>.md`
6. Warren approve → qua Phase 3

### Phase 3: BUILD — Incremental Implementation

Xây từng slice, mỗi slice qua 3 gates:

```
BUILD SLICE
    ↓
┌─────────────────────────┐
│ Code Simplification     │ ← Preserve behavior, clarity>cleverness,
│   (self-review)         │    follow conventions, scope to change
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│ 5-Axis Code Review      │ ← Correctness, Readability, Architecture,
│   (self-review)         │    Security, Performance
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│ FRESH Verification      │ ← Chạy test LẠI sau mỗi edit code,
│   (REQUIRED)            │    ko trust kết quả cũ cùng session
└───────────┬─────────────┘
            ↓
      NEXT SLICE (hoặc CHECKPOINT)
```

**Code Simplification principles:**
1. Preserve Behavior Exactly — ko đổi logic, chỉ đổi cách viết
2. Follow Project Conventions — style giống codebase
3. Prefer Clarity Over Cleverness — if/else > nested ternary
4. Maintain Balance — ko inline hết vào 1 hàm 200 dòng
5. Scope to Change — chỉ sửa file trong task

**5-Axis Review:**
- Correctness: edge cases handled? error paths?
- Readability: naming clear? control flow thẳng?
- Architecture: import existing helpers? module boundaries?
- Security: secrets ko log? input untrusted?
- Performance: unbounded loops?

**Fresh Verification rule:** Sau mỗi lần edit code, verification evidence phải được chạy lại từ đầu. Ko được nói "đã verify rồi" nếu kết quả cũ từ earlier trong cùng session. Chạy test command, đọc output, báo cáo pass/fail.

### Phase 4: HARDEN — Battle Test + A/B Test

**Battle test:** Stress test tối thiểu các edge cases:
- Valid input đủ field
- Missing optional field
- Input sai format hoàn toàn
- Tag có nhưng data rỗng
- Unicode/emoji
- Message siêu dài (5K+ chars)
- Duplicate detection
- State file corrupt
- Network timeout
- Token missing

**Telegram getUpdates conflict (409):** Bot API chỉ cho phép 1 getUpdates instance/lúc.
- Nếu watchdog + cron chạy đồng thời → 409 Conflict → retry với exponential backoff
- Watchdog dùng long-poll (timeout 60s) → cron ngắn (timeout 5s) → cron fail nhẹ, watchdog retry
- Tránh debug getUpdates bằng tay khi pipeline đang chạy (consume mất update)
- Khi cần debug: pause cron → kill watchdog → test → restart

**E2E test checklist (Telegram pipeline):** Trước khi deploy cron/watchdog, chạy:
1. [ ] dry-run: `--dry-run` parse sample OK
2. [ ] send test: gửi `[capture-sleep]` từ app Telegram → bot trả draft
3. [ ] approve: reply "ok" vào draft → bot xác nhận ghi vault + sync GSheet
4. [ ] skip: reply "skip" → bot xác nhận bỏ qua
5. [ ] bare ok: gõ "ok" KHÔNG reply → bot vẫn xử lý (fallback mode 2)
6. [ ] duplicate: gửi cùng ngày → bot báo "đã có trong vault", không spam
7. [ ] GSheet verify: check sheet có row mới
8. [ ] 409 conflict: cron chạy khi watchdog active → không crash (retry OK)

**A/B test:** Nếu automation thay thế workflow cũ:
- Chạy cả 2 path với cùng input
- So sánh output format
- Chỉ deploy khi format match

### Phase 5: VERIFY — Debugging & Error Recovery

Verify built-in recovery mechanisms:
- [ ] Network error handling (try/except + retry)
- [ ] Corrupt state file recovery (backup + reset)
- [ ] Atomic writes (.tmp → rename)
- [ ] Stale state cleanup (timeout)
- [ ] Input validation (source, format, content)
- [ ] Dedup (by date/key)
- [ ] Idempotent offset/state tracking
- [ ] Dry-run guard trên mọi mutation

**Bare "ok"/"skip" fallback mode:** User có thể reply "ok"/"skip" theo 2 cách:
1. Reply trực tiếp vào draft message (preferred) — `reply_to_message_id == proposal_msg_id`
2. Gõ "ok"/"skip" như tin nhắn riêng (fallback) — check text + pending state, KHÔNG check reply_to
- Cả 2 mode đều phải xử lý. Nếu chỉ support mode 1 → user gõ "ok" riêng → pipeline tắc.
- Nguy cơ: user vô tình gõ "ok" khi đang có pending → approve nhầm. Chấp nhận vì pending chỉ 1 và timeout.

**Duplicate spam protection:** Khi phát hiện duplicate date, chỉ gửi cảnh báo **1 lần/ngày**.
- Dùng ALREADY_NOTIFIED set (in-memory) để track date đã warn
- Tránh spam: nếu user gửi 20 lần cùng ngày → chỉ warn 1 lần
- Set reset khi restart process (in-memory, không persist)

### Phase 6: DEPLOY

1. Tạo cron job (schedule phù hợp)
2. Set deliver channel
3. Monitor 24h đầu — check logs, state files
4. OK → thông báo Warren
5. Ghi zone vào Delegation Zones

---

## Reference Architecture

Xem `references/telegram-poller-pattern.md` cho mẫu:
- Poll-based Telegram integration (ko webhook)
- Tag-based triggering (`[capture-sleep]`)
- State machine: IDLE → AWAITING_CONFIRM → (APPEND|EDIT|SKIP)
- Pending state file với timeout cleanup
- Atomic write cho state + offset tracking

---

## Boundaries

| Always | Ask First | Never |
|--------|-----------|-------|
| Hỏi từng câu + kèm gợi ý | Tạo cron job | Tự động ghi SOUL.md |
| Giải thích zone bằng tiếng Việt | Deploy skill | Auto-act zone 🔴 |
| Chạy test 1 lần trước khi deploy | Patch SOUL.md | Chạy cron trước khi test |
