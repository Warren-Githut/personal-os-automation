---
---name: tidy
description: Vault organizer — inbox triage, case archiving, deprecated folder cleanup, wiki health.
version: 1.7.0
trigger: /tidy
category: vault
tags: ['tidy', 'cleanup', 'archive', 'inbox', 'organize']
related_skills: ['ruthless']
---
---

# /tidy

Vault health maintenance with safety gates.

## 🚫 Governance Rules (Warren-enforced)

### Rule 1: NEVER auto-create vault folders/files without approval
- **Hermes không được tự động tạo bất kỳ folder/file mới nào trong `vault/`** nếu chưa được Warren xác nhận.
- Phải present path suggestion + content → wait for "approved" → then create.
- Exceptions:
  - `_inbox/` items (fleeting, user-intended drop zone)
  - `10_OPERATION_DATA/` log entries from parsers (already approved per parser contract)
- If unsure → present options + tradeoffs → ask → wait.
- Rationale: Warren muốn vault sạch, không folder rác từ agent cũ (ORION, Kilo Code) hay plugin auto-clip.

### Rule 1-b: Wiki write protection (STOCK_MEMORY.md Rule #6)
- **KHÔNG ghi bất kỳ file nào vào `30_KNOWLEDGE_BASE/wiki/`** nếu không có lệnh hoặc approval trực tiếp từ Warren.
- Mọi analysis output phải được Warren approve trước khi write vào wiki.
- Applies to tidy output too — if cleanup analysis belongs in wiki/, present + wait for approval first.

### Rule 2: Prefer dot-prefix for hidden folders
- Folder cần ẩn khỏi Obsidian → đặt tên bắt đầu bằng dấu chấm (`.private/` thay vì `_private/`).
- Obsidian tự động ẩn dot-folders khỏi **file explorer tree** — KHÔNG cần setting, KHÔNG cần plugin.
- **⚠️ `userIgnoreFilters` (Settings → Excluded files) KHÔNG ẩn khỏi file tree** — chỉ ẩn Search/Graph/Unlinked Mentions. Đừng lead với userIgnoreFilters khi Warren muốn "ẩn folder khỏi cây". Dùng dotfolder. (Detail: skill `obsidian-vault-hygiene`.)
- **Update script paths sau khi rename** — bulk `.replace(old, new)` trong `.py`/`.md`/`.json` (Python script, không sed). `Path(__file__).resolve()` tự theo, nhưng string literals trong 17+ file vault phải sửa.
- **`__pycache__` prevention:** nếu folder chứa script chạy → Python regen `__pycache__/` (non-dot) sau rename. Thêm `import sys; sys.dont_write_bytecode = True` vào scripts + `.gitignore` với `__pycache__/`.
- **Verify bằng liteparse nếu Warren gửi screenshot Obsidian** (vision có thể fail 402): liteparse OCR đọc UI text → confirm behavior thực tế.

## 🧭 Warren's Vault Principle

**Non-friction, minimal cognitive load.** Khi phân vân về giá trị của file/folder — DELETE. Zero tolerance for clutter. Warren không muốn nhớ cấu trúc vault phức tạp. Nếu một folder không có chức năng rõ ràng hoặc nội dung có thể suy luận từ chỗ khác → xoá.

**Clean-sweep rule:** Delete + grep vault-wide + patch broken refs in one pass. Không bỏ sót reference chết.

## Sub-modes

### 1. Inbox triage
Route `_inbox/` items to correct locations via `/ops-ingest` and `/ops-process-notes`.

### 2. Case archiving
Close stale cases, move `_cases/active/` → `_cases/closed/`, rebuild index.

**Frontmatter fields required when closing:**
```yaml
status: closed
updated: YYYY-MM-DD
closed_date: YYYY-MM-DD
resolution: "Short summary of why closed and outcome"
```
- Remove `follow_up` / `followup_date` field (no longer needed)
- Update `file_path` in CASES_INDEX.md to point to `_cases/closed/`
- Add `closed_date` and `resolution` to the CASES_INDEX.md YAML entry

**Workflow:**
1. Update the case file frontmatter (status→closed, add closed_date + resolution)
2. `mv _cases/active/<slug>.md _cases/closed/<slug>.md`
3. Update CASES_INDEX.md: status→closed, file_path→closed/, add closed_date + resolution
4. Bump CASES_INDEX.md `last_updated`

## 3. 🧹 Deprecated agent folder cleanup (e.g. `_kilo/`, `_roo/`)

**When:** An old agent folder exists and you want to delete it safely.

**Workflow:**

1. **Inventory files** — `ls -la vault/_kilo/` (or target folder). List every file + subdir.
2. **Audit references** — for EACH file, search the vault for active references:
   ```
   search_files path=vault pattern=<filename>
   ```
   Also check cron jobs (`cronjob action=list`), scripts, configs.
3. **Categorize:**
   - ❌ **No active refs** → safe to delete
   - ⚠️ **Active refs → code/docs** → patch code first, then delete
   - 🔶 **Active refs → live data** → move to appropriate location first
4. **Patch code before delete** — if orchestrator scripts/parsers reference files in the deprecated folder:
   - Remove function calls referencing those files
   - Remove corresponding import/path constants
   - Verify syntax (`ast.parse` or run `python3 -c "import ast; ast.parse(...)"`)
5. **Propose move path for live files, get confirmation** — user preference: Warren wants path suggestion presented for approval before moving (e.g. `_kilo/ACTIVITY_LOG.md` → `_cases/case_activity_log.md`). Don't move silently — suggest, wait for "approved", then execute.
   - After confirmation: `mv` file + update path constant in referencing scripts
   - Verify new path exists, old path reference zeroed
6. **Update cross-references** — scan for doc references to old folder path (e.g. grep for `_kilo/`):
   ```
   search_files path=vault pattern=_kilo/ target=content
   ```
   Update per-profile context: `00_CORE_LOGIC/STOCK_CONTEXT.md` (stock) or `00_CORE_LOGIC/PERSONAL_CONTEXT.md` (personal), `_cases/README.md`, etc. Also check history/idea/log files — fix or acknowledge as stale.
7. **Delete — use PowerShell, NOT MSYS `rm -rf`** for git-tracked directories on Windows:
   ```bash
   # ✅ Reliable — native NTFS, no MSYS caching
   powershell.exe -Command "Remove-Item -Path '_kilo' -Recurse -Force"
   # Fallback:
   cmd.exe /c "rmdir /S /Q _kilo"
   ```
   **Do NOT rely on MSYS/git-bash `rm -rf`** — it can appear to succeed (exit 0, echo "DELETED") while NTFS still holds cached handles, causing files to reappear after commit. If `ls` shows the directory still exists after `rm -rf`, switch to PowerShell immediately.
   
   **After deletion:** `ls target_dir 2>&1` should show "No such file or directory".

8. **Git commit — use `git add -A`, not `git add -u`:**
   ```bash
   git add -A && git commit -m "chore: remove deprecated _kilo/ folder" && git push
   ```
   **Why `git add -A`:** `git add -u` only stages changes to already-tracked files. When Windows/MSYS caches recreate files between delete and stage, `git add -u` misses them. `git add -A` stages everything (deletions, new files, re-deletions) in one shot.
   
   **Potential 2-pass reality:** If files reappear on disk after first commit (Windows handle caching), run PowerShell delete + `git add -A` + commit again. This is normal — the first commit records the batch deletion, but stale NTFS handles may recreate a few survivors that need a second pass.
   
   **⚠️ Watch out for `git add -A` re-adding Windows-restored files:** If deleted files were auto-restored by Windows (or remotely-save plugin), `git add -A` will pick them up as new files and create them again in the index. Before committing deletion, ALWAYS check `git status --short` for unexpected untracked files. If stale files were re-added:
   ```bash
   git rm --cached <path>       # remove from index
   # then add to .gitignore and commit
   ```
   
   **After push, verify:** `ls target_dir 2>&1` and `git status --short target_dir/` — both should show directory gone and no pending changes.

9. **Verify cleanup** — search vault-wide for old folder path string, confirm zero matches:
   ```
   search_files path=vault pattern=_kilo/ target=content file_glob=*.md
   ```
   If any survive, patch them. Zero tolerance.

**Ad-hoc verification pattern (system requirement):**
After code edits (no canonical test suite), the system will demand verification. Always comply with this pattern:

- **Code edits (.py, .json, .yaml, scripts):**
  1. Create temp script: `AppData/Local/Temp/hermes-verify-<topic>.py`
  2. Check: old function names/constants gone, new syntax valid, cross-refs updated, vault-wide zero stale references
  3. Run via `python3`
  4. Clean up temp file (`rm`)
  5. Report as "Ad-hoc verification PASSED" (not suite green)

- **Markdown-only edits (wiki links, docs, pulse logs):**
  No test runner exists. Run manual verification instead:
  1. `ls <deleted-folder> 2>&1` → confirms directory gone
  2. `search_files path=vault pattern=<deleted-folder>/ file_glob=*.md` → zero matches
  3. Report: "Verification passed. No test suite for markdown — 2 manual checks confirmed."

**Fast-path for repeated verification requests:** If system demands verification again for the same edit batch (files already verified), use inline `python3 -c "..."` for code edits or the 2-line manual check for markdown edits.

**Pitfalls:**
| Pitfall | Fix |
|---------|-----|
| Cron job references file in deprecated folder | Remove/update cron job first, or patch script it calls |
| File is referenced by multiple scripts | Search ALL refs across vault, not just one file |
| ACTIVITY_LOG or Kanban files are still live | Move to `_cases/` or appropriate location, update path constant in scripts |
| Path proposal — don't move without confirmation | Present path choice first, wait for "approved" |
| MSYS `rm -rf` deletes but files reappear | Use PowerShell `Remove-Item -Recurse -Force`. If reappear after commit, do second pass with `git add -A` |
| `git add -u` misses recreated files | Use `git add -A` for cleanup commits (catches re-deletions and new files) |
| `git add -A` may re-add Windows-restored files | Check `git status --short` before committing; use `git rm --cached` to undo |
| System asks for verification repeatedly | First time: temp script. Repeated times: inline `python3 -c "..."` fast-path |
| Windows auto-restores deleted files | Delete via PowerShell, then add filenames to `.gitignore` — even if Windows recreates them, git won't track. Run `git rm --cached` if they were accidentally re-added by `git add -A`. Full pattern set discovered across cleanups: `_kilo/`, `Clippings/`, `_drafts/`, `_inbox/tasks.md`, `_hermes_vault_index.md`, `README.md`, `USER_GUIDE.md`, `tests/`, `labour_costs/`, `docs/`, `skills/`, `99_HERMES_AGENT_WORKSPACE/` |
| Stale skill copies in vault | If `vault/skills/` exists, it's a stale copy (real skills in `~/.hermes/profiles/*/skills/`). Delete vault copy, don't maintain it. Confirm with Warren first. |
| **Remotely Save plugin restores deleted files** | Before bulk-deleting tracked files, check `vault/.obsidian/community-plugins.json` for `remotely-save`. If active, the plugin syncs vault to cloud (S3/WebDAV) and will restore deleted files from remote. **Fix:** Temporarily remove `remotely-save` from `community-plugins.json`, delete files, re-add plugin after. Or disable plugin in Obsidian settings before cleanup. |
| **`99_HERMES_AGENT_WORKSPACE/` contains live pre_edit_checklist.md** | Before nuking this folder, **copy** `templates-checklist/pre_edit_checklist.md` to `00_CORE_LOGIC/pre_edit_checklist.md` first. Update SOUL.md path. Then delete the rest. |
| Critical file protection | Add visible `⚠️ KHÔNG XOÁ` warning at top of critical files (e.g. `SOUL.md`) so Warren doesn't accidentally delete them. Renaming would break references, so a warning in the file itself is safer. |

### 3b. 🗑️ General vault folder deletion (non-agent, non-special)

**When:** A folder exists but is NOT a standard vault folder (i.e. not in the canonical structure from AGENTS.md) and NOT a deprecated agent folder (`_kilo/`, `_roo/`). Examples: `docs/`, `tests/`, `_tmp_broker/`, random loose folders.

**Non-friction rule:** Warren wants ZERO folders he has to remember. If a folder has no clear function in the standard vault architecture → delete. If the content can be inferred or reconstructed from other sources → delete. "Đỡ nhớ" is the goal.

**Workflow:**

1. **Check vault architecture** — does the folder appear in `AGENTS.md`'s canonical structure? If yes → keep (it's standard). If no → candidate for deletion.

1.5 **Duplicate check** — before assessing content, verify the folder isn't a stale duplicate of another folder:
   - Look for similarly named folders (e.g. `investing/` vs `03_Investing/`, `00_INDEX.md` vs `00_WIKI_INDEX.md`)
   - `diff -r <candidate> <other>` to compare contents — flag identical or near-identical copies
   - Check which folder has more files / more recent `last_updated` in file frontmatter
   - **Search vault references for BOTH paths** — the copy with zero active references is stale
   - Only delete the stale copy; confirm the surviving folder has all content + all references

2. **Inventory** — what's inside?
   ```bash
   search_files path=vault/<folder> pattern=* target=files
   ```

3. **Assess value:**
   - ❌ **Empty** → delete directly
   - ❌ **Planning/Spec docs for completed work** → delete (historical value is negative — Warren doesn't want to remember dead plans)
   - ❌ **Old tests from TDD cycle** → delete if no one runs them (`scripts/` still works without test suite)
   - 🔶 **Has unprocessed data** → move to correct location (e.g. `_inbox/01_unprocessed/`), then delete folder

4. **Pre-deletion triage for non-empty folders:**
   ```
   ┌──────────────────────────────────────────────────────────────┐
   │ Has live content that doesn't belong in a standard location? │
   ├──────────┬───────────────────────────────────────────────────┤
   │ YES      │ Move to appropriate standard path first.          │
   │          │ Example: inbox-notes/ → 01_unprocessed/           │
   ├──────────┼───────────────────────────────────────────────────┤
   │ NO       │ Delete directly. No friction.                     │
   └──────────┴───────────────────────────────────────────────────┘
   ```

5. **Delete:**
   ```bash
   rm -rf vault/<folder>
   ```

6. **Post-delete link audit** — grep vault for broken wiki links now pointing to deleted folder:
   ```bash
   search_files path=vault pattern=<folder-name>/ target=content file_glob=*.md
   ```
   Patch any matches. Zero tolerance.

7. **Verify:**
   ```bash
   ls vault/<folder> 2>&1   # should show "No such file or directory"
   grep -r "<folder-name>/" vault/   # should return zero
   ```

**Pitfalls:**

| Pitfall | Fix |
|---------|------|
| Content is useful but folder is non-standard | Move content to standard location (e.g. unprocessed files → `01_unprocessed/`), then delete folder |
| Planner/spec for something NOT yet done | Ask Warren — don't auto-delete unexecuted plans |
| User says "delete hết luôn được ko" | This is a YES signal. Confirm understanding, then move any live files first, delete clean. |
| Broken wiki links after deletion | **Always grep post-delete.** Pulse logs and wiki files often link to deleted folders. |
| `FRONTMATTER_CACHE.json` giữ entry stale của file wiki vừa xóa | Xóa file/folder wiki → search `FRONTMATTER_CACHE.json` bằng CẢ tên cũ VÀ tên mới (cache thường lag tên thực, vd folder rename thành `09_connections/` nhưng cache vẫn ghi `wiki/_connections/...`). Xóa block JSON tương ứng. Quên bước này → cache reference treo. |

### 4. 🔒 `_private/` credential folder — hide from Obsidian

**When:** A `_private/` or similar folder contains credential JSONs (service account keys, OAuth secrets) and you want to hide it from Obsidian while keeping it accessible to scripts.

**Three approaches — use Option A for new deployments:**

#### Option A: Rename to dot-prefix folder (reliable, no Obsidian settings needed)

Obsidian **naturally hides** any folder starting with a dot (`.private/`, `.credentials/`, etc.) on all platforms. No settings to toggle.

**Workflow:**

1. **Inventory** — `ls -la vault/_private/` — note each file
2. **Check active refs** — for EACH file, search vault scripts:
   ```
   search_files path=scripts pattern=<filename-tail> target=content file_glob=*.py
   ```
   Also check `.env` files, shell scripts, cron jobs.
3. **Categorize:**
   - ❌ **No active refs** (e.g. leftover `client_secret_*.json` from initial Google API setup) → `rm -f`
   - 🔴 **Active refs** (e.g. `lusine-calendar-sa-key.json` used by `review_response_handler.py`) → keep
4. **Delete stale** — `rm -f` credential files with no active references
5. **Rename folder** to dot-prefix:
   ```bash
   mv _private .private
   ```
6. **Update all script paths** — search for `_private` in scripts:
   ```
   search_files path=scripts pattern=_private/ target=content file_glob=*.py
   ```
   Update each to `.private/`. Common files:
   - `scripts/review_response_handler.py` — `SA_KEY = VAULT_ROOT / "_private" / "lusine-calendar-sa-key.json"`
   - `scripts/gsheet_query.md` — `KEY_PATH = os.path.join('vault', '_private', 'lusine-calendar-sa-key.json')`
7. **Update Obsidian `userIgnoreFilters`** (optional — dot-folder is auto-hidden, but keep filter for consistency):
   ```json
   "userIgnoreFilters": ["/.private/"]
   ```
8. **Verify** — folder exists, scripts point to new path, no `_private` references in code:
   ```python
   assert Path('vault/.private').is_dir()
   assert not Path('vault/_private').exists()
   ```
9. **Commit:**
   ```bash
   git add -A && git commit -m "fix: rename _private -> .private (Obsidian auto-hide)" && git push
   ```

**Pitfalls:**
| Pitfall | Fix |
|---------|-----|
| Script paths hardcoded to `_private/` | Search + patch all. Use `patch` not `sed` |
| `.private/` may be gitignored (`.*` pattern) | Check `.gitignore` — if `.*` or `.*/` exists, the folder won't be tracked. Use `git add -f .private/` or explicitly allow it |
| Old `_private/` tracked by git but renamed | `git add -A` detects rename automatically |
| User wants folder visible again | `mv .private _private` + restore script paths. No Obsidian settings to revert |

#### Option B: Windows hidden attribute + `userIgnoreFilters` (backup, needs Obsidian settings)

**When Option A (rename) is not possible** — e.g. `scripts/` can't be renamed because cron jobs reference the path, or Warren prefers the underscore name.

**Workflow:**
1. **Inventory + check refs** — same as Option A steps 1-3
2. **Delete stale** — `rm -f` unreferenced credential files
3. **Step A: Patch `.obsidian/app.json`** — add `"userIgnoreFilters": ["/_private/"]`
   - Format: leading `/` = vault root, trailing `/` = directory match
   - Affects: Quick Switcher, Search, Graph View (NOT file explorer without Step B)
4. **Step B: Mark folder hidden in Windows filesystem:**
   ```bash
   attrib +h "_private"
   ```
   - Affects: Obsidian file explorer (if "Show hidden files" is OFF in Settings → Files & Links)
   - File remains accessible to scripts on disk regardless
4. **Reload Obsidian** (`Ctrl+R`) — folder hidden from all views
5. **Verify in Obsidian UI** — if folder still appears after reload, check **Obsidian Settings → Files & Links → "Show hidden files"** — must be OFF (default). Turn it OFF and reload again.
   - If the setting is OFF and folder still shows, the `attrib +h` didn't persist → re-run `attrib +h "_private"` and verify via Windows File Explorer properties (General → Attributes → Hidden should be checked).

**Pitfalls:**
| Pitfall | Fix |
|---------|-----|
| `userIgnoreFilters` alone does NOT hide from file explorer | **Must also run `attrib +h`** on Windows. Obsidian respects Windows hidden attribute by default |
| Wrong format in JSON (`"_private"` vs `"/_private/"`) | Use leading slash for vault root + trailing slash for directory: `"/_private/"` |
| `patch` may mangle JSON (comma placement, broken array) in app.json | If JSON breaks, `write_file` the whole corrected content instead |
| Obsidian "Show hidden files" is ON in Settings | Toggle it OFF in Obsidian Settings → Files & Links |
| User wants folder visible later | Revert: remove from `userIgnoreFilters` + `attrib -h "_private"` |

#### Option C: CSS snippet (last resort — when `attrib +h` doesn't work)

**When neither rename nor Windows hidden attribute works** — some Obsidian versions always show hidden files, or the folder can't be renamed (like `scripts/`).

**Workflow:**
1. Create CSS snippet:
   ```bash
   mkdir -p vault/.obsidian/snippets
   ```
2. Write `vault/.obsidian/snippets/hide-folder.css`:
   ```css
   /* Replace "scripts" with folder name to hide */
   .nav-folder[data-path="scripts"],
   .nav-folder[data-path="scripts/"],
   div[data-path="scripts"],
   div[data-path="scripts/"],
   .nav-folder-title[data-path="scripts"],
   .nav-folder-title[data-path="scripts/"] {
     display: none !important;
   }
   ```
3. **Tell user to enable it** — Obsidian Settings → Appearance → CSS snippets → Refresh (🔄) → toggle ON
4. If still showing after toggle: edit snippet -> try multiple selectors (shown above)

**Pitfalls:**
| Pitfall | Fix |
|---------|-----|
| CSS snippet not working | User must manually toggle ON in Obsidian Settings; restart Obsidian; verify with `body { background: red !important; }` test |
| Selector doesn't match | Obsidian may use different DOM structure per version. Use multiple `data-path` selector variations |

### 5. Wiki health
Review `30_KNOWLEDGE_BASE/wiki/00_WIKI_INDEX.md` for numbered folder integrity, orphan pages, stale entries.

**Checklist:**
- [ ] All 10 numbered folders (01–10) exist on disk
- [ ] `00_WIKI_INDEX.md` `total_files` count matches reality
- [ ] No phantom file declared in INDEX but missing on disk
- [ ] "Where To Go" section present and current
- [ ] All INDEX files have `00_` prefix
- [ ] **No stale number prefix** — scan mỗi folder: file trong folder `04_...` không được có prefix `02_/03_/05_`. Báo cáo file lạc prefix.
- [ ] **No duplicate folder number** — `ls -d 30_KNOWLEDGE_BASE/wiki/0*/`: không được có 2 folder cùng prefix `NN_` (vd `09_connections/` đụng `09_hourly_cover_revenue/` = collision). Báo cáo + đề xuất renumber hoặc delete folder rỗng/chết.

**Workflow:**
1. `ls -d 30_KNOWLEDGE_BASE/wiki/0*/` — verify all 10 numbered folders exist
2. Compare INDEX entries against actual `ls` output
3. **Stale prefix scan:** cho mỗi numbered folder, `ls` files bên trong → flag file nào có prefix `NN_` khác với số folder (vd `02_HR_Movements...` trong `04_labour_costs/`). Báo cáo findings.
4. **Fix stale prefix:** rename file (bỏ prefix), update frontmatter name + title, update WIKI INDEX entry, grep vault-wide cho old filename và patch cross-references. See `references/wiki-file-maintenance.md` §1.
5. **Total_files accuracy:** sau khi add/remove files, count bằng `ls | grep -c "^-"` trong folder, update `total_files` frontmatter.
6. Report mismatches as findings

**Case study:** See `references/2026-07-07-wiki-09-number-collision-delete.md` — `09_connections/` (dead shell, chức năng đã merge vào `/ops-weekly-report`) đụng số với `09_hourly_cover_revenue/`. Delete + patch WIKI_INDEX + xóa FRONTMATTER_CACHE.json stale entry.

### 6. 📥 Inbox standardization

**When:** `_inbox/` có extra folder ngoài `01_unprocessed/`, `02_processed_archived/`, `.last_fetch`.

**Workflow:**

1. **Inventory** — list all subdirs in `_inbox/`:
   ```
   search_files path=vault/_inbox pattern=* target=files
   ```

2. **Classify each extra folder:**
   - ❌ **Empty folder** → delete directly
   - 🔶 **Has unprocessed files** → move files to `01_unprocessed/`, then delete folder
   - ⚠️ **Has processed files** → move to `02_processed_archived/`, then delete folder

3. **Reference check** — nếu có file được move, grep vault-wide cho old path, patch nếu có.

4. **Standard structure after cleanup:**
   ```
   _inbox/
   ├── 01_unprocessed/         ← raw items waiting for processing
   ├── 02_processed_archived/  ← processed items archive
   └── .last_fetch             ← timestamp (operational, gitignored)
   ```

5. **No friction rule:** Không tạo extra inbox folder. Nếu script cần drop zone → dùng `01_unprocessed/`.

### 8. 📊 Data freshness audit

**When:** Check if log file frontmatter `last_updated` matches actual file modification time.

**Workflow:**

1. **Scan all 10_OPERATION_DATA/ log files:**
```python
import os, yaml
from datetime import datetime

for f in os.listdir('10_OPERATION_DATA/'):
    if not f.endswith('.md') or f.startswith('00_'): continue
    mtime = datetime.fromtimestamp(os.path.getmtime(f'10_OPERATION_DATA/{f}'))
    content = open(f'10_OPERATION_DATA/{f}', encoding='utf-8').read()
    fm = content.split('---', 2)[1]
    lu = yaml.safe_load(fm).get('last_updated')
    delta = (mtime - datetime.strptime(str(lu), '%Y-%m-%d')).days
    if delta > 30:
        print(f'🔴 STALE: {f} — lu={lu}, mtime={mtime.date()}, delta={delta}d')
```

2. **Fix stale frontmatter:**
   - `patch` the `last_updated` field to match today's date
   - Only fix if file content was actually modified (not just mtime drift)

3. **Morning briefs folder:**
   - Check `morning_briefs/` files too — same pattern

**Thresholds:**
| Delta | Severity | Action |
|-------|----------|--------|
| 0–7d | ✅ OK | None |
| 7–30d | 🟡 Warning | Flag but skip |
| >30d | 🔴 Stale | Update `last_updated` to today |

### ⚠️ Pre-Flight Safety Check (before any INDEX fix)

**Khi nào:** Trước khi modify bất kỳ shared INDEX file nào (CASES_INDEX, WIKI_INDEX, OPERATION_INDEX) — dù là fix phantom path, update total_files, rename file, hay sửa slug.

**Mục đích:** Verify không script/cron/parser nào vỡ khi sửa INDEX.

**Workflow — 4 bước bắt buộc:**

1. **Search scripts cho file name:**
   ```bash
   search_files path=scripts pattern=CASES_INDEX file_glob=*.py
   search_files path=scripts pattern=file_path file_glob=*.py
   # Mở rộng cho mọi field sẽ sửa (total_files, case_id, slug...)
   ```

2. **Trace từng script — đọc function có reference:**
   - Script có đọc field đó không? (e.g. `data.get("file_path", "")` )
   - Script có **dùng field đó để mở file** không? (e.g. `open(file_path)` )
   - Script có **tự generate** giá trị mới không? (không phụ thuộc giá trị cũ)

3. **Map findings thành bảng:**
   ```
   | Script | Đọc field X? | Dùng để mở file? | Tự generate? | Break? |
   |--------|-------------|-------------------|--------------|--------|
   | cases_parser.py | ✅ file_path | ❌ only metadata | — | ✅ An toàn |
   | gen_today.py | ❌ chỉ followup_date | — | — | ✅ An toàn |
   | case_followup_orch.py | ❌ tự gen mới | — | ✅ gen đúng | ✅ An toàn |
   ```

4. **Present cho Warren với kết luận rõ:**
   - "✅ Không script/cron/parser nào vỡ" — nếu tất cả an toàn
   - "🔴 Script X sẽ vỡ, cần patch trước" — nếu có script phụ thuộc

**Ví dụ thực tế (2026-07-05):** Fix 22 phantom `file_path: [[_cases/closed/]]` trong CASES_INDEX:
- Traced 5 scripts: cases_parser.py, gen_today.py, case_followup_orchestrator.py, generate_today_revenue.py, ops_cases_cli.py
- Kết quả: **không script nào dùng `file_path` để mở file** → all safe → proceed.
- Nguồn: `vault/_cases/00_CASES_INDEX.md` — phantom paths from YAML entries where case was closed by hand without slug.

### 9. 👻 Phantom file detection

**When:** Check if all files listed in INDEX actually exist on disk.

**Workflow:**

1. **Read INDEX** (`00_WIKI_INDEX.md`, `00_CASES_INDEX.md`) — extract all `file` column entries.

2. **Verify existence:**
```bash
# For each file in the INDEX table
ls "path/to/file.md" 2>&1
# Returns error if file doesn't exist
```

3. **For missing files — check git history:**
```bash
git log --all --oneline -- "*/missing_file*" 2>/dev/null
# Empty output = never existed (phantom)
# Has output = deleted at some point
```

4. **Cleanup:**
   - **Never existed (phantom):**
     - Remove from INDEX table
     - Update `total_files` count
     - Remove all wikilinks `[[PhantomFile]]` vault-wide
     - For standalone list items: `sed -i '/PhantomFile/d' file1.md file2.md ...`
     - For inline references: use `patch` surgically
     - Verify: `grep -rn "PhantomFile" --include="*.md" .` → 0 results
   - **Was deleted intentionally:**
     - Remove from INDEX table only
     - Keep wikilinks (they already point to nothing — cosmetic issue only)

5. **Em dash hazard:**
   Files with en-dash (`–`, U+2013) in the name may not show up in `ls` with basic glob.
   Use `find . -name "*partial_name*"` or `git ls-files "*partial*"` instead.

**Prevention:**
- New files: avoid en-dash/em-dash in filenames. Use hyphens instead.
- After any INDEX update: verify next file in table actually exists.

### 10b. 🧨 Full app/tool uninstall + git-safe vault cleanup

**When:** Warren says "xóa hết [app] chỉ giữ [app]" (e.g. "xóa Cursor + Kilo Code + VS Code, chỉ còn Hermes Desktop"). This is a BLAST-RADIUS task — confirm scope first because "only keep X" may implicitly kill things Warren didn't name (e.g. VS Code app, sibling repos).

**Workflow (verified 2026-07-09 — removed Cursor + Kilo Code + VS Code, kept Hermes):**

0. **Confirm blast radius (clarify).** "Only keep X" does NOT name everything else. Ask: does Warren also want VS Code app gone? Sibling git repos (e.g. `tmp_agent_skills/`)? Don't assume.

1. **Inventory ALL traces (read-only first, never delete blind):**
   ```bash
   # git-tracked in vault
   git -C "C:/Users/khoans/Documents/Personal_OS" ls-files | grep -iE 'cursor|kilo|\.vscode'
   # app/AppData traces (depth 3-4, skip node_modules)
   find /c/Users/khoans/AppData /c/Users/khoans -maxdepth 4 -iname '*cursor*' -o -iname '*kilo*' 2>/dev/null | grep -vi node_modules
   # home hidden dirs + installers
   ls -d /c/Users/khoans/.cursor /c/Users/khoans/.vscode 2>/dev/null
   ls /c/Users/khoans/AppData/Local/Programs/ 2>/dev/null | grep -iE 'cursor|code'
   ls /c/Users/khoans/Downloads/*ursor* 2>/dev/null
   # running processes
   tasklist 2>/dev/null | grep -iE 'cursor|kilo|code'
   # winget packages
   winget list 2>/dev/null | grep -iE 'cursor|visualstudiocode'
   ```

2. **Classify each trace:**
   - **git-tracked vault files** (e.g. `.kilo/`) → must `git rm -r --cached` THEN `rm -rf` (plain `rm` does NOT untrack; git restores on next commit).
   - **Nested git repo in vault** (e.g. `tmp_agent_skills/`) → `git ls-files -s` shows **mode 160000** (gitlink/submodule reference). Remove with `git rm -r --cached tmp_agent_skills` + `rm -rf`. Git will NOT restore a deleted gitlink after commit.
   - **App install** → `winget uninstall --silent --accept-source-agreements <id>` (may list same app twice: EXE user + MSIX store — uninstall BOTH).
   - **AppData / home config** → `rm -rf` after uninstall.
   - **`.git/` internals** (e.g. `stock_vault/.git/cursor`, `stock_vault/.git/kilo`) → leftover refs from `git rm`; `rm -rf` them too (git status stays clean).

3. **Git path gotcha (CRITICAL on Windows):** git in this env **rejects MSYS paths** (`/c/Users/...`) with `fatal: not a git repository`. ALWAYS pass **Windows-style** paths (`C:/Users/khoans/...`) to `git -C`. The `terminal` tool runs bash, but git needs the `C:/` form.

4. **`.gitignore` silent exclusion:** After editing, if `git status` shows "nothing to commit" but your files changed on disk, check `.gitignore`:
   ```bash
   git -C "C:/Users/khoans/Documents/Personal_OS" check-ignore -v stock_vault/00_CORE_LOGIC/STOCK_MEMORY.md
   ```
   If ignored, git will NOT track/commit those changes. Don't force-add unless Warren approves (ask via clarify). The change is still on disk — safe, just not in git.

5. **Verify 100% clean (zero tolerance):**
   ```bash
   find /c/Users/khoans -maxdepth 5 \( -iname '*cursor*' -o -iname '*kilo*' \) 2>/dev/null | grep -viE 'node_modules|/lsp/'
   winget list 2>/dev/null | grep -iE 'cursor|visualstudiocode'   # expect NONE
   git -C "C:/Users/khoans/Documents/Personal_OS" status --short    # expect clean
   tasklist 2>/dev/null | grep -iE 'cursor|kilo|code'              # expect no running
   ls -d /c/Users/khoans/.cursor /c/Users/khoans/.vscode 2>/dev/null || echo GONE
   ```

**Pitfalls (2026-07-09):**
| Pitfall | Fix |
|---------|-----|
| `rm` on a git-tracked file → git restores on commit | Use `git rm -r --cached` first, then `rm -rf` |
| Nested repo shows as gitlink `160000` | `git rm -r --cached <repo>` + `rm -rf`; git won't restore |
| git rejects `/c/Users/...` (MSYS path) | Use `C:/Users/khoans/...` Windows path with `git -C` |
| `git status` clean but disk changed | `.gitignore` excludes it — check `check-ignore -v`, ask before force-add |
| winget output swallowed in background bash (`stdin is not a tty`) | Verify via `winget list` after, not the background stdout |
| `~/.vscode` is actually VS Code config, not Cursor | Kilo Code runs as a VS Code *extension*; deleting `~/.vscode` removes Kilo too |
| `.git/cursor` / `.git/kilo` leftover internals | `rm -rf` them separately after `git rm` (git status stays clean) |

### 10. 🪄 Wiki file rename / merge / rolling conversion

**When:** Cần restructure files trong wiki folder — rename file (remove stale prefix), merge multiple files, hoặc convert year-specific file sang perpetual rolling format.

**Principles:**
- **Rename:** chỉ change tên, ko change content. Update frontmatter, title, INDEX, cross-refs.
- **Merge:** identify unique content per source file, preserve in target, delete sources. Net file count giảm.
- **Rolling:** year-specific → perpetual format. Add year transition instruction. Update INDEX type.

**Full workflows with commands: see `references/wiki-file-maintenance.md` (sections 1-4).**

**Key pitfalls when using `patch` tool on WIKI INDEX:**

| Pitfall | Fix |
|---------|-----|
| `patch` fails: "Found N matches" (pattern không unique) | Dùng `sed -i` qua terminal cho replacement: `sed -i 's/old-text/new-text/g' file.md` |
| `patch` fails with `...` pattern across YAML `---` blocks in INDEX files | `patch`'s fuzzy matching can't span YAML `---` delimiters. Pattern như `case_id: "X" ... file_path:` sẽ fail. **Fix:** Dùng Python script: `re.split('---')` → `str.replace()` → join. Xem `references/yaml-block-index-patch.py` cho code mẫu. |
| Pipe count sai trong INDEX table row
| INDEX row có `|||` thay vì `||` (dư 1 pipe) | Do closing pipe của row trước + `||` của row mới. Kiểm tra raw với `cat -A`. Sửa `|||` → `||`. |
| `total_files` không match reality | `ls wiki/folder/ \| grep -c "\\.md$"` rồi update frontmatter. |
| Quên update cross-refs sau rename/delete | `search_files path=vault pattern=<old-filename> target=content` vault-wide. Xoá sạch. |

### 10c. 🧹 Feature decommission — scope triage + duplicate-identity detection
**When:** Warren says "remove [X] entirely for consistency" (e.g. mem0 purge 2026-07-12). Naive grep-and-delete BREAKS live systems. Triage every hit into 4 buckets BEFORE touching anything:

| Bucket | Examples | Action |
|--------|----------|---------|
| 🔴 **Functional infra** (the thing actually runs) | `config.yaml provider:`, skill dir, cron jobs | Decommission LAST, step-by-step, Warren approves each. Deleting = kill feature. |
| 🟡 **Active docs** (reference the feature) | SOUL.md, USER.md, WARREN_MEMORY.md active-ref lines, ONTOLOGY tags, wiki index JSON, `_inbox/INDEX.md` | Clean first — safe, no runtime impact. |
| 📼 **Historical** (archive/snapshot/log/cache) | `_archives/`, `state-snapshots/`, `cron/output/`, `FRONTMATTER_CACHE.json` node-name strings | **DO NOT touch** — record, not live. Node-name strings in JSON (e.g. `"Mem0_Manual_Flow"`) are fine if not in a `tags` array. |
| 🗑️ **Stale drafts/intents** (`_inbox/` files named after the feature, `status: draft`) | `spec_mem0_faiss.md`, `intent_tencent_memory.md` | Delete if no skill/cron references the filename (search profile skills first). |

**Duplicate-identity trap (caught 2026-07-12):** A feature doc may exist in 2 places that LOOK like copies but AREN'T:
- `vault/SOUL.md` (edit-copy) vs `profiles/warren-profile/SOUL.md` (**LIVE** — Hermes Desktop loads `$HERMES_HOME/SOUL.md` at session start).
- **Rule:** profile SOUL = canonical live. Vault SOUL = redundant copy. Before deleting either: (1) `diff` both, (2) merge unique content from the deleted one INTO the survivor (frontmatter `canonical: true`, §2.5 step7 ontology reconcile, §3 vault-structure table, §7 quick-ref, §8 search-chain are typically vault-unique; §5.1 zones / §3.1 liteparse-gate / consent-gate are typically profile-unique and skill-referenced — KEEP them), (3) sweep all cross-refs (`AGENTS.md`, skills) pointing to the deleted path and repoint, (4) THEN delete. Never `write_file` overwrite live SOUL with the copy — that downgrades the agent (drops §5.1/§3.1, dangling skill refs).

**Warren's explicit governance on this (2026-07-12):** "double check it won't affect workflow/structure/parser/script/cron" + "check the 2 files, move important info from the deleted one into the profile file, update everything to 1 canonical." → Encode as: VERIFY scope (search profile `skills/`, `cron/`, `scripts/` for references) BEFORE delete; MERGE-THEN-DELETE; REPOINT all refs to survivor.

**JSON tag-array verify (ad-hoc, system-required):** When patching wiki `*.json` (WIKI_GRAPH.json, FRONTMATTER_CACHE.json) to drop a tag, verify with a temp script:
```python
# AppData/Local/Temp/hermes-verify-<topic>.py
import json, re, os
base=".../30_KNOWLEDGE_BASE/wiki"; files=["WIKI_GRAPH.json","FRONTMATTER_CACHE.json"]
ok=True
def walk(o):
    global ok
    if isinstance(o,dict):
        if "tags" in o and isinstance(o["tags"],list):
            for t in o["tags"]:
                if isinstance(t,str) and "mem0" in t.lower(): ok=False; print("FAIL tag",t)
        for v in o.values(): walk(v)
    elif isinstance(o,list):
        for v in o: walk(v)
for f in files:
    d=json.load(open(os.path.join(base,f),encoding="utf-8")); walk(d)
    json.load(open(os.path.join(base,f),encoding="utf-8")); print("PASS valid",f)
print("ALL PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
```
Run `python3`, cleanup temp. Raw "mem0" in node-name strings is acceptable (not in `tags`). Report as "Ad-hoc verification PASSED" — no suite exists for JSON.

**Full worked example + scope table + verify script: see `references/mem0-decommission-pattern.md`.**
| Pitfall | Fix |
|---------|-----|
| grep-only sweep misses filename-based hits (`*mem0*.md` in `_inbox/`) | After content-grep, `ls` the dir for filename matches too |
| Deleting live SOUL (`profiles/.../SOUL.md`) | Kills agent identity → fallback built-in default. NEVER. |
| Overwriting live SOUL with vault copy | Downgrades agent, dangling §5.1/§3.1 skill refs. MERGE unique, keep profile structure. |
| Skill references dangling after delete (e.g. `audit-automation/SKILL.md` had vault-SOUL fallback) | Sweep `skills/**` for the deleted path BEFORE delete; patch. |
| JSON `tags` array borked by hand-edit | Use the temp-script verify above; never eyeball-edit JSON arrays. |
| "Remove all mem0" interpreted as kill infra | Triaging: functional infra = last step, Warren approves per-action. Active-docs/historical/drafts handled first. |
