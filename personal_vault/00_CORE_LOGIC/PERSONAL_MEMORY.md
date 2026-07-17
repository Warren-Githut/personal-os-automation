---
name: "PERSONAL_MEMORY"
type: "memory_reference"
status: "active"
version: "2026-07-09"
created: "2026-07-01"
last_updated: "2026-07-09"
tags: [preferences, corrections, patterns, lessons-learned]
domain: "personal"
---

# MEMORY — Personal Profile Reference Knowledge

> **SSOT — Single Source of Truth duy nhất cho personal_profile.** Mọi thứ đều đọc từ file này.
> Raw lessons log ở `personal_vault/_inbox/_personal_memory_raw.md` (append-only, newest đầu).
> Chỉ update sau `/compress-personal-memory` + Warren approve.
>
> **Auto-sync (read-only):** Hermes đọc file này đầu mỗi session → apply rules.
> **Built-in memory** (`memory` tool) auto-saves mặc định — Hermes tự động ghi nhớ facts durable.
>
> **Built-in memory là cache tạm — KHÔNG phải SSOT.** Mất built-in memory không sao,
> mất PERSONAL_MEMORY.md là mất tất cả. Warren chỉ cần sửa file vault là đủ.
>
> ⚠️ **2 MEMORY STORES — distinct (Warren 2026-07-09):**
> - **(a) Hermes built-in memory** = `memory` tool = **HARD 2,200-char WRITE CAP**. Hermes **tự do prune stale + add mới khi đầy** (Warren KO ý kiến, native management). **ANTI-LOOP (chỉ cho b):** KHÔNG loop xóa entry (a) để nhét content (b) — (b) push qua Python script riêng, không qua `memory` tool.
> - **(b) mem0 FAISS local** = **SEPARATE, UNLIMITED** store. **CHỈ ghi khi Warren chạy `/compress-memory`** (distill raw → mem0). Hermes KHÔNG ghi mem0 trực tiếp. mem0 không bao giờ đầy.
> - `_personal_memory_raw.md` = SSOT unlimited (append-only). /compress-memory distill → PERSONAL_MEMORY.md + push mem0 (b).
>
> **Language:** Tiếng Việt (có dấu)
>
> **Lưu ý:** warren-profile (tên cũ của personal_profile trên Hermes) có SSOT riêng tại `Warren_OS_Local/vault/00_CORE_LOGIC/WARREN_MEMORY.md` — KHÔNG nhầm với file này. Khi conflict, vault SSOT tương ứng thắng built-in memory.
> **Hard rule:** Không bao giờ tin tuyệt đối vào LLM — luôn phải VERIFY trước khi trust output.

---

## Per-Session Memory Cycle

1. **Đầu session:** Hermes đọc PERSONAL_MEMORY.md → apply Preferences / Corrections / Patterns / Lessons Learned
2. **Trong session:** Sau mỗi major task, Hermes silent internal check 3 câu:
   - Điều gì worked? → ghi nhớ để propose
   - Điều gì failed? → ghi nhớ để propose
   - Rule nào rút ra? → ghi nhớ để propose
   > Không nói ra. Không propose giữa chừng.
3. **Cuối session — trigger = `git commit`:** Khi Warren commit (bất kỳ repo nào), Hermes check:
   - Có lessons ghi nhớ từ bước 2? → nếu có → propose cho Warren
   - Warren nói "ghi" → append vào `personal_vault/_inbox/_personal_memory_raw.md` ngay
   - Không có lessons → im lặng, không spam
   > Git commit là deterministic trigger duy nhất. 100% session có check, không bỏ sót, không hên xui.

---

## Monthly Cycle (`/compress-personal-memory`)

Warren chạy `/compress-personal-memory` ~1 lần/tháng hoặc sau 3-4 sessions:

1. **Archive** — copy PERSONAL_MEMORY.md → `_archives/memory/PERSONAL_MEMORY_YYYY-MM-DD.md`
2. **Read** — đọc `personal_vault/_inbox/_personal_memory_raw.md` + PERSONAL_MEMORY.md hiện tại
3. **Distill** — gộp raw lessons vào PERSONAL_MEMORY.md, xóa trùng, sharpen rules
4. **Propose** — show Warren draft PERSONAL_MEMORY.md mới
5. **Apply** — Warren OK → ghi đè `00_CORE_LOGIC/PERSONAL_MEMORY.md`
6. **Clean raw** — clear `personal_vault/_inbox/_personal_memory_raw.md`
7. **Ontology reconcile** — scan toàn vault `type:` values + cây folder vs `00_CORE_LOGIC/PERSONAL_ONTOLOGY.md` (personal-domain types) → diff → propose node type/edge mới hoặc drift → Warren OK → update PERSONAL_ONTOLOGY.md + ghi `## 🔄 Reconciliation Log`. (Borrow từ bài ontology-constrained memory: schema phải scan định kỳ để không lệch thực tế.)
8. **Push mem0** — hỏi Warren "có push durable facts lên mem0 không?"
9. **Report** — "Đã distill X raw entries → Y rules. Ontology reconciled (N diff). Archive tại _archives/memory/."

---

## Nguyên tắc chung

- Never duplicate entries. Rewrite existing rules when you learn something better.
- Archive before every cleanup.
- Mọi data point phải cite source — xem SOUL.md Data quality tags.
- Không bao giờ tin tuyệt đối vào LLM output — luôn VERIFY trước khi trust.
- **[2026-07-09] User rule — NEVER TRUST LLM, verify everything:** Sau LLM parse Excel/PDF/CSV → BẮT BUỘC 2nd source fact-check. Enforced qua skill verify-parser-output. Parser output không có verify report = UNTRUSTED.

---

## Write Governance

**HARD RULE:** Hermes không tự động write vào: **PERSONAL_MEMORY.md, PERSONAL_USER.md, hay mem0 (b).**
> **Built-in memory (a)** (`memory` tool) = Hermes tự do quản lý, Warren không can thiệp.

Mọi proposed write phải qua **2 gates**:

| # | Gate | Nếu NO → |
|---|------|----------|
| 1 | **7 ngày nữa thông tin này còn đúng và có giá trị không?** | SKIP |
| 2 | **Đây là durable fact (preference/decision/config/lesson), hay task artifact?** | Nếu artifact → SKIP |

Chỉ WRITE khi:
1. **Direct command** — Warren nói "lưu", "nhớ giùm", "ghi vào memory" → execute ngay
2. **End-of-session proposal** — Hermes proposes lessons → Warren approves → **append vào `personal_vault/_inbox/_personal_memory_raw.md`**
3. **PERSONAL_USER.md update** — Hermes phát hiện preference mới → propose → Warren approve → ghi
4. **`/compress-personal-memory`** — distills raw → proposes PERSONAL_MEMORY.md edits → Warren approve → WRITE + SYNC mem0 (b)

---

## Preferences

*Cách Warren muốn mọi thứ vận hành trong personal context. Hermes tuân thủ mặc định.*

- **[2026-07-09] Memory model 2-store:** (a) Hermes built-in (`memory` tool, 2200 cap) = Hermes tự do prune stale + add mới (native, Warren KO ý kiến). (b) mem0 FAISS local = separate unlimited, CHỈ `/compress-memory` ghi. SSOT = `_personal_memory_raw.md`. ANTI-LOOP: KHÔNG loop xóa entry (a) để nhét (b) — (b) push qua Python, không qua `memory` tool.
- **[2026-07-09] Agent surface = Hermes Desktop ONLY.** Kilo Code / Cursor retired triệt để (không git). Đã rửa: 3× auth.json.corrupt, 2× auth.json live (xóa block kilocode), Personal_OS/_kilo folder, 9 commands/skills reference, SOUL/WARREN_MEMORY/CONTEXT/weekly_briefs_log. Giữ nguyên: state-snapshots, cron/output, sessions (history/rollback).
- **[2026-07-03] Divorce finalized** — QĐ 575/2026/QĐST-HNGĐ (25/6/2026). Cấp dưỡng GG 11M/tháng, ngày 10 DL. GG ở với Khanh. Warren có quyền thăm nom. Calendar recurring đã set.

---

## Corrections

*Lỗi đã từng mắc (personal mistakes, workflow errors) + bài học rút ra. Hermes không lặp lại.*

- **[2026-07-09] Underscore-prefix scan miss:** Quét deletion lọt `_kilo` vì pattern `.kilo` (dot). Luôn scan BOTH dot-prefix (`.kilo`, `.kilocode`, `.cursor`) VÀ underscore-prefix (`_kilo`, `_archive/kilo-*`) ở vault + home + profile dirs.
- **[Setup] Personal domain ban:** Lần đầu setup personal_profile thiếu HARD RULE "personal domain cấm stock" ở SOUL.md → bổ sung sau lint. Luôn lint SOUL sau edit.

---

## Patterns

*Patterns quan sát được từ đời sống hoặc Warren approach. Hermes chủ động apply.*

*(Còn trống — fill dần khi có patterns mới.)*

---

## Lessons Learned

*Hard-earned lessons — từ health, family, workflow.*

- **[2026-07-09] Purge legacy tool protocol:** Phân biệt LIVE config (auth.json, commands/*.md, skills/*/SKILL.md — sửa/xóa) vs HISTORY/CACHE (cron/output/*.md, sessions/*.json, state-snapshots/* — để nguyên, xóa=nuốt rollback). Reference docs nhắc tool (deletion-discipline.md, hermes-agent SKILL bảng provider) cũng để nguyên vì đúng mục đích.
- **[2026-07-03] Memory architecture:** PERSONAL_MEMORY.md = SSOT vault file; built-in memory = cache tạm (mất không sao). Hermes đọc SSOT đầu session. 4 file riêng biệt: SOUL (identity/rules) | USER (đối tượng) | MEMORY (bộ nhớ) | AGENT (access/boundaries) — ko gộp.
- **[2026-07-03] Divorce case closed:** QĐ 575/2026/QĐST-HNGĐ. Cấp dưỡng GG 11M/tháng ngày 10 DL. Calendar recurring. QĐ lưu vault/legal/.
