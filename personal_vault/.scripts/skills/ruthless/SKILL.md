---
name: ruthless
description: Apply Musk-style deletion lens to vault artifacts — skills, SOPs, wiki pages, ideas, commands. Evaluate for redundancy, consolidation, or eradication.
category: devops
tags: ['simplify', 'delete', 'tidy', 'ruthless', 'cleanup']
version: 2.2.0
trigger: /ruthless [target]
related_skills: ['tidy']
---

# /ruthless
Evaluate targets for deletion, merge, or simplification.

## Lens
1. Question necessity — "What happens if this doesn't exist?"
2. Delete if redundant — overlaps with another artifact?
3. Simplify complexity — can this be merged into a parent?
4. Accelerate remaining — after cut, what's the new fastest path?
5. Automate last — only automate what survives the cut.

## Skill Audit Protocol

Use this when evaluating a skill/command for consolidation or deletion.

### Phase 1: Load & Analyze
1. Load the target skill via `skill_view(name)` — read SKILL.md completely
2. Load its references and runner scripts
3. List the checks/actions it actually performs (not what it claims)
4. Identify which checks/actions are UNIQUE vs overlapping

### Phase 2: Cross-Reference
1. Search for overlapping skills via `skills_list()` + `skill_view()` on each candidate
2. Build a comparison matrix:
   | Check/Action | Target Skill | Overlap Skill 1 | Overlap Skill 2 |
   |-------------|--------------|-----------------|-----------------|
   | Unique?     | ✅           | ❌              | ❌              |
3. Check cron jobs via `cronjob action=list` — is this skill referenced in any cron?
4. Check if other skills reference this skill by name
5. Check memory for references to this skill

### Phase 3: Verdict
Produce ONE of the following verdicts with evidence:

| Verdict | Condition | Action |
|---------|-----------|--------|
| **KEEP** | Has unique, valuable checks/actions not covered elsewhere | Document why it survives |
| **MERGE into [X]** | Every check overlaps with skill X | Redirect SKILL.md, update X's SKILL.md, update X's runner, update cron/memory |
| **DELETE** | All checks are dead (none runnable) or fully covered by existing skills | Delete skill, update references |
| **SIMPLIFY** | Has unique value but over-engineered (3,000-word SKILL.md for 9 actual checks) | Trim SKILL.md to match reality, archive unused scripts |

### Phase 4: Execute (if user approves)
1. For MERGE:
   - Update target skill's SKILL.md to absorb the functionality
   - Update target skill's runner script if applicable
   - Set source skill's SKILL.md to redirect/deprecation notice
   - Update any cron jobs referencing the source skill
   - Update memory references
2. For DELETE:
   - `skill_manage(action='delete', name='...', absorbed_into='target_skill')`
   - Update cron/memory
3. For SIMPLIFY:
   - Rewrite SKILL.md to match actual behavior
   - Archive unused scripts/references in a deprecated section

### Phase 5: Verify
1. Run the target (or merged) skill to confirm it still works
2. Confirm cron jobs execute without error
3. Confirm no stale references remain

## Skill Audit Trigger Signals
Red flags that warrant running this protocol:
- SKILL.md is >1,500 words but does less than described (aspirational docs)
- Multiple skills do the same checks (overlap cluster)
- Skill references a script that doesn't exist on disk
- Cron job references a deprecated or renamed skill
- **Code was merged/consolidated but the skill documentation wasn't updated** (e.g. `ops_index_lint_sync.py` merged ops-lint + ops-index-sync 06/2026, but `vault-index-sync` skill stayed standalone until 07/2026)
- User asks "skill này có cần thiết không?" or similar

## User-Specific Conventions (Warren)
- **Language:** Warren asks in Vietnamese, expects answer in Vietnamese (with diacritics). "thẳng thắng ko khoan nhượng" = straight talk, no throat-clearing.
- **Preferred verdict pattern:** Conclusion-first, no hedging. "Nó có dư thừa ko? Nếu có, merge vào lệnh nào, rồi delete vĩnh viễn luôn."
- **Default bias:** Delete/merge over keep. If a command or artifact can be absorbed into another with zero value loss, Warren wants it gone.
- **⚠️ Communication density (2026-07-12, explicit "ghi nhớ dùm tôi"):** Khi phân tích / viết report → NÓI NGẮN GỌN, BULLET POINTS, tránh dài dòng / prose lang mang. Một insight = 1-3 gạch đầu dòng, không viết đoạn văn dài. Warren ghét "quá nhiều chữ mà lang mang".
- **🚫 KHÔNG tự tạo folder/file mới trong vault.** Mọi thay đổi cấu trúc (tạo folder, file mới) = zone 🔴, PHẢI hỏi Warren trước. Ghi measurement/tracking VÀO case file có sẵn, đừng tạo file riêng.
- **📌 Measurement blocks lên ĐẦU file.** Khi gắn tracking/promo measurement vào case file → đặt ngay sau §1 (cùng nhóm todo/follow-up) để Warren "nhìn vô thấy liền", KHÔNG để cuối file (§10). Lý do: ông duyệt plan xong hay quên check cuối.
- **Existential gate:** Before agreeing to delete any file, Warren asks 4 questions: tác dụng gì, sao tồn tại, tốt cho ai, xoá được ko. Always pre-answer all four when proposing deletion.
- **🚫 "DELETE" = xóa hẳn, KHÔNG giữ dòng + explanatory note.** Khi Warren nói "xóa [dòng X]", thực thi là xóa sạch dòng đó khỏi file. Đừng giữ lại dòng rồi chèn blockquote giải thích "đã xóa" — Warren coi đó là chưa làm. Nếu cần lưu context tạm (vd số lịch sử), ghi vào MỘT CHỖ KHÁC (file SSOT Block 0 historical note, hoặc memory), không giữ dòng gốc. Concrete failure (2026-07-07): Warren bảo "xóa line 23 (~64 staff baseline)" nhưng agent giữ dòng + thêm note deprecated → Warren phải nhắc lại "xóa". **Fix:** xóa trắng dòng, chuyển context sang nơi đúng, báo cáo "đã xóa hẳn".
- **Signals to act:** Warren has now asked "thẳng thắng advise" for 3 commands (ops-lint, ops-weekly-connections, ops-context-update). Each time the pattern was: evaluate → propose merge → execute delete. This is a learned workflow — don't wait to be asked twice.
- **🚫 KHÔNG tự động tạo folder/file mới trong vault.** Warren explicitly stated this: "ko tự động tạo folder. phải hỏi ý tôi, làm mọi thứ gọn gàng." Before ANY vault structure change (create/rename/move folder), present options with tradeoffs + recommended reply. Only execute after Warren explicitly approves.
- **📉 LEAN-CUT FIRST (cross-reference before proposing new work):** When Warren asks to apply an external idea/tool/framework, ALWAYS grep the vault for existing artifacts that already cover the same ground BEFORE proposing new actions. Session 2026-07-12: a 6-action "apply marketingskills to L'Usine" plan was cut to 3 because `SOP_005` (review response), `Beverage_Concept_Strategy_2025` (positioning), and `lto_tracker_Hub` (LTO ideas) already existed. Present the redundancy matrix to Warren, then propose MERGE/keep-only. Default bias: delete/merge over keep.
- **🗣️ COMMS CONVENTION (Warren, 2026-07-12):** "nói ngắn gọn, có bullet, tránh dài dòng, quá nhiều chữ mà lang mang" + "chỉ trả lời". When delivering analysis/debate: conclusion-first, bullet points, NO long prose walls. He WANTS pushback (debate, challenge assumptions) — but deliver it densely, not verbosely. When he says "chỉ trả lời" → answer the literal question only, no preamble.
- **📌 PUT MEASUREMENT/TODO AT TOP:** When adding tracking/measurement to a case file, place it near the top (§1.x, same cluster as todo/follow-up) so Warren sees it immediately — NOT at the bottom (§10). Session 2026-07-12: promo measurement added as §1.5, not §10, per his instruction.

## Vault line-ending pitfall (Windows / Obsidian .md files) — PATCH VIA BYTES
Warren's vault .md files have **MIXED line endings** — some sections use real CRLF/LF, others use literal backslash-n (`\n` as 2 raw bytes `5c 6e`). `patch` tool and naive `python` string `.replace()` with `'\n'` (real newline) FAIL silently because the file stores literal `\n` in places.
**Symptom:** 6 consecutive failed `assert anchor in s` attempts this session on one file, despite the text looking identical in `read_file`.
**Fix:** Never guess. Inspect raw bytes first, then patch at the byte level:
```python
b = open(path, 'rb').read()
i = b.find(b'unique-anchor-substring')
print(repr(b[i-10:i+30]))   # reveals CRLF vs LF vs literal \n
```
- If `repr` shows `\\n` (double backslash) → file uses literal backslash-n; match with `b'\\n'` (bytes `5c 6e`), NOT `b'\n'`.
- If `repr` shows `\r\n` or `\n` (single) → real newline; match with `b'\r\n'` / `b'\n'`.
- Also avoid `write_file` for these edits — its escaping mangles UTF-8 anchors. Write a temp `.py` that does `open(p,'wb').write(b)`, run `python` (NOT `python3`), then `rm` the script.
- Unicode in anchors: prefer a short ASCII-ish byte substring (e.g. `b'Guardrails:'`) over a full Vietnamese sentence to dodge encoding mismatches.
- **📝 Style — NGẮN GỌN, BULLET, KHÔNG lang mang.** Warren (2026-07-12): "nói ngắn gọn, có bullet, tránh dài dòng, quá nhiều chữ mà lang mang. ghi nhớ dùm tôi ha." Apply to ALL analysis/reports: lead with conclusion, use bullets/tables, cut prose. Long narrative = failure even if correct.
- **📌 Measurement/promo tracking → GẮN VÀO CASE FILE ĐẦU, không để cuối.** Warren (2026-07-12): "để nó lên đầu file, cùng với những todo/follow up, để warren nhìn vô thấy liền." When adding a tracking/measurement section to an existing case, insert it right after §1 (Bối cảnh) / near the todo-followup block — NOT as a trailing §10+. He scans the top; buried sections are missed.
- **🔒 Respect "giữ nguyên" — DO NOT re-propose a change you already offered.** Warren (2026-07-12) said keep §4 targets as-is; when challenged later ("lý do nào bạn tăng lên 240?") the agent had re-suggested 240. If Warren declines a suggestion, lock it. Re-opening a rejected option without new evidence = annoying. Defend the rejected option only if he explicitly re-opens it.
- **🗂️ Measurement lives in the EXISTING case file, not a new folder.** When Warren asks to measure a promo, patch the relevant active case (e.g. quick-wins plan) — do NOT create `05_Promo_Tracking/` or similar. New folders = vault-structure change = needs approval (see above). Reference the SSOT rolling log by path; never copy raw data into the case.
- **🟢 Phân tích = NGẮN GỌN + BULLET.** Warren explicit (2026-07-12): "nói ngắn gọn, có bullet, tránh dài dòng, quá nhiều chữ mà lang mang. ghi nhớ dùm tôi ha." Khi viết report/analysis/advise → lead với conclusion, dùng bullet points, cắt bỏ prose thừa. Dài dòng = fail.
- **🟢 Measurement/tracking sections ĐỂ LÊN ĐẦU file.** Warren (2026-07-12): khi gắn đo lường/promo tracking vào case file → đặt ngay đầu (cùng nhóm TODO/follow-up), "để warren nhìn vô thấy liền", KHÔNG để cuối file (§10, §11...). Vd: gắn `## 1.5. PROMO MEASUREMENT` ngay sau `## 1. BỐI CẢNH`, trước `## 2.`. Tuân thủ 5-second rule của ops-case-lifecycle.
- **🚫 KHÔNG tạo folder riêng cho promo tracking.** Khi đo lường 1 promo (vd Sunset HH / Morning Kickstart), GHI VÀO case file có sẵn (vd `2026-06-28_quick-wins...`), KHÔNG tạo `05_Promo_Tracking/`. Vi phạm rule "không tự tạo folder" + dư thừa. Chỉ link sang SSOT data (`09_Hourly_Cover_Revenue_Log.md`), KHÔNG copy raw data vào case.
## Vault Orphan Cleanup Protocol

Use this when evaluating orphan folders (empty, stale, or agent-artifact folders) in the vault.

### Pre-flight

1. **Check folder contents** — `ls -la` to see what's inside
2. **Search vault references** — `search_files(pattern, path=vault/)` for both folder name and files inside
3. **Check git tracking** — `git status --short <path>` before any delete
4. **Present to Warren** — show folder contents + reference count + verdict (safe to delete / needs keep)
5. **Warren must approve** before any delete — never auto-delete even if zero references

### Execution (Windows)

- **Do NOT use `rm -rf` from git-bash/MSYS** — Windows filesystem caching often causes silent failure (file appears deleted but is recreated moments later by search index, antivirus, or OneDrive).
- **Use PowerShell** instead:
  ```
  powershell.exe -Command "Remove-Item -Path '<path>' -Recurse -Force -ErrorAction Stop"
  ```
- **Verify deletion** — `ls <path>` after delete to confirm it's gone
- **Check git status** — if files were tracked, `git status --short` will show ` D` or `D ` (deleted)

### Post-delete
### Post-delete
1. **Check git tracking first** — `git status --short <path>` before any stage/commit
   - **No output** = file was already gitignored or never tracked → **skip commit**, tell user "đã có trong `.gitignore`, không có gì để commit"
   - **` D` / `D `** = tracked file was deleted → proceed to stage
   - **`??`** = untracked file was deleted → skip commit (was never tracked)

### Referenced-File Deletion Protocol (Warren: "patch lại những file có liên quan")

When the target is NOT an orphan but IS referenced by other files, deletion alone leaves broken links. Warren expects the referencers patched too. This is the standard path for "xóa file X + patch mọi file liên quan".

1. **Find ALL referencers BEFORE deleting:**
   ```bash
   search_files(pattern="TARGET.md")                                    # vault + repo root
   search_files(pattern="TARGET.md", path="~/.hermes/profiles/warren-profile/skills")   # skill docs
   search_files(pattern="TARGET.md", path="~/.hermes/profiles/warren-profile/cron")     # cron prompts
   # Wiki file/folder deletes ALSO check the frontmatter cache (path may lag actual name):
   search_files(pattern="TARGET.md", path="vault/30_KNOWLEDGE_BASE/wiki/FRONTMATTER_CACHE.json")
   ```
   - Vault md references → patch inline (remove the row / reword the sentence).
   - `~/.hermes` skill references in HISTORICAL/ARCHIVE docs (case-study `.md` under `references/`) → leave untouched (they're records, not live instructions). Only patch ACTIVE skill SKILL.md / runner if it instructs the user to open the deleted file.
   - Cron `jobs.json` prompt strings → patch the prompt (e.g. remove "write to TARGET.md" instruction). Edit via `patch` on the JSON file.
2. **Patch every live referencer**, then delete the target.
3. **Verify zero references remain** with the same 3 searches → expect 0 matches (archive docs excluded).
4. **Delete:** `git rm -f vault/.../TARGET.md` (use `-f` — a tracked file with uncommitted modifications will refuse a plain `git rm`; `-f` forces it). For untracked targets use `git rm` without `-f` or just delete from disk.
5. **Commit + push.** Watch for the battle-test pre-commit hook: deleted files with missing frontmatter `created`/`last_updated` on OTHER patched files (e.g. `SOUL.compact.md`) will BLOCK the commit — add the frontmatter fields to the patched file, not the deleted one.

#### Wiki-Page Deletion Cascade (Obsidian artifacts)

When the deleted target is a wiki `.md` page (under `30_KNOWLEDGE_BASE/wiki/`), plain referencer-patching is NOT enough — Obsidian also tracks the page in generated graph/cache files, and dozens of unrelated active files may hold `- [[PageName]]` list-items. The blast radius is typically far larger than Warren expects (session 2026-07-10: 5 deleted P&L pages → broken links in 48 active files, 143 lines). Follow this cascade:

1. **Find referencers** (standard step 1) BUT widen to catch generated artifacts:
   - `00_WIKI_INDEX.md` rows (file + period + key_insights columns)
   - `*_Hub.md` table rows (e.g. `P&L_Budget_Hub.md`)
   - `WIKI_GRAPH.json` nodes/edges (DO NOT hand-edit — regenerate, step 4)
   - `FRONTMATTER_CACHE.json` entries (regenerate, step 4)
   - Any active `.md` holding `- [[PageName]]` list-items (often 20–50 files)
2. **Patch human-readable referencers**: remove index rows, hub-table rows, and every `- [[PageName]]` list-item in ACTIVE (non-`10_archive`) files. For mass wikilink cleanup, write a temp script that strips exact `- [[NAME]]` lines via regex, skipping `10_archive/` (recipe in `references/2026-07-10-pl-wiki-cascade-delete.md`).
3. **Delete the target files** — PowerShell `Remove-Item -LiteralPath` (preferred per Windows deletion rule), or `rm -f` with absolute quoted path as fallback. NEVER `cd` into the target dir if the path contains `&` (see pitfall below).
4. **Regenerate graph + cache + index** (auto-removes dead nodes/edges — do NOT hand-edit JSON):
   ```bash
   cd vault && python scripts/rebuild_wiki_index.py --graph --frontmatter
   ```
   Run AFTER deletion so stale entries vanish. This rewrites `WIKI_GRAPH.json`, `FRONTMATTER_CACHE.json`, and `WIKI_INDEX.md` from current on-disk files.
5. **Verify**: `search_files` for `[[PageName]]` across `wiki/` → expect 0 in active files (`10_archive/` links allowed to stay — script excludes archive). Optionally run an ad-hoc verify script (temp file under `%TEMP%`, deleted immediately after).

**Pitfall — `&` in path breaks `cd` in git-bash terminal.** Folder `01_P&L_Budget` contains a literal `&`; `cd "C:/.../01_P&L_Budget"` fails with `syntax error: unexpected end of file` (bash treats `&` as background operator even inside quotes in the terminal tool's eval). Fix: never `cd` into a path with `&` — use absolute `Remove-Item -LiteralPath '<path>'` (PowerShell) or `rm -f "/full/path/File.md"` with quotes. Durable quirk of THIS vault's folder naming.

### Windows git ghost-temp file cleanup

Ad-hoc verify scripts written to `%TEMP%` with a Windows path can leak into the repo as a phantom untracked file named like `"C:\Users\khoans\AppData\Local\Temp\hermes-verify-19763.py"` (git displays the raw UTF-8-mangled `C:` bytes). `git status` shows it; `find` on disk finds NOTHING (it doesn't really exist). It gets swept into `git add -A` and committed as a ghost.

**Removal (after the fact):**
- `git rm --cached <path>` and `git rm <path>` both FAIL ("outside repository" / pathspec mismatch) because of the mangled path.
- Working fix: read `git ls-files -z`, find entries containing `hermes-verify-19763`, and pipe the raw bytes to `git update-index --force-remove --stdin`:
  ```python
  import subprocess
  files = subprocess.run(['git','ls-files','-z'],capture_output=True).stdout.split(b'\x00')
  ghost = [f for f in files if b'hermes-verify-19763' in f]
  for g in ghost:
      subprocess.run(['git','update-index','--force-remove','--stdin'], input=g+b'\n', capture_output=True)
  ```
- Then `git commit --amend --no-edit` + `git push --force-with-lease origin master`.
- **Prevention:** always delete the temp verify script (via `rm` in the same terminal call) immediately after running it. Never rely on `git add -A` when a temp script was written anywhere under the repo root or `%TEMP%`.
- **Note:** after `git commit --amend` the ghost may still show in `git ls-files` locally until the `--force-remove` step runs; the authoritative check is `git ls-tree --name-only origin/master | grep hermes-verify` (must be empty after force-push).
2. **Important pre-commit check:** Nếu user yêu cầu commit/push ngay sau khi xóa, **luôn chạy `git status --short` trước** để xác nhận có change thật. Đừng stage/commit mù — nếu file đã gitignored, `git add -A` không có gì để stage và commit sẽ bị từ chối hoặc tạo empty commit.
3. **Stage deletion** — `git add -A` (preferred over `git add -u` to catch both tracked deletions and untracked renames)
4. **Commit** — message pattern: `"chore: remove <folder> — <reason>"`
5. **Push** — `git push`
6. **Verify git clean** — `git status --short` should be empty

### Obsidian Folder Hiding

To hide a sensitive folder from Obsidian file explorer:

| Method | How | Pros | Cons |
|--------|-----|------|------|
| **Dot-prefix** (recommended) | Rename `folder` → `.folder` | Obsidian auto-hides dot-folders by default | Breaks file paths in scripts (must update) |
| **`attrib +h`** (Windows hidden) | `attrib +h "folder"` | No path change needed | Obsidian must have "Show hidden files" OFF |
| **`userIgnoreFilters`** | Add `["/folder/"]` to `.obsidian/app.json` | Only affects Obsidian, not filesystem | Doesn't hide from file explorer sidebar — only Quick Switcher/Search/Graph |
| **CSS snippet** (when others fail) | Create `.obsidian/snippets/hide-folder.css` with CSS rules targeting the folder | Works regardless of Obsidian settings/themes; no path changes needed | Requires manual toggle ON in Obsidian (Settings → Appearance → CSS snippets) |

**CSS Snippet detailed workflow (when `attrib +h` + `userIgnoreFilters` still don't hide it):**

1. Create the snippet file:
   ```bash
   mkdir -p vault/.obsidian/snippets/
   ```
2. Write CSS with multiple selectors to cover different Obsidian versions:
   ```css
   .nav-folder[data-path="scripts"],
   .nav-folder[data-path="scripts/"],
   div[data-path="scripts"],
   div[data-path="scripts/"] {
     display: none !important;
   }
   ```
3. **User must manually enable in Obsidian:**
   - Settings → Appearance → CSS snippets
   - Click Refresh (🔄) — the snippet name should appear
   - Click the toggle button ON
   - Full restart of Obsidian may be needed
4. If snippet toggle ON but still visible:
   - Verify the `data-path` attribute value matches Obsidian's exact DOM (may be just folder name, or name with trailing slash)
   - Test snippet is loading: temporarily replace content with `body { background: red !important; }` to confirm CSS loading
   - Try toggling snippet OFF → ON again
   - Restart Obsidian fully (not just reload)

**Best practice:** dot-prefix for permanent hiding (rename + update script paths), `attrib +h` for quick temporary hiding, CSS snippet as last resort for folders that can't be renamed.

### Windows File Restore Issue

Observed behavior: after `rm -rf` deletion from git-bash, deleted files reappear within seconds or after git commit/push.

**Root causes (in order of likelihood):**
1. **Obsidian Remotely Save plugin** — if enabled in `.obsidian/community-plugins.json`, this plugin syncs vault to remote (S3/WebDAV). When local files are deleted, plugin restores them from remote on next sync cycle. 
   - **Fix:** Temporarily disable plugin: remove `"remotely-save"` from `community-plugins.json`, delete files, re-enable plugin. Next sync will propagate deletions to remote.
   - **Prevention:** Configure plugin's ignore list to skip stale artifact folders, or use `remotely-save` sync settings that respect deletions.
2. **Windows Search Index** — holding file handles via NTFS caching.
3. **OneDrive / File History** — restoring from cloud/previous versions.

**Workarounds:**
1. Disable sync plugin first (most likely cause)
2. Use PowerShell `Remove-Item` instead of `rm -rf` (native NTFS, bypasses MSYS caching)
3. After deletion, add folder/file patterns to `.gitignore` so if Windows auto-restores them, git won't re-track them
4. If PowerShell fails, the process holding the handle must be identified (handle.exe, Process Explorer)
5. After working tree is clean, `git add -A && git commit` before files reappear

**Defense in depth layers (apply all for permanent solution):**
| Layer | Method | Effect |
|-------|--------|--------|
| 1 | Delete via PowerShell (not `rm -rf`) | Real NTFS deletion bypassing MSYS cache |
| 2 | Add to `.gitignore` | Even if Windows restores, git won't track |
| 3 | `git rm --cached` if accidentally re-added | Remove from index if `git add -A` picked up restored files |
| 4 | Disable Remotely Save plugin | Stops sync loop restoring files from remote |

## Examples / Case Studies

### Case 1: ops-lint → ops-index-sync (2026-06-22)
- 3,000-word SKILL.md → redirect, 2 cron jobs → 1, 2 scripts → 1 unified script
- See `references/2026-06-22-ops-lint-merge-case-study.md`

### Case 2: Command consolidation — ops-context-update + ops-weekly-connections → ops-weekly-report (2026-06-22)
- 3 commands → 1, 2 skills deleted, 1 log file archived, 13 vault files cleaned
- See `references/2026-06-22-command-consolidation-case-study.md`

### Case 3: vault-index-sync deprecation + vault-structure-audit overlap (2026-07-01)
- Code was already merged (06/2026) but skill documentation stayed stale for 3+ weeks
- Detected: stale `.kilo/` refs, standalone script refs, missing execution path
- See `references/2026-07-01-vault-index-sync-deprecation.md`

### Case 5: P&L wiki cascade delete (2026-07-10)
- 5 wiki pages deleted → 143 broken `- [[Name]]` lines across 48 active files + WIKI_GRAPH/FRONTMATTER_CACHE/INDEX entries.
- Fix: cascade cleanup (index + hub rows + mass wikilink strip) + `rebuild_wiki_index.py --graph --frontmatter`, then verify 0 active hits.
- Durable quirk learned: `&` in `01_P&L_Budget` path breaks `cd` in terminal → use absolute quoted `rm` / PowerShell `-LiteralPath`.
- See `references/2026-07-10-pl-wiki-cascade-delete.md`
- Standalone 112-line command reference → absorbed into parent file subsection
- Quick Map (15 rows) moved to §4C, cron schedule merged into §4B
- Detailed command specs discarded (low-value, Hermes knows from skills)
- Source file **deleted completely**, not just deprecated
- Updated 2 skill references + 1 vault reference
- See `references/2026-07-01-HERMES-COMMANDS-merge-case-study.md`

### Pattern: Warren's approval workflow
1. Present 3 columns: what each command does, overlap matrix, verdict
2. Ask: "Muốn tôi patch [target] rồi delete [source] luôn không?"
3. Execute: patch first, delete second, clean references third

### Pattern: File-to-section merge (vs skill-to-skill merge)

Use when a standalone reference file can be absorbed into a parent file's subsection.

| Check | Why |
|-------|-----|
| Content is informational only (not executable)? | ✅ Safe to merge |
| Parent file already has a related section? | ✅ Natural home |
| User uses the Quick Map, not detailed specs? | ✅ Low-value specs can be dropped |
| Can all references be updated? | ✅ Must verify no broken links |
| User prefers delete over deprecated? | ✅ Then delete, not mark deprecated |

**Steps:**
1. Identify what content is valuable (Quick Map) vs discardable (detailed specs)
2. Merge valuable content into parent file as a new subsection
3. Update all cross-references (vault + skills)
4. Verify no broken wikilinks or file references remain
5. If user prefers deletion → delete source file entirely
6. Document the deletion in parent file header ("Replaces [source]")

**Example:** See `references/2026-07-01-HERMES-COMMANDS-merge-case-study.md`

## Mem0 Cleanup Protocol

Use when Warren reports or you observe corrupted/duplicate entries in mem0 (e.g. escape sequences `\x1b[`, garbled Vietnamese chars like `cƩo`, `nõ`, `nói` injected into context).

### Detection
1. List entries: `mem0_list(page_size=200)` — examine each for:
   - Corrupted text (escape chars, garbled Unicode)
   - Duplicates (same content, different IDs)
   - Literal "dup of [N]" notes
   - Task artifacts ("ad-hoc verification: 5/5 passed", session fragments)
   - File paths (per MEM0 GATE, file paths are not durable facts)
2. Search for known signal: `mem0_search(query="pre-check case vespa update")`

### Deletion
1. Delete each entry with full UUID: `mem0_delete(memory_id="full-uuid-string")`
2. **⚠️ UUID format:** IDs from `mem0_list` are full UUIDs (`2ed46937-d1ee-496c-988f-f74d992b5b40`). Pass the ENTIRE string, not just the prefix. Short IDs cause `400 Bad Request` errors that crash qdrant.

### Recovery (when qdrant crashes)
1. Find qdrant PID: `tasklist //FI "IMAGENAME eq qdrant*"`
2. Kill: `taskkill //F //PID <pid>`
3. Restart: run `C:\Users\khoans\AppData\Local\qdrant\qdrant.exe --uri http://localhost:6333` as a background process
4. Verify: `curl -s http://localhost:6333/healthz`

### Post-cleanup
1. Verify: `mem0_list(page_size=200)` — confirm count dropped and no garbled entries remain
2. The count may stay at 20 even after deletions (entries below display threshold bubble up). Multiple delete rounds may be needed.
3. If duplicates reappear, check for fragment entries (partial text split from larger entries) — delete those too.

### Prevention
- Always use full UUIDs in mem0_delete calls
- Avoid storing conversation fragments or task artifacts (use MEM0 GATE: "7 ngày nữa còn giá trị?" + "durable fact?")
- When in doubt, skip save — prefer memory tool over mem0 for durable facts