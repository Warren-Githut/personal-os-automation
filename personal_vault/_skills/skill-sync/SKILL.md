---
name: skill-sync
description: "Sync 1 skill từ AppData (nơi Bố patch) → vault SSOT (.scripts/skills) + archive + git commit/push. Chạy được từ mọi profile (warren/stock/personal). Trigger: 'skill-sync <skill-name>' hoặc 'sync <skill-name>'."
version: 1.0.0
tags: [skill, sync, backup, git, ssot]
disable-model-invocation: true
---

# skill-sync

> Đồng bộ 1 skill Bố vừa patch ở AppData → két sắt git (vault `.scripts/skills/`) + backup `_archives/skills/` + push GitHub.
> **Chạy từ bất kỳ profile nào** (warren / stock / personal) — skill tự detect profile hiện tại và resolve đúng vault + repo.

## Trigger
```
skill-sync <skill-name>     → đồng bộ skill đó
sync <skill-name>           → alias, y hệt
skill-sync --help           → in hướng dẫn
```
Ví dụ: `skill-sync stock-ingest` (từ warren, stock, hay personal đều được).

## Hard rules (KHÔNG đụng)
- SOUL §5 Skill SSOT Sync Gate + Skill Archive Gate = guardrail. Skill này là thực thi của 2 gate đó.
- SSOT = vault `.scripts/skills/<name>/SKILL.md`. KHÔNG sửa AppData trực tiếp làm nguồn. Copy 1 chiều SSOT → AppData.
- Commit vào repo của **profile đang chạy** (warren→warren-os-lusine, stock→warren-os-lusine do symlink, personal→personal-os-automation). KHÔNG bao giờ commit sang repo profile khác.
- Archive vào `<vault>/_archives/skills/<name>_SKILL_backup_YYYY-MM-DD.md`.

## Process (6 bước, mỗi bước có completion criterion)

### Step 1 — Detect profile + resolve paths
Xác định profile hiện tại từ `HERMES_PROFILE` env hoặc path `AppData/Local/hermes/profiles/<X>`.
Resolve:
- `APP_SKILLS` = `C:/Users/khoans/AppData/Local/hermes/profiles/<X>/skills/`
- `VAULT_SSOT` + `VAULT_ARCHIVE` + `GIT_REPO` theo bảng:

| Profile | APP_SKILLS (vật lý) | VAULT_SSOT | VAULT_ARCHIVE | GIT_REPO |
|---------|---------------------|------------|---------------|----------|
| warren-profile | warren-profile/skills | Warren_OS_Local/vault/.scripts/skills | Warren_OS_Local/vault/_archives/skills | warren-os-lusine (master) |
| stock-profile | warren-profile/skills (symlink) | Warren_OS_Local/vault/.scripts/skills | Warren_OS_Local/vault/_archives/skills | warren-os-lusine (master) |
| personal_profile | personal_profile/skills | Personal_OS/personal_vault/.scripts/skills | Personal_OS/personal_vault/_archives/skills | personal-os-automation |

*Note: stock-profile skills là symlink → vật lý nằm ở warren-profile/skills. Nên SSOT + repo = warren.*

**Completion:** Đường dẫn 4 biến đã xác định và `APP_SKILLS/<name>` tồn tại. Nếu `<name>` không có trong APP_SKILLS → DỪNG, báo Bố "skill <name> không tồn tại ở profile <X>".

### Step 2 — Ensure SSOT dir exists
Nếu `VAULT_SSOT/<name>` chưa có → `mkdir -p`. Với personal mà `personal_vault/.scripts` chưa có → tạo luôn (`mkdir -p personal_vault/.scripts/skills`).
**Completion:** `VAULT_SSOT/<name>` tồn tại.

### Step 3 — Copy skill AppData → SSOT (1 chiều)
`cp -r APP_SKILLS/<name>/. VAULT_SSOT/<name>/`
**Completion:** `diff -rq APP_SKILLS/<name> VAULT_SSOT/<name>` → IDENTICAL. Không identical → DỪNG, báo lỗi.

### Step 4 — Archive backup
`cp APP_SKILLS/<name>/SKILL.md VAULT_ARCHIVE/<name>_SKILL_backup_YYYY-MM-DD.md`
(Dùng ngày hiện tại YYYY-MM-DD.)
**Completion:** File archive tồn tại trong VAULT_ARCHIVE.

### Step 5 — Git commit + push (repo của profile)
```
cd <VAULT_ROOT> && git add VAULT_SSOT/<name> VAULT_ARCHIVE/<name>_SKILL_backup_*.md
git commit -m "backup: <name> SSOT synced + archive YYYY-MM-DD"
git push origin <branch>
```
Branch: warren=master, personal=master (verify `git branch` nếu không chắc).
**Completion:** `git ls-files VAULT_SSOT/<name>/SKILL.md` trả về path (đã tracked remote). Push không lỗi.

### Step 6 — Print token + report
In dòng: `📦 ARCHIVE: ✅ <name>` + tóm tắt (profile, repo, commit hash ngắn).
In `✅ GATES: sync✓ archive✓` vào cuối.

## Pitfalls
- **Quên detect profile** → commit nhầm repo (warren sang personal). Fix: Step 1 BẮT BUỘC resolve bảng, không hardcode.
- **Symlink stock** → tưởng stock có skills riêng. Fix: stock-profile = warren vật lý, SSOT luôn về warren.
- **personal chưa có .scripts** → cp fail. Fix: Step 2 tự mkdir.
- **Bố patch chưa xong đã sync** → copy bản dở. Fix: Bố chỉ gọi sync khi đã sửa xong.
- **AppData không phải SSOT** → nếu sau này sửa trực tiếp SSOT quên sync ngược, AppData cũ. Fix: luôn coi AppData là "bản làm việc", SSOT vault là "bản thật".

## Verify (bắt buộc trước báo xong)
- `diff -rq` AppData vs SSOT = IDENTICAL.
- `git ls-files` SSOT/SKILL.md có trên remote.
- Archive file tồn tại.
Thiếu 1 trong 3 → chưa xong, báo Bố.
