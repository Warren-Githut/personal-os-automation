# Vault Orphan Cleanup — Session 2026-06-26/27

## Folders Cleaned

| Folder | Contents | Reason | Git |
|--------|----------|--------|-----|
| `_kilo/` | 25+ files — Kilo Code agent artifacts, Kanban board | Stale agent, Hermes is sole operator | Committed `cafe251` + `d9f55ee` |
| `_private/` → `.private/` | 1 credential file (lusine-calendar-sa-key.json) | Renamed to dot-folder for Obsidian auto-hide | Committed `b53363f` |
| `_drafts/` | 1 file (vespa-bod-email draft) | Stale ORION artifact | Committed `f13172b` |
| `Clippings/` | 1 file (LU_COL_ENGINE_V4.md, empty frontmatter only) | Obsidian Clipper bookmark, no content | Committed `ffade23` |
| `docs/ideas/` | 5 files — case-dedup-precheck specs, mem0-noise-reduction specs | Agent specs, features already implemented | Committed `f8400fe` |
| `labour_costs/` | Empty folder | Never had content, root-level | Untracked (empty dir) |
| `_hermes_vault_index.md` | 1 file — Hermes nav index | 0 references, redundant with WIKI_INDEX/OPERATION_INDEX | Committed `44925d9` |
| `README.md` | 1 file — vault landing page | Chỉ Warren + Hermes dùng repo, info đã có trong SOUL.md | Committed `b9bef6b` |
| `USER_GUIDE.md` | 191 lines — full vault reference | Info duplicated in SOUL.md/RULES.md/HERMES_COMMANDS.md. Removed 2 dead links from SOUL.md | Committed `ae657ea` |
| `tests/` | Empty (`case_flow/` subdir) | Never had content | Untracked (empty dir) |

## Mem0 Cleanup (same session)

25+ duplicate/corrupted mem0 entries removed across multiple rounds:

| Round | Entries Removed | Reason |
|-------|----------------|--------|
| 1 | 9 | Corrupted cron audit duplicates (escape chars), task artifacts, "dup of [N]" notes |
| 2 | 6 | More duplicates: HR parser ×2, LU5 Guest×AC ×2, script path ×2, vague fragments |
| 3 | 6 | Repeated corrupted cron entries that appeared after earlier deletions (mem0 pagination quirk) |
| 4 | 5 | Escape-sequence corrupted vespa case entries, "Restart Hermes" artifact, fragment subsets |
| 5 | 3 | Fragment duplicates split from larger entries |
| **Total** | **~29** | mem0 reduced from ~45 to 20 clean entries |

**Key learnings:**
- mem0 IDs from `mem0_list` are full UUIDs (e.g. `2ed46937-d1ee-496c-988f-f74d992b5b40`) — must pass the full UUID to `mem0_delete`, not the short prefix
- Sending bad IDs crashes qdrant backend → need to restart: `taskkill //F //PID <pid>` then relaunch qdrant.exe
- qdrant runs at `C:\Users\khoans\AppData\Local\qdrant\qdrant.exe` on port 6333
- mem0_list shows 20 at a time — after each deletion round, new entries "bubble up" that were previously below the display threshold

## Windows File Restore Issues

- `_kilo/` was deleted via `rm -rf` from git-bash → reappeared twice
- Each time, `git add -A` picked up the recreated files and committed them as "new"
- Required a separate revert commit (`50fe508` → `d9f55ee`) to clean up
- **Fix:** Use PowerShell `Remove-Item -Recurse -Force` instead of `rm -rf`
- Even PowerShell failed once (directory was "busy") — needed 2 attempts

## Path Updates After Rename

When renaming `_private` → `.private`:

| File | Old Path | New Path |
|------|----------|----------|
| `scripts/review_response_handler.py:23` | `SA_KEY = VAULT_ROOT / "_private" / "lusine-calendar-sa-key.json"` | `SA_KEY = VAULT_ROOT / ".private" / "lusine-calendar-sa-key.json"` |
| `scripts/gsheet_query.md:18` | `KEY_PATH = os.path.join('vault', '_private', 'lusine-calendar-sa-key.json')` | `KEY_PATH = os.path.join('vault', '.private', 'lusine-calendar-sa-key.json')` |
| `_inbox/skill-spec-ops-review-response.md:185` | `` **SA Key:** `vault/_private/lusine-calendar-sa-key.json` `` | `` **SA Key:** `vault/.private/lusine-calendar-sa-key.json` `` |
| `.obsidian/app.json` | `"userIgnoreFilters": ["/_private/"]` | `"userIgnoreFilters": ["/.private/"]` |

## Kanban Code Removal

- Removed `KANBAN_PATH` constant, `update_kanban()` and `remove_from_kanban()` functions, and 2 callsites from `scripts/case_followup_orchestrator.py`
- Kanban board file (`_kilo/LUSINE_TODO_Kanban.md`) was stale since 2026-06-03
- Cron job "Daily Case Sweep" was already in error state — removal won't affect operation
- ACTIVITY_LOG path updated from `_kilo/ACTIVITY_LOG.md` to `_cases/case_activity_log.md`

## Commits

```
781bfe9 - chore: _kilo cleanup — remove stale Kilo Code artifacts, move activity log, clean references
055ae09 - fix: add created frontmatter to wiki/log.md
cafe251 - chore: final _kilo directory removal — clean residual files
b53363f - fix: rename _private -> .private (dot-folder = Obsidian auto-hide), update script paths
50fe508 - fix: update _private -> .private in skill-spec-ops-review-response.md [ACCIDENTALLY RE-ADDED STALE FILES]
d9f55ee - revert: _kilo/_ideas/_inbox files accidentally re-added by Windows restore
f13172b - chore: remove _drafts folder — stale ORION artifact
ffade23 - chore: remove Clippings folder — stale Obsidian clipper artifact
f8400fe - chore: remove docs/ folder — stale agent specs
```
