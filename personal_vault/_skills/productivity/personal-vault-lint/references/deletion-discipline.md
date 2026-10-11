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
🔴 PITFALL (vault rename 2026-07-14): `patch` với `replace_all` trên substring nằm trong absolute path DÀI → match "ăn" mất prefix chung. Vd file có `30_KNOWLEDGE_BASE/wiki/health/Genetics/...`; old=`wiki/health/Genetics/` → new=`02_Health/ac_Warren_Genetics_Report/` sinh ra `30_KNOWLEDGE_BASE/02_Health/...` (MẤT `/wiki/`). Fix: new_string phải GIỮ lại mọi segment vẫn hợp lệ → `wiki/02_Health/ac_Warren_Genetics_Report/`. Quy tắc: replacement phải tái-bao-gồm mọi đoạn còn đúng trong path mới; đừng để match nuốt prefix anh em. (Áp dụng cho mọi rename folder có link absolute path.)

## RESURRECTION DIAGNOSTIC — xóa rồi vẫn mọc lại (🔴 BẮT BUỘC trước khi báo "đã xóa vĩnh viễn")

Khi Warren nói "tôi xóa nhiều lần rồi mà nó vẫn ở đó" → có 1 trong 3 generator chưa bị neutralize. Phải tìm ĐỦ 3 trước khi commit xóa.

### Cause 1 — Git-tracked (phổ biến nhất)
Folder/file vẫn nằm trong git index → mỗi `git checkout` / `git restore` / commit re-add lại.
- Check: `git ls-files <path>` (non-empty = đang tracked). `git log --oneline -3 -- <path>` → nếu commit GẦN NHẤT re-add file (vd `b5faace` re-add `investing/`), đó là nguồn.
- Permanent triple (cả 3 bước):
  ```bash
  git rm -r --cached <path>   # xóa khỏi git index
  rm -rf <path>               # xóa disk
  git commit -m "chore: xoa <path> (duplicate/retired)"
  ```
  ⚠️ `rm -rf` ONESELF → git index còn → resurrect trên checkout/restore. `git rm` không commit → staged-uncommitted, chưa triệt để.
- Verify: `git ls-files <path> | wc -l` = 0; `find <path> -type f 2>/dev/null` = rỗng.

### Cause 2 — Cron / skill regenerate (nguy hiểm nhất, dễ sót)
Cron job active chạy skill có step HARDCODE tạo file vào path đó → mỗi kỳ chạy nó recreate + `git add` + commit.
- Check: `cronjob list` → lọc job có `workdir` = vault. Đọc SKILL.md của skill đó tìn step "Create/Update/Append `<path>`".
- 🔴 Cách bắt chắc nhất: `grep -rn "<path>" ~/.hermes/profiles/personal_profile/cron/output/*.md` → output log ghi rõ "3c. Update `_kilo/ACTIVITY_LOG.md`" + "created. Commit `5e33a98`". Đó là bằng chứng job nào regenerate.
- Fix: PHẢI patch skill SKILL.md (bỏ step hoặc redirect đích sang path hợp lệ, vd `_kilo/ACTIVITY_LOG.md` → `30_KNOWLEDGE_BASE/wiki/log.md` đã là active log). Chỉ xóa folder không patch skill → tuần sau mọc lại.
- Cron đã chạy xong (next_run tương lai) → sửa skill là đủ, không cần kill cron.

### Cause 3 — Script hardcode path
`.py` trong `scripts/` hardcode `VAULT_ROOT / "<path>"`.
- Check: `grep -rn "<path>" scripts/` → tìm `GENETICS_WIKI = VAULT_ROOT / "02_Health" / "ac_Warren_Genetics_Report"` class.
- Fix: sửa constant sang path mới. Verify: `python3 -m py_compile scripts/*.py` (exit 0 = OK).

### Decision tree
```
Warren: "xóa vĩnh viễn, không bao giờ hồi phục"
  → 1. git ls-files <path> ? tracked → git rm --cached + rm -rf + commit
  → 2. cronjob list + grep cron/output/<path> ? regenerate → patch skill
  → 3. grep scripts/<path> ? hardcode → sửa constant
  → 4. re-scan (deletion-discipline 4-step) = 0 → báo sạch
```

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
- `investing/` (2026-07-14): duplicate của `03_Investing/` (48 files active). User "xóa vĩnh viễn không bao giờ hồi phục". Root = git-tracked: commit `b5faace` re-add 3 files (`Frameworks.md`, `Candidates_Watchlist.md`, `Holdings.md`) → disk delete một mình hồi sinh. Fix = permanent triple (`git rm -r --cached` + `rm -rf` + commit). Verify `git ls-files`=0, `find`=none. 1 ref còn sót ở `stock-profile_pre_edit_checklist.md` nhưng path sai (`personal_vault/investing/GAS_thesis.md`) → không gãy.
- `_kilo/` (2026-07-14): legacy Kilo Code, retired 07-09. Root = 2 ACTIVE cron (`personal-weekly-connections`, `personal-context-update`) có Step 3c/Step 5 hardcode ghi `_kilo/ACTIVITY_LOG.md` + commit (commit `5e33a98` 07-13). Disk+git delete ONESELF → resurrect T2 tới. Fix = patch 2 skill redirect → `30_KNOWLEDGE_BASE/wiki/log.md` (đã là active log, cron 07-14 xác nhận OK). Bắt được qua `grep cron/output/*.md` thấy "created. Commit 5e33a98". Không cần kill cron (next_run 07-20, sửa skill đủ).
