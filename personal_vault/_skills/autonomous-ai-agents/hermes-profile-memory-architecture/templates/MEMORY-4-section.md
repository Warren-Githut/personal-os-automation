---
name: "Hermes Memory Template"
type: "memory_reference"
status: "active"
version: "YYYY-MM-DD"
created: "YYYY-MM-DD"
last_updated: "YYYY-MM-DD"
tags: [preferences, corrections, patterns, lessons-learned]
domain: "ops|trading|finance|..."
---

# MEMORY — Hermes Reference Knowledge

> **File này là REFERENCE — Hermes đọc đầu mỗi session để apply rules.**
> (raw log abolished 2026-08-30)
> Chỉ update sau `/compress-memory` + Warren approve.
>
> **Language:** Tiếng Việt (có dấu)
>
> **Hard rule:** Không bao giờ tin tuyệt đối vào LLM — luôn phải VERIFY trước khi trust output.

---

## Daily Memory Cycle (mọi session)

1. **Đầu session:** Hermes đọc MEMORY.md → apply Preferences / Corrections / Patterns / Lessons Learned
2. **Trong session:** Sau mỗi major task, Hermes internal check 3 câu:
   - Điều gì worked? → ghi chú để propose
   - Điều gì failed? → ghi chú để propose
   - Rule nào rút ra? → ghi chú để propose
3. **Cuối session / khi có lesson:** Hermes propose → Warren approve → **append vào `MEMORY.md`**

---

## Weekly Cycle (`/compress-memory`)

1. **Archive** — copy MEMORY.md cũ → `vault/_archives/memory/MEMORY_YYYY-MM-DD.md`
2. **Read** — đọc `MEMORY.md` hiện tại
3. **Distill** — "Identify patterns across all logged lessons. Distill into sharper, more general rules. Delete anything superseded. Goal: fewer, better rules."
4. **Propose** — show Warren bản draft MEMORY.md mới
5. **Apply** — Warren OK → ghi đè `vault/00_CORE_LOGIC/MEMORY.md`
6. **Clean raw** — (skip — raw log abolished)
7. **Push mem0** — hỏi Warren "có muốn push durable facts lên mem0 không?"
8. **Sync** — copy MEMORY.md sang profile
9. **Report** — "Đã distill X raw entries → Y rules. File cũ archived."

---

## Nguyên tắc chung

- Never duplicate entries. Rewrite existing rules when you learn something better.
- Archive before every cleanup.
- Never trust LLM output without verification. Cross-check before saving.

---

## Preferences

*Cách user muốn mọi thứ vận hành. Agent tuân thủ mặc định.*

- _(Ví dụ: Luôn pushback nếu thấy user ko hợp lý)_
- _(Ví dụ: Liteparse OCR first, fallback vision nếu fail)_

---

## Corrections

*Lỗi đã từng mắc + bài học rút ra. Agent không lặp lại.*

_(Còn trống — sẽ fill qua `/compress-memory`.)_

---

## Patterns

*Patterns quan sát được từ user hoặc operation. Agent chủ động apply.*

_(Còn trống.)_

---

## Lessons Learned

*Hard-earned lessons — từ data, từ sai lầm, từ phân tích.*

_(Còn trống.)_
