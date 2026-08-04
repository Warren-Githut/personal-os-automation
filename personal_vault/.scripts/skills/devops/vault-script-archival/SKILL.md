---
name: vault-script-archival
description: Safe script archival workflow for Warren's vault — verifies existence, checks import dependencies, archives to dated folder with rollback docs, single commit.
category: devops
---

# Vault Script Archival — Safe Cleanup Workflow

## When to Use
- Removing unused scripts from `vault/scripts/`
- Any cleanup where rollback must be instant (30 seconds via `git mv`)
- Before archiving: verify no CI workflows or other scripts import the candidates

## Core Principle
**Archive (move), never delete physically.** Every archived file is one `git mv` away from restore.

## Workflow (8 Steps)

### 1. Define Archive List
Explicit list in a variable — no glob patterns that might grab active files.

### 2. Verify Existence (STOP Gate)
```bash
for f in $ARCHIVE_LIST; do
  if [ -f "vault/scripts/$f" ]; then echo "OK: $f"; else echo "MISSING: $f"; fi
done
```
**STOP if any MISSING** — paste list, ask user.

### 3. Verify No External Imports (STOP Gate)
```bash
for f in $ARCHIVE_LIST; do
  stem=$(basename "$f" .py)  # adjust for .ps1/.mjs/.bat/.cmd
  grep -r "import $stem\|from $stem\|require.*$stem" \
    vault/scripts/ .github/workflows/ vault/_kilo/ 2>/dev/null \
    | grep -v "Binary" | grep -v "$f:" || echo "No external refs for $f"
done
```
**STOP if any hits outside the file itself** — paste matches, ask user.

### 4. Create Dated Archive Folder
```bash
mkdir -p vault/scripts/.archive/YYYY-MM_phaseN/
```

### 5. Git Move Files
```bash
for f in $ARCHIVE_LIST; do
  git mv "vault/scripts/$f" "vault/scripts/.archive/YYYY-MM_phaseN/$f"
done
```

### 6. Create README in Archive Folder
```markdown
# Phase N — Archived Scripts (YYYY-MM-DD)

## Why archived
- Not called by CI (.github/workflows/)
- Not imported by other scripts
- Warren confirmed not used in last 30 days (audit interview)

## Rollback
Single file: git mv vault/scripts/.archive/YYYY-MM_phaseN/<file> vault/scripts/<file>
All: git revert <commit-hash>

## Archived files (N total)

| File | Reason archived |
|---|---|
| ... | ... |
```

### 7. Verify Counts
```bash
ls vault/scripts/*.py vault/scripts/*.ps1 ... | wc -l   # Expected: original - archived
ls vault/scripts/.archive/YYYY-MM_phaseN/ | wc -l       # Expected: archived + 1 (README)
```
**STOP if counts differ by > ±2.**

### 8. Single Commit + Report
```bash
git add vault/scripts/.archive/YYYY-MM_phaseN/
git commit -m "chore(scripts): archive N unused scripts (Phase N, X% cleanup)
...
Rollback: git mv <archive>/<file> vault/scripts/<file>
README: vault/scripts/.archive/YYYY-MM_phaseN/README.md"
```
Create `vault/_kilo/.archive/PHASE_N_REPORT.md` with:
- Commit hash
- Table of archived files with reasons
- Verification numbers
- Risk flags (confidence levels)
- Rollback procedure

## Risk Flags in Report
| Level | Criteria |
|-------|----------|
| HIGH | Script name suggests one-shot (debug/test/fix/setup), feature disabled, duplicate |
| MEDIUM | Warren said "not used but might" (NO-but-might) |
| LOW | Exact duplicate of kept file |

## Pitfalls to Avoid
- ❌ Don't use `rm` — physical delete breaks instant rollback
- ❌ Don't batch multiple phases in one commit — each phase needs independent rollback
- ❌ Don't skip import check — broke CI in Phase 2B when `gsheet_to_vault.py` still referenced parsers
- ❌ Don't archive files outside the explicit list — scope creep
- ❌ Don't touch `.github/workflows/` files

### 🔴 RECOVERY — file "deleted" is usually ARCHIVED, not gone (2026-07-27 lesson)
When a vault `.py`/`.sh` "disappears" (only `.pyc` bytecode cache remains, or a user's documented command `.../gen_X_dashboard.py` fails with "No such file"), it is almost always **moved to `_archives/`** (the safe-archive pattern above), NOT physically deleted. Git history still has it.

**The 0-byte trap:** `git show <sha>:<original/path>` returns 0 bytes when the file was moved (the original path no longer exists at that sha). Recovering blindly into a non-existent path = empty file.

**Correct recovery recipe (ALWAYS do this):**
```bash
cd <vault-root>
# 1. Find the LAST commit that still had the file at ANY path
git log --all --oneline -- "*<filename>" | head -1
# 2. List the EXACT path the file lived at in that commit (it may be under _archives/)
git ls-tree -r --name-only <sha> | grep -i "<filename>"
# 3. Recover using that REAL path (NOT the assumed original path)
git show "<sha>:<real/path/from/step2>" > <destination/path>
# 4. Verify non-zero bytes
wc -c <destination/path>
```
**Concrete case (2026-07-27):** `gen_item_sales_dashboard.py` "missing" at `vault/10_OPERATION_DATA/.parsers/`. Real path was `vault/_archives/parsers/gen_item_sales_dashboard_archived_2026-07-27.py` (committed in `0002443`). Recover from there, then optionally copy back to `.parsers/`.

**Rule:** NEVER assume the original vault path is intact after an archive. Always `git ls-tree -r` to discover the real archived path first. A 0-byte recovered file = wrong source path, retry with the discovered path.

## Templates
See `templates/archive-readme.md` for the README template.
See `templates/phase-report.md` for the report template.

## Scripts
See `scripts/verify-archive-list.sh` — runs Steps 2 & 3 automatically.