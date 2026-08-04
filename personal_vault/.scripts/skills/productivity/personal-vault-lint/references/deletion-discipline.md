---
name: deletion-discipline
type: reference
---

# Deletion Discipline — Purge Retired Tools/Apps

Dùng khi Warren yêu cầu xóa triệt để một tool/app đã retire (vd: Kilo Code, Cursor). "Xóa" = xóa HẲN mọi dấu vết, KHÔNG giữ deprecated note.

## Quy trình 4 bước (triệt để)

1. **Quét filename** — quét CẢ dot VÀ underscore prefix (2 variant bắt buộc):
   - `*.kilo*` → bắt `.kilo/`, `.kilocode/`
   - `*_kilo*` → bắt `_kilo/` (**⚠️ dot-glob `*.kilo*` ONESELF KHÔNG bắt được `_kilo` — underscore là prefix khác**)
   - `*.cursor*`, `*_cursor*`
   Chạy `search_files(target=files, pattern=...)` riêng từng variant ở cả vault + home `C:/Users/khoans`.
   🔴 PITFALL (bị chính session 2026-07-09): chỉ dùng `*.kilo*` → LỌT `_kilo/` → user phải chỉ mặt. Luôn quét cả `_kilo*` và `.kilo*`.
2. **Quét content** — `search_files(pattern="kilo|cursor|Kilo|Cursor", file_glob="*.md")` trong mọi vault (Warren_OS_Local + Personal_OS).
3. **Quét hidden dirs** — `.kilocode/`, `.kilo/`, `_kilo/`, `.cursor/`, `.archive/kilo-*`.
4. **Quét logs** — activity log / weekly brief / retrospective entries nhắc tool đó. Cả dòng "X retired" note cũng là trace → xóa luôn.

## Kill the GENERATOR, not just the output (🔴 BẮT BUỘC)

Warren's literal instruction: *"parser/command/script nào generate thì remove phần generate đó"*. Xóa folder rác ≠ xong. PHẢI:
1. Tìm command/skill/script nào **viết** vào path đó (create file, append, prepend).
2. Neutralize đoạn generate: xóa bước tạo file, hoặc đổi đích sang path hợp lệ (vd `_kilo/memory/project_*.md` → `_ideas/generated_plans/project_*.md`).
3. Cả reference (đọc path đó) trong commands/skills → đổi sang source thay thế.
🔴 PITFALL (session 2026-07-09): xóa folder `_kilo/` xong tưởng xong, nhưng `review-plan.md` vẫn có step "Create `_kilo/memory/project_*.md`" → generate lại vào lần sau. Phải patch cả generate logic.

## Active auth.json provider-key removal (🔴 MỚI)
Retired tool có thể nằm trong **active** `auth.json` (`credential_pool.<provider>` key), khÔNG chỉ `.corrupt`.
- `.corrupt` → xóa file luôn (cache, an toàn).
- Active `auth.json` → KHÔNG xóa file. Chỉ **xóa riêng block provider** (vd `"kilocode": [...]`), giữ nguyên provider khác. Patch qua patch tool, sau đó **verify JSON valid + key gone** (python json.load).
- ⚠️ Credential file → vẫn tuân thủ cross-profile guard (file profile khác → hỏi user).
- ⚠️ `state-snapshots/*/auth.json` (pre-update backup) có block cũ → ĐỂ NGUYÊN (rollback point, khÔNG phải live).

## Re-scan confirmation (BẮT BUỘC trước khi báo xong)

Sau khi sửa/xóa xong → chạy LẠI full 4-step scan (filename cả 2 variant + content + hidden dirs + logs). Chỉ báo "sạch" khi KẾT QUẢ = 0.
- Nếu còn sót → phân loại: LIVE code (commands/skills/.md đang chạy) → sửa; HISTORY/CACHE (cron/output, sessions/*.json, auth.json.corrupt, provider cache) → ĐỂ NGUYÊN (xóa = nuốt log/lịch sử).
- Cross-profile: file thuộc profile khác (vd `warren-profile/skills/...`) → KHÔNG tự sửa, hỏi user (cross-profile guard).

## False-positive guard (QUAN TRỌNG)

Match string ≠ chính tool. Trước khi xóa, xác nhận PURPOSE của file:
- ❌ SAI: `Personal_OS/tmp_agent_skills/` có 17 dòng nhắc "Cursor" → tưởng là app Cursor mà xóa. Thực tế là **agent-skills framework TEMPLATE** (docs hướng dẫn tích hợp với nhiều IDE: Cursor, Claude Code, Copilot...). Xóa = nuốt thư mục template kỹ thuật.
- ✅ ĐÚNG: Chỉ xóa khi file THUỘC app đó (config, state, rules của Kilo/Cursor).

→ Khi nghi ngờ, đọc context xung quanh match trước khi act.

## No-commit rule

Sau khi xóa/sửa: chạy `git status --short` + `git diff --stat`, HIỂN THỊ cho Warren, rồi HỎI trước khi commit. Warren thường muốn review trước ("ko cho git gì luôn"). Chỉ commit khi anh bảo.

## Ví dụ thực tế (2026-07-09, Kilo/Cursor purge)

- ⚠️ **F94485F CHỈ TOUCH WARREN_OS_LOCAL.** Commit đó xóa `.kilocode/` `.kilo/` `_kilo/` `.cursor/` trong `Warren_OS_Local/` NHƯNG KHÔNG đụng `Personal_OS/personal_vault/_kilo/` (repo riêng, uncommitted) → folder này SỐNG SÓT đến 2026-07-09. Đừng tin "đã xóa từ commit X" → luôn re-scan disk thực tế.
- Content còn sót (Warren_OS_Local): WARREN_MEMORY.md (2 dòng note retired), weekly_briefs_log.md (activity log), CONTEXT.md (lesson "Roo→Kilo"). Profile SOUL.md (`applies_to` chứa "Kilo Code").
- Personal_OS: `_kilo/` folder vẫn còn → xóa `rm -rf` (uncommitted, không git-tracked).
- Đã sửa, re-scan DISK phát hiện `_kilo` còn sót tại Personal_OS → xóa tiếp. Git status Warren_OS_Local hiển thị 3 file, chưa commit (theo ý Warren).
- **Generator kill**: `review-plan.md` có step tạo `_kilo/memory/project_*.md` → đổi sang `_ideas/generated_plans/`. 9 commands/skills reference `_kilo`/`.kilo` → sửa hết reference (personal-context-update, personal-weekly-connections, ops-weekly-connections, review-plan, review-audit ×4, generate-plan, explore, personal-vault-lint SKILL, vault-structure-audit SKILL cross-profile).
- **auth.json**: 3× `.corrupt` → xóa. 2× active (`warren-profile`, `stock-profile`) → xóa block `"kilocode"` trong `credential_pool`, giữ provider khác. Verify bằng `python3 -c "import json; json.load(...)"` → cả 2 file valid, kilocode=False. `state-snapshots/*/auth.json` → để nguyên (backup).
- **Activity log**: user bảo "xóa cả ACTIVITY LOG luôn" → weekly_briefs_log.md dòng nhắc Kilo sprint + CONTEXT.md lesson "Roo→Kilo" → sửa/xóa.
