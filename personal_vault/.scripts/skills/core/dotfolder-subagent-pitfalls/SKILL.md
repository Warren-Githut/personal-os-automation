---
name: dotfolder-subagent-pitfalls
description: "Subagent blinds dotfolder; rolling-window needs None-guard."
version: 1.0.0
author: Hermes
trigger: "Khi dispatch delegate_task review/debug file trong vault/.scripts/ HOẶC compute rolling-window metric (4-week avg, MoM, WoW) cho ops brief/dashboard."
category: core
tags: ['subagent', 'dotfolder', 'reviewer', 'rolling-window', 'pitfall']
related_skills: ['reviewer-node', 'code-review-and-quality', 'test-driven-development', 'using-agent-skills']
---

# Dotfolder Subagent Pitfalls + Rolling-Window Guard

> Class-level skill gom 2 lesson lặp lại từ session Warren-profile (phát hiện 2026-07-26). 2 skill bị curator off-limits (reviewer-node, code-review-and-quality, test-driven-development, using-agent-skills đều manually-authored) → gom vào đây để session sau vẫn có.

---

## 1. 🔴 SUBAGENT BLIND DOTFOLDER

`delegate_task` subagents (reviewer-node, code-review, simplify fan-out) **KHÔNG thấy `vault/.scripts/`** — dotfolder ẩn với cả `search_files` lẫn delegate agent's file tools.

**Failure thực tế (2026-07-26):** reviewer-node được gửi context `vault/scripts/cases_parser.py` (sai path, thiếu dấu chấm). Subagent search → `total_count: 0` → báo *"files don't exist anywhere"* → FALSE finding. Main agent almost trusted it.

**HARD RULE khi dispatch subagent review/debug:**
1. Context PHẢI truyền ABSOLUTE path: `C:/Users/khoans/Documents/Warren_OS_Local/vault/.scripts/<file>.py` (có dấu chấm).
2. Dặn subagent: *"Dùng terminal `ls` / `find` với path tuyệt đối trên để xác nhận file tồn tại trước khi review — đừng tin `search_files` trả rỗng."*
3. Nếu subagent VẪN claim file missing → orchestrator TỰ verify on disk (read_file / chạy script) và OWN findings. Subagent output là *suggestion*, không phải truth (theo `code-review-and-quality` Pitfall 2026-07-13).
4. Khi file đổi nằm trong dotfolder → **ưu tiên orchestrator tự chạy 5-trục review trực tiếp** thay dispatch subagent blind.

**Trigger mở rộng:** mọi file trong `vault/.*` (`.scripts/`, `.archives/`, `.accumulation/`, `.private/`, `._verify_tmp/`) đều blind với subagent. Luôn dẫn absolute path + verify trước.

### 1B. 🔴 MSYS PATH TRAP (cả main agent cũng dính)

Trên Windows git-bash (MSYS), `search_files` với path kiểu `/c/Users/khoans/...` (POSIX-style với drive letter) ĐÔI KHI fail với `IO error: The system cannot find the path specified (os error 3)` — ngay cả khi file tồn tại và main agent dùng `read_file` bình thường. Lỗi này xuất hiện cả ở main agent (không chỉ subagent).

**Symptom (2026-07-27):** `search_files(pattern='references/', path='/c/Users/.../ops-grabfood-cron/SKILL.md')` → `IO error (os error 3)` mặc dù file có thật. Cùng lúc `read_file` path đó OK.

**Giải pháp:**
- Dùng **terminal** `grep -rnE "pattern" path/` hoặc `ls path/` thay `search_files` khi gặp MSYS path error.
- Hoặc chuyển sang Windows native path `C:/Users/khoans/...` (có dấu hai chấm) — `search_files` chấp nhận tốt hơn POSIX `/c/...`.
- Khi verify file tồn tại để patch: luôn `read_file` (không depend `search_files`) — `read_file` dùng Windows path layer riêng, không dính MSYS trap.

**Lesson:** `search_files` là convenience tool, KHÔNG phải source of truth về file existence. Khi nó trả IO error trên path có vẻ đúng → verify bằng `read_file` hoặc `terminal ls` trước khi kết luận file missing.

---

## 2. 🔴 ROLLING-WINDOW GUARD (Min Data Window A5)

Khi compute rolling-window metric (4-week avg, MoM, WoW, WTD), value CHỈ meaningful khi đủ prior periods. Bug phổ biến: tính average qua các tuần CÓ mặt (vd chỉ 2/4 tuần) rồi display → vi phạm ANCHORS A5 + mislead (hiện "0.0M" giả).

**Correct pattern (TDD-worthy):**
- Chỉ compute khi `count >= required_window` (4 cho 4wAvg).
- Ngược lại set value = `None` (KHÔNG `0.0`) + display layer render `"—"`.
- Test PHẢI assert `value is None` (không `== 0.0`) khi `count < required`.
- Display guard check CẢ `count < required` VÀ `value is None` (defensive).

**Session example (2026-07-26, Ops Brief 4wAvg):** `compute_wtd_wow_mom` originally `w4_rev_mil = round(avg/1e6,1)` unconditional → store có 2 prior weeks hiện `4wAvg 0.0M, —` (trông như doanh thu 0). Fixed: `if w4_count >= 4: w4_rev_mil = round(...); else: w4_rev_mil = None`. Display: `w4_count < 4 or w4_y is None → "—"`.

**TDD lesson:** metric có data-window precondition → test MUST assert EMPTY/INSUFFICIENT case trả "no-data" sentinel (None/"—"), không số giả. Test chỉ check happy path sẽ pass trong khi bug misleading-number vẫn ship.

---

## 3. When to load this skill

- Dispatch `reviewer-node` / `code-review-and-quality` / `simplify-code` review parser trong `vault/.scripts/` → load trước để nhắc path tuyệt đối + verify-on-disk.
- Viết/sửa hàm tính rolling-window (4wAvg, MoM, WoW, WTD) → load để nhắc None-guard + TDD insufficient-case.

## 4. Integration

- `reviewer-node` SKILL.md Pitfalls nên link skill này (nhưng reviewer-node bị curator off-limits → note ở đây).
- `test-driven-development` Warren Ops Pitfall nên link skill này.
- Mọi parser skill mới (WARREN_MEMORY §): embed None-guard + TDD insufficient-case.
