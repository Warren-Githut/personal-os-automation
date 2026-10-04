---
name: vault-file-deprecate-merge
type: reference
description: SSOT consolidation — deprecate one vault file by merging its rules into another, archive-don't-delete, repoint active pointers, hardening verify, scoped 2-repo commit.
---

# VAULT-FILE DEPRECATE / MERGE (SSOT Consolidation)

Dùng khi Warren muốn **gộp nội dung 1 file vào file khác** và **xóa (deprecate) file cũ** — KHÔNG phải rename (path đổi). Ví dụ thực tế 2026-07-14: `RULES.md` → merge vào `SOUL.md` §5/§8, move `RULES.md` → `_archives/RULES_deprecated_2026-07-14.md`.

## Khác với rename
- **Rename** (`references/vault-file-rename-repoint.md`): path đổi → repoint mọi ref để không gãy link.
- **Deprecate/merge**: file cũ bị archive (không xóa hẳn), nội dung sống sót trong file mới. Ref cũ trỏ file cũ → phải repoint sang file mới (SOUL.md). Không có link gãy (vì file cũ đã archive) NHƯNG ref vẫn sai nếu để nguyên → dual-source drift tái phát.

## Quy trình (Warren approve zone 🔴 trước khi chạy)

### 1. Blast-radius scan (2 repos)
```bash
# Vault repo
cd C:/Users/khoans/Documents/Warren_OS_Local
grep -rln "RULES.md" --include="*.md" .

# Skills repo (SEPARATE git repo — KHÔNG commit chung)
cd C:/Users/khoans/AppData/Local/hermes/profiles/warren-profile/skills
grep -rln "RULES.md" --include="*.md" .
```
Phân loại refs:
- **Active pointer** (cần repoint): `canonical_rule:`, `see vault/RULES.md`, `read RULES.md đầu tiên`, `check RULES.md + AGENTS.md` trong checklist.
- **Historical/archive note** (GIỮ NGUYÊN): `RULES.md: Added X to pointer map` (ghi chép git history), archive files trong `_archives/memory/`. KHÔNG sửa — đó là lịch sử.
- **Deprecation note (cố ý thêm)**: ghi `RULES.md deprecated → SOUL.md` vào file mới để context tương lai.

### 2. Archive don't delete
```bash
cd C:/Users/khoans/Documents/Warren_OS_Local
git mv vault/RULES.md vault/_archives/RULES_deprecated_2026-07-14.md
```
Giữ lịch sử, không destroy. (Warren correction: 'xóa' = xóa hẳn, nhưng với SSOT file class-level → archive an toàn hơn; Warren chọn archive 2026-07-14.)

### 3. Repoint active pointers
- Vault files: AGENTS.md (canonical_rule + session-start), CONTEXT.md, pre_edit_checklist.md, WARREN_MEMORY.md.
- Skills files: vault-folder-rename SKILL + rename-checklist, vault-structure-audit (safe-rename B2/B5 + Rules root), ops-wiki-extra-hours (identity exception), tidy (critical-file example).
- Dùng `patch` tool, từng file, context đủ để unique. Tránh `replace_all` trên substring ngắn (double-substitution trap — xem rename reference).

### 4. HARDENING VERIFY (BẮT BUỘC trước commit)
```bash
# Confirm 0 active pointer còn sót (chỉ chấp nhận historical + deprecation notes cố ý)
grep -rn "canonical rule file.*RULES.md\|see \`vault/RULES.md\`\|read RULES.md đầu tiên\|RULES.md (canonical\|single source)" .
# → expect 0 matches
```
Nếu còn → repoint tiếp, chưa commit. Đây là bước tự-verify chống tái phát drift.

### 5. Scoped 2-repo commit
```bash
# Repo 1: Warren_OS_Local (vault edits)
cd C:/Users/khoans/Documents/Warren_OS_Local
git add <chỉ 5 files task này>   # KHÔNG git add -A — TODAY.md có pre-existing mod không thuộc task
git commit -m "refactor: consolidate RULES.md into SOUL.md (SSOT)"

# Repo 2: skills (SEPARATE repo)
cd C:/Users/khoans/AppData/Local/hermes/profiles/warren-profile/skills
git add <chỉ 6 skill files task này>
git commit -m "refactor(skills): repoint RULES.md references to SOUL.md"
```
**⚠️ 2 repos riêng biệt** — skill edits KHÔNG commit qua Warren_OS_Local git (lỗi "outside repository"). Commit ở skills repo.

### 6. Không push (Warren thích manual trigger, không auto-push)

## PITFALL — CRLF diff artifact
`patch` tool diff có thể render **toàn bộ file như changed** (vd WARREN_MEMORY.md: 680 insertions / 348 deletions) do line-ending `\r\n` vs `\n` khác biệt giữa source và target. **File trên disk vẫn NGUYÊN VẸN.**
→ LUÔN verify trên disk via `read_file` (kiểm tra frontmatter `---` đóng/mở 1 line, không dư trắng) thay vì tin diff rendering. Đừng hoảng sửa lại file vì tưởng hỏng.

## Router-vs-canonical drift (structure-audit finding)
Khi file router (AGENTS.md `canonical_rule:`) trỏ tới 1 file, nhưng file canonical (SOUL.md §6 session-start) **KHÔNG liệt kê file đó** → file đó thành dead pointer (không ai đọc).
→ Audit: cross-check AGENTS.md `canonical_rule` vs SOUL.md §6 list. Mọi file được AGENTS.md gọi PHẢI có mặt trong SOUL.md §6 (hoặc có reasons ghi chú). Phát hiện thực tế 2026-07-14: RULES.md bị cả 2 lệch → deprecate.
