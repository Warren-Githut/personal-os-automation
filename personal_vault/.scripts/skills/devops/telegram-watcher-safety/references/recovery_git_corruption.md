# Recovery: Git Working-Tree Corruption (Warren vault, 2026-07-27)

## Symptom
After a `git pull --rebase` / `git reset --hard` during recovery or inside a
no_agent watcher, `git status` shows the ENTIRE `vault/` (or project root) as
untracked, OR after `rebase --abort` re-applies an autostash and HEAD jumps to
a stale/test commit. Looks destroyed — is recoverable.

## Root cause
`git pull --rebase --autostash origin HEAD` checks out the remote tip (which may
be an OLD commit) and untracks everything; `rebase --abort` then applies the
autostash and moves HEAD to a test commit. E2E test harness doing
`git reset --hard` + `rm` source files also deletes the script under test.

## Recovery recipe (when already corrupted)
1. STOP. Do not run more git mutations.
2. `git reflog` → find last KNOWN-GOOD commit (Warren's last real push).
3. BACK UP any uncommitted Bố files to /tmp FIRST
   (e.g. `cp vault/_journal/*.md /tmp/journal_backup/`).
4. `git stash clear` only AFTER confirming disk already has the needed files.
5. `git reset --hard <known-good-sha>` → restores correct working tree.
6. Verify key files on disk:
   `ls vault/.scripts/hourly_regen_commit_watcher.py`
   `grep -c "ok 09" vault/.scripts/lusine-ops/lusine_ops/telegram_bot.py`
7. `git push --force-with-lease origin master` to overwrite a junk test commit
   on remote — ONLY if that remote commit is your own E2E trash, never Bố's work.
8. Restore Bố's backed-up files from /tmp.

## Prevention (encode in no_agent watchers)
- NEVER `git pull --rebase` / `git reset --hard` in a cron script.
- Scoped: `git add <explicit files>` → `git commit` → `git push origin HEAD`.
- On push reject: red TG + raise, no auto-rebase.
- E2E tests: unique temp filenames per run; cleanup only temp commit
  (`reset --soft <before>`) + temp file; never `rm` production source.
