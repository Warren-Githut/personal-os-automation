# No-Agent Git-Pushing Watcher — Pitfalls & Reject-Safe Skeleton

> Companion to cron-job-ops §11.10 (repo-corruption HARD rule) + §12.5/§12.6.
> Session: hourly-regen-commit-watcher (2026-07-27).

## 1. The corruption incident (what NOT to do)

Watcher ran `git pull --rebase --autostash origin HEAD` after commit.
Remote had commits Bố pushed from another machine (older SHA than local HEAD).
`pull --rebase` checked out the OLDER remote commit → entire working tree
became untracked (`?? vault/`), rebase conflict opened, `.git/index.lock`
orphaned → repo broken. Recovery: `git rebase --abort` + `rm .git/index.lock`
+ `git reset --hard <known-good-SHA>` (Bố approved).

**Rule: NEVER `pull`/`rebase`/`stash`/`checkout`/`reset --hard` inside a watcher.**
These move HEAD on a repo with uncommitted Bố-work → destroys/untracks everything.

## 2. Reject-safe do_commit_push() skeleton

```python
def do_commit_push():
    _run_git(["add"] + COMMIT_FILES)
    if not _run_git(["diff", "--cached", "--name-only"]):
        return None  # nothing to commit
    _run_git(["commit", "-m", "weekly: hourly regen (auto via ok 09)"])
    try:
        _run_git(["push", "origin", "HEAD"])
    except RuntimeError as e:
        _tg_red(f"PUSH REJECTED: {str(e)[:120]}. Bo pull thu cong hoac push tay.")
        raise
    return _run_git(["rev-parse", "--short", "HEAD"])
```
Push reject → 🔴 TG + sys.exit(1) + STOP. Bố pulls manually. No HEAD move.

## 3. Watcher anatomy (Warren 7-point compliant)

- **Unique trigger** (avoid clash with col/review crons): exact `"ok 09"`
  (case-insensitive, trimmed). Negative: bare `"ok"`, `"ok push"`, `"ok hourly"`,
  `"09 ok"` reversed → NO trigger.
- **Ack receipt immediately** (Warren point 6 — never silent): on trigger,
  send ✅ "Nhan duoc 'OK 09' tu Bo. Dang commit+push..." BEFORE doing work.
- **Success** → ✅ "Da push <hash>". **Failure** → 🔴 short error + sys.exit(1).
- **Week-guard** (commit once/week): state file `.hourly_regen_commit_state.json`
  saves `last_committed_week`; if == current week → SKIP entire run (no poll, no 409).
- **Private offset file** (`.hourly_regen_commit_offset.json`) — NOT shared with
  col_telegram_intake (avoid race if Bố runs manually off-schedule).
- **Mojibake gate**: ASCII prints only in no_agent cron; TG via plain-text sender
  (no parse_mode — vault filenames have `_` → Markdown 400).

## 4. E2E test-harness safety (avoid source deletion)

Test harness that creates temp commits MUST clean ONLY its own artifacts:
- Use a UNIQUE temp filename per run (`_e2e_<timestamp>.txt`) → no stale-tracked
  collision with prior runs.
- Cleanup = `git reset --soft <before>` + `git reset HEAD <tempfile>` + `rm tempfile`.
- NEVER `git reset --hard` in test harness against the real repo — it wipes Bố's
  uncommitted work. The 2026-07-27 incident started from an over-eager harness.
- Isolate watcher's STATE/OFFSET/ENV to a `tempfile.mkdtemp()` so no real TG poll
  (avoids 409 + avoids spamming Bố during dev).
