---
name: vault-restructure
description: Restructure and align vault architecture between two Obsidian vaults. Apply structural patterns (00_ prefix INDEX files, numbered wiki folders, Where To Go sections, missing directories) from a source vault to a target vault, with full cross-reference updates and verification.
version: 1.1
triggers:
  - reorg vault like
  - apply pattern from
  - restructure vault
  - align vault structure
  - vault reorg
  - vault architecture
  - 00_ prefix
  - numbered wiki folders
  - vault reorganization
platforms: [windows, macos, linux]
---

# Vault Restructure — Cross-Vault Pattern Alignment

> Apply an established vault structure pattern from one vault (source) to another (target).
> The pattern typically includes: INDEX files → `00_` prefix, wiki folders → numbered (`01_`–`NN_`), "Where To Go" sections, missing directories (`_journal/`, `_cases/projects/`), and full cross-reference updates.

---

## 1. Pattern Extraction (from source vault)

Before touching the target, understand the source vault's reorg pattern:

```bash
cd <source_vault>
git log --oneline -20
```

Look for commits with keywords: `prefix`, `rename`, `wiki`, `INDEX`, `reorg`, `restructure`, `numbered`.

Key patterns to extract:
| Element | How to detect |
|---------|---------------|
| INDEX prefix (`00_`) | `git log --all --oneline | grep -i "prefix\\|rename.*INDEX"` |
| Numbered wiki folders | `ls -d 30_KNOWLEDGE_BASE/wiki/[0-9]*/` |
| Where To Go sections | `grep -rn "Where To Go" 30_KNOWLEDGE_BASE/wiki/` |
| Missing dirs in target | Compare `find` output between source and target |
| SOUL/CONTEXT pattern | Read `00_CORE_LOGIC/CONTEXT.md §3` in source |

## 1b. Domain Deletion Pattern (v1.1)

When a wiki domain needs to be REMOVED (not just renamed), the workflow differs significantly from folder renaming.

**Interview first — confirm with user:**
1. Delete permanently (files + all cross-refs)?
2. Archive to `_archives/` first?
3. For pulse entries referencing the deleted domain: remove entire entry if exclusive to that domain, or strip the domain tag but keep factual content if cross-linked?

**Deletion steps:**
```bash
# 1. Delete folder + tracked files
git rm -r 30_KNOWLEDGE_BASE/wiki/<domain>/

# 2. Remove from INDEX files
#    00_WIKI_INDEX.md: remove section entirely, update total_files
#    00_INDEX.md: remove [[domain]] line
#    RETRIEVAL_MAP.md: remove table row

# 3. Update AGENTS.md
#    - Remove from vault tree diagram
#    - Remove from YAML domain validation list

# 4. Update agent config (.kilo/agent/<profile>.md)
#    - Remove from domain routing rules
#    - Remove from description strings

# 5. Remove cross-refs from scripts
#    fetch_slack_notes.py: remove DOMAIN_KEYWORDS entry
#    personal_lint.py: remove from VALID_DOMAINS
#    Any script with wiki/<domain>/ hardcoded path

# 6. Handle pulse entries referencing the deleted domain
#    weekly_connections_log.md: strip domain from `| Domains |` column
#    Remove "Most connected domain" lines if they reference deleted domain
#    Keep factual content (life data), only remove domain TAG
#    Lint_Report.md: remove from audit group lists

# 7. Remove file references from task lists
#    TODO_Kanban.md or task files linking to deleted domain files
```

## 2. Target Vault Analysis

Map the target vault's current structure:

```bash
cd <target_vault>
find . -maxdepth 4 -type d | sort > /tmp/target_dirs.txt
find . -maxdepth 4 -type f -name "*.md" | sort > /tmp/target_files.txt
```

Identify:
- Which INDEX files need `00_` prefix
- Which wiki folders need numbering
- Which directories are missing vs source
- All scripts, config files, and agent configs that reference old paths

## 3. Cross-Reference Scanning (critical — most failure-prone step)

Scan across ALL file types and ALL hidden/config directories:

```bash
# 3a — Wiki folder path references
grep -rn "wiki/<old_domain>/" --include="*.md" --include="*.py" --include="*.json" .
grep -rn "30_KNOWLEDGE_BASE/wiki/<old_domain>" --include="*.md" --include="*.py" --include="*.json" .

# 3b — Obsidian wiki links [[old_domain/...]]
grep -rn "\\[\\[<old_domain>" --include="*.md" .

# 3c — Old INDEX file names
grep -rn "WIKI_INDEX\\|PULSE_INDEX\\|CASES_INDEX" --include="*.md" --include="*.py" --include="*.json" .

# 3d — Scripts referencing paths
grep -rn "<old_path>" --include="*.py" .
```

**Scan these directories specifically:**
- `30_KNOWLEDGE_BASE/wiki/` — content + index files
- `10_PULSE/` — pulse logs with domain references
- `_cases/` — case files with cross-refs
- `_kilo/` — agent memories, config, checkout notes
- `.kilo/` — agent config, rules, skills (may reference paths)
- `.obsidian/` — workspace.json has hardcoded pane paths
- `scripts/` — Python scripts with string paths
- `00_CORE_LOGIC/` — CONTEXT.md, STOCK_MEMORY.md
- Root files: `AGENTS.md`, `README.md`, `HOME.md`
- Agent config: `.kilo/agent/<profile>.md`

## 4. Phased Execution Plan

Always create a plan with these phases:

### Phase 0 — Safety
```bash
git add -A && git stash push -m "pre-reorg-$(date +%Y-%m-%d_%H%M)"
# OR create a working branch (preferred for complex reorgs):
git checkout -b reorg/<pattern>-<date>
```
- Backup derived data files (FRONTMATTER_CACHE.json, WIKI_GRAPH.json)

### Phase 1 — INDEX rename (00_ prefix)
Use `git mv` for each INDEX file. Update internal self-refs immediately.

### Phase 2 — Wiki folder numbering + domain deletion
Two sub-patterns:
- **Rename:** `git mv wiki/<old> wiki/<NN_New>` per folder
- **Delete:** `git rm -r wiki/<domain>/` + follow §1b Domain Deletion Pattern

Then update ALL references in one batch:
- Use Python `execute_code` with `str.replace()` for bulk find-replace across all file types
- **Pitfall:** the `patch` tool has escape-drift on Windows when handling Python strings with `\"` — use `execute_code` + `str.replace()` instead of `patch` for bulk operations
- Target: all `.md`, `.py`, `.json`, `.yaml`, `.yml` files across the entire vault
- Script to run:
```python
from pathlib import Path
vault = Path("<target_vault>")
import os
replacements = {
    "wiki/<old_domain>/": "wiki/<NN_New_Domain>/",
    "30_KNOWLEDGE_BASE/wiki/<old_domain>/": "30_KNOWLEDGE_BASE/wiki/<NN_New_Domain>/",
}
for dirpath, dirnames, filenames in os.walk(str(vault)):
    skip = {'.git', 'node_modules', '.archive', '__pycache__'}
    dirnames[:] = [d for d in dirnames if d not in skip]
    for fn in filenames:
        if fn.endswith(('.md', '.py', '.json', '.yaml', '.yml')):
            fp = os.path.join(dirpath, fn)
            try:
                content = open(fp, 'r', encoding='utf-8').read()
            except: continue
            original = content
            for old, new in replacements.items():
                content = content.replace(old, new)
            if content != original:
                open(fp, 'w', encoding='utf-8').write(content)
```

### Phase 3 — Add missing directories
- `_journal/` — with INDEX.md (template + conventions)
- `_cases/projects/` — with .gitkeep
- `_inbox/INDEX.md` — routing rules if missing

### Phase 4 — Add "Where To Go" sections
To each renamed INDEX file, add a navigation table:
```markdown
## 🧭 Where To Go

| Nếu cần… | Thì mở… |
|-----------|---------|
| ... | ... |
```

### Phase 5 — Update SOUL/CONTEXT/memory
- `00_CORE_LOGIC/CONTEXT.md` §3 Vault Architecture — update all paths
- `AGENTS.md` — update vault tree + path references
- Any STOCK_MEMORY.md or profile memory with hardcoded paths
- Raw memory append: log the reorg pattern for future sessions

### Phase 6 — Regenerate derived data
- FRONTMATTER_CACHE.json → clear or regenerate
- WIKI_GRAPH.json → clear or regenerate
- RETRIEVAL_MAP.md → rewrite with new paths

## 5. Verification — 10-Test Checklist

Run these in order. Each test MUST pass before moving to the next.

### Test 1 — Git sanity
```bash
git status          # should show expected renames (no unexpected deletions)
git diff --stat     # content changes only in INDEX + Where To Go + path updates
```

### Test 2 — File existence (10+ critical paths)
Verify every renamed INDEX file and numbered folder exists at new location.

### Test 3 — No old [[wikilinks]] remain
```bash
grep -rn "\\[\\[<old_domain>" --include="*.md" . --exclude-dir=.git --exclude-dir=node_modules
```
→ Expected: 0 results

### Test 4 — No old wiki path references remain
```bash
grep -rn "wiki/<old_domain>/" --include="*.md" --include="*.py" --include="*.json" . --exclude-dir=.git
```
→ Expected: 0 results

### Test 5 — No old INDEX file names remain
```bash
grep -rn "WIKI_INDEX\\|PULSE_INDEX\\|CASES_INDEX" --include="*.md" --include="*.py" --include="*.json" . --exclude-dir=.git
```
→ Expected: only `00_WIKI_INDEX.md` etc. references remain

### Test 6 — No old absolute paths remain
For each old domain path:
```bash
grep -rn "30_KNOWLEDGE_BASE/wiki/<old_domain>" --include="*.md" --include="*.py" --include="*.json" . --exclude-dir=.git
```
→ Expected: 0 results

### Test 7 — Script execution smoke test
```bash
python scripts/<script1>.py --help  # at least doesn't crash on import
python scripts/<script2>.py          # no path-related error
```

### Test 8 — Workspace config
Check `.obsidian/workspace.json` for any old pane paths. Update manually if found.

### Test 9 — Final git diff
```bash
git diff --stat  # verify only expected files changed
```

### Test 10 — Domain deletion specific (if applicable)
If domains were deleted:
```bash
# Verify no remaining domain tag references in pulse entries
grep -n "↔ <deleted_domain>" 10_PULSE/weekly_connections_log.md
grep -n "↔ <deleted_domain>" 10_PULSE/Daily_Pulse.md
```
→ Expected: 0 results

## 6. Pitfalls

- **Hidden config files**: `.obsidian/workspace.json` and `.kilo/agent/*.md` have hardcoded file paths — NOT caught by standard `.md`-only grep.
- **Derived data needs regeneration**: FRONTMATTER_CACHE.json and WIKI_GRAPH.json store paths as JSON keys — patching is fragile. Regenerate.
- **`patch` tool escape-drift on Windows**: When patching Python files with double-quoted strings, `patch` escapes `"` → `\"` and fails with "Escape-drift detected". Use `execute_code` + `str.replace()` instead for bulk/regex replacements.
- **Script string paths**: Python scripts may have `Path(VAULT_ROOT / "30_KNOWLEDGE_BASE" / "wiki" / "health")` — won't break at import but WILL at runtime. Must update.
- **Git mv preserves history**: Always use `git mv` for renames, not OS-level `mv`.
- **Rollback plan**: `git stash pop` restores everything. For partial rollback, `git mv` back + revert path changes.
- **AGENTS.md ASCII tree**: Hardcoded folder names — must update manually.
- **Obsidian workspace.json panes**: Each pane stores a `file` path. Will silently break ("File not found") if moved. Update all pane paths.
- **Pulse domain tags vs factual content**: When deleting a domain, distinguish between domain TAGS (remove from `| Domains |` column) and factual content about that topic (preserve — it's life data, not a wiki reference). Remove "Most connected domain" stats lines referencing deleted domains.
- **Interview gate required**: Always interview before starting — confirm delete vs archive vs skip, and pulse entry handling preference.

## 7. Commit Message Convention

```
reorg: full vault pattern — 00_ INDEX, numbered wiki, _journal/, Where To Go, all cross-refs updated
```

## 8. References

Session-specific detail (reorg patterns, escape-drift workaround, domain deletion checklist) stored in `references/2026-07-01_Personal_OS_full_reorg.md`.
