# Vault Rename / Move / Permanent-Deletion Discipline

> Class-level procedure for renaming, moving, or permanently deleting files and
> folders in the Personal_OS vault. Embed into any vault-ops task instead of
> rediscovering it.

## A. RENAME / MOVE a file or folder

1. **Scan EVERY reference BEFORE moving** (grep the whole `personal_vault/`):
   - Obsidian wikilinks: `[[OldName]]`
   - Relative paths: `../OldFolder/` or `OldFolder/`
   - Absolute paths: `30_KNOWLEDGE_BASE/wiki/02_Health/...`
   - Index files: `00_WIKI_INDEX.md`, `00_INDEX.md`, `RETRIEVAL_MAP.md`
   - Scripts with a hardcoded `VAULT_ROOT` path
   - Skill `related:` frontmatter fields
2. **Move with history:** `git mv <old> <new>` (keeps blame).
3. **Renumber** when moving into a subfolder (`aa_x` → `01_x`) — ask Warren first.
4. **Fix refs in dependency order:** indexes → internal wikilinks → cross-folder →
   scripts → skills. Then re-grep until zero hits.
5. **Lint verify** before committing.
6. **Commit SEPARATELY** from any deletions in the same session.
7. Leave historical logs (`STOCK_MEMORY.md`, `log.md`) untouched.

⚠️ **Partial link-fix = correction prompt from Warren.** Half-updated references are
worse than not starting.

### replace_all path-drop pitfall

`patch` with `replace_all` on a substring inside a LONG absolute path eats shared
prefixes. Example: a file contains
`30_KNOWLEDGE_BASE/wiki/health/Genetics/...`; replacing
`wiki/health/Genetics/` → `02_Health/ac_Warren_Genetics_Report/` yields
`30_KNOWLEDGE_BASE/02_Health/...` — the `/wiki/` segment is LOST.

Fix: `new_string` must re-include every segment that is still valid, e.g.
`wiki/02_Health/ac_Warren_Genetics_Report/`. Rule: the replacement re-includes every
still-correct piece of the path; never let the match swallow a sibling prefix.

## B. PERMANENT DELETION of a folder that "keeps coming back"

Symptom: Warren says "I deleted it several times and it is still there". A generator
recreates it. Diagnose the source, then kill all layers.

### Step 1 — diagnose

- `git ls-files <path>` → non-empty means git-tracked
- `git log --oneline -3 -- <path>` → a recent commit that RE-ADDS the files
- `grep -rn "<path>" scripts/` → a hardcoded path in a Python script
- `grep -rn "<path>" cron/output/*.md` → a cron job that recreates and commits it

### Step 2 — 4-layer kill

```bash
git rm -r --cached <path>    # 1. drop from the index
rm -rf <path>                # 2. drop from disk
git commit -m "chore: remove <path>"   # 3. make it stick
# 4. patch the generator (cron job / skill step / script constant)
```

⚠️ `rm -rf` alone fails when git still tracks the path — the index restores it.
⚠️ `git rm` without a commit leaves it staged, so the next unrelated commit sweeps
the deletions in.

### Step 3 — verify

```bash
git ls-files <path> | wc -l   # must be 0
find <path> -type f 2>/dev/null | wc -l   # must be 0
python3 -m py_compile scripts/*.py        # exit 0 if a script constant changed
```

### Symlink caveat (2026-07-14)

Some generator skills are symlinked between profiles
(`personal_profile/skills/personal-commands` → `warren-profile/skills/personal-commands`
— same inode). Patching through the personal_profile path edits the warren-profile
canonical file. That is usually the intent, but pass `cross_profile=True` and confirm
which repo the fix must land in before committing.

## C. Cron-mode notes

`execute_code` is unavailable in cron sessions — use `search_files`, `read_file`,
`terminal(git)`, or a temp `.py` run through `terminal`.