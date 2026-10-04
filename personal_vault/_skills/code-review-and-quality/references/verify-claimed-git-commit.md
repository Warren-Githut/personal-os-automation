# Verify a Claimed Git Commit Against Reality

Use when reviewing work described by a summary/PR text that asserts "commit C did X / deleted file Y / updated file Z". The summary is a claim, not ground truth — verify against git before accepting it.

## Probe sequence (run against the actual repo)
```bash
cd <repo>
git cat-file -t <commit>                             # exists? else summary hash is wrong
git show --name-status <commit>                      # EXACT files touched: M/A/D per path
git show --stat <commit>                             # quick list
git ls-files <dir>/                                  # is claimed file tracked at all?
git log --all --oneline -- <path>                    # ever in history? empty = NEVER tracked
git rev-list --left-right --count origin/<b>...HEAD  # 0 0 = push verified / in sync
git status --short <folder>                          # ?? = folder untracked (edits disk-only)
```

## Decision rules
- Summary "deleted X in commit C" → TRUE only if `git show --name-status C` lists `D <path>` OR file absent from `git ls-files` AND was previously tracked. If `git log --all -- <path>` is empty, the file was an untracked local file: the commit did NOT delete it (disk-only op). Flag commit message as inaccurate; end-state may still be fine.
- Commit message lists a file change not in the diff → likely the containing folder is untracked (e.g. `.scripts/`). `git status --short <folder>` → `??` confirms. Edit is disk-only, invisible to a fresh clone.
- Stated repo path has NONE of the described artifacts → HUNT for a sibling repo before FAIL. Same machine often has multiple vaults/copies (`Stock_OS/stock_vault` vs `Personal_OS/personal_vault`). Broad search:
  ```bash
  find <home> -path "*/.git" -prune -o -iname "PERSONAL_MEMORY.md" -print 2>/dev/null
  find <home> -path "*/.git" -prune -o -iname "*telegram_capture_sleep*" -print 2>/dev/null
  ```
  The real work may be in a different repo whose branch/HEAD is the claimed commit.

## Real example (2026-08-03)
Summary: commit `3c0c447` "deleted scripts/telegram_capture_sleep_watchdog.py (included in commit)" + "updated SKILL.md".
Verification: `git show --name-status 3c0c447` → only 2 doc files (PERSONAL_MEMORY.md, automation/README.md). `git log --all -- scripts/telegram_capture_sleep_watchdog.py` empty → file never tracked. `.scripts/` untracked → SKILL.md edit disk-only. Verdict: summary overstated the commit; end-state correct.
