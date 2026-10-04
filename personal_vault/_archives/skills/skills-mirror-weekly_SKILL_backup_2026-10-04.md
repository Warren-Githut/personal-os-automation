---
name: skills-mirror-weekly
description: "Weekly bulk mirror: AppData personal_profile/skills -> Personal_OS/personal_vault/_skills/ + git commit/push + Telegram. Executed by cron job weekly-skills-mirror (no_agent). Trigger: 'run skills mirror', 'mirror skills'."
version: 1.0.0
type: automation
status: active
owner: Hermes
cron_job_id: 47fdaa2facb5
schedule: "0 3 * * 0"
last_updated: 2026-10-04
tags: [skill, sync, mirror, backup, git, cron, vault]
related_skills: ["skill-sync", "bulk-mirror-sync", "vault-git-push"]
---

# skills-mirror-weekly - Bulk Skills Mirror (cron)

> Mirror the ENTIRE `personal_profile` skill library from AppData into
> `Personal_OS/personal_vault/_skills/` so GitHub tracks it. Hermes still LOADS skills
> from AppData (primary = AppData; `_skills/` is a mirror artifact only).

## Script

`~/AppData/Local/hermes/profiles/personal_profile/scripts/skills_mirror_weekly.py`

```bash
python3 skills_mirror_weekly.py --dry-run   # mirror + stage, NO commit/push/Telegram
python3 skills_mirror_weekly.py             # full flow incl. Telegram
```

## Cron

| Field | Value |
|-------|-------|
| Job ID | `47fdaa2facb5` |
| Name | `weekly-skills-mirror` |
| Schedule | `0 3 * * 0` (Sunday 03:00) |
| Mode | `no_agent=true` (script only, zero LLM tokens) |
| Deliver | `local` (script sends its own Telegram message) |
| First fire | 2026-10-11 03:00 |

## Flow

1. **Build manifest** - walk `SRC/`, skip: top-level dot entries (`.archive/`,
   `.curator_ledger.jsonl`, `.usage.json`, `.curator_backups/`), **top-level symlinks**,
   and caches (`__pycache__/`, `.pytest_cache/`, `.pyc`/`.pyo`).
2. **Mirror** - copy missing/size-changed files; prune every `_skills/` file absent from
   the manifest.
3. **Sync remote** - `ff-only` pull when only the remote moved ahead; **never rebase,
   never force-push** when diverged.
4. **Commit + push** - stage ONLY `personal_vault/_skills/`; commit message
   `chore: mirror personal-profile skills to vault (YYYY-MM-DD HH:MM)`.
5. **Telegram** - report `OK / COMMITTED-NOT-PUSHED / no changes / GIT ERROR`.
   **No changes -> send NOTHING** (watchdog: empty stdout = silence).

## Pitfalls (all hit for real on 2026-10-04)

| Pitfall | Fix |
|---------|-----|
| **`git diff --name-status` exits 0 even WITH changes** - checking `code == 0` reported a false "no changes" while 609 files were staged | Test for EMPTY OUTPUT (`if not lines`), never the return code. Only `--quiet` reflects rc. |
| **Top-level symlink gets followed** - `personal_profile/skills/personal-commands` symlinks to `warren-profile/skills/personal-commands` (warren-owned). The old script copied 30 warren files into the personal mirror | `build_manifest()` skips `entry.is_symlink()`; the mirror is **manifest-driven**, so those 30 stale files self-pruned. Report warns about skipped symlinks. |
| **Wrong profile spelling** - the old script used `personal-profile`, actual dir is `personal_profile` (underscore) -> `[ERROR] Source not found` | Verify a path with `ls -d` before writing any script around it. |
| **Nested dot-dirs leak into the mirror** if only the top level is checked (`find . -name SKILL.md -path "*/.*/*"` -> 118 hits under `.archive/`) | Skip dot entries at EVERY level: `entry.name.startswith(".")` while walking top level + `IGNORE_DIRS` for nested paths. |
| **Missing `.gitignore` cache rules** -> `_skills/` collects `__pycache__`/`.pytest_cache` | Add to `Personal_OS/.gitignore`: `personal_vault/_skills/**/__pycache__/`, `**/.pytest_cache/`, `*.pyc`, `*.pyo`. |
| **Diverged branch** -> `git push` rejected with `fetch first` | Check `ahead`/`behind` BEFORE pushing: `ff-only` pull when only remote is ahead; when both sides moved -> skip push + report (never auto rebase/force). |
| **Missing git identity** -> "Author identity unknown" | Repo already sets `user.name=Warren` / `user.email=warren@local`. Never set global. |

## Verify (do not trust the script's own stdout)

```bash
cd C:/Users/khoans/Documents/Personal_OS
git log --oneline -2                        # commit mirror
git rev-list --left-right --count master...origin/master   # 0  0 = fully synced
git ls-tree -r --name-only origin/master -- personal_vault/_skills | wc -l   # 580
git ls-tree -r --name-only origin/master | grep -c "personal_vault/_skills/personal-commands"  # 0 = no leak
```

## Anti-goal

- **NEVER** load skills from `_skills/` - Hermes loads from AppData.
- **NEVER** `git add -A` - stage only `personal_vault/_skills/`.
- **NEVER** rebase / force-push / amend when diverged.
- **NEVER** send Telegram when nothing changed.
- **NEVER** touch `personal-commands/` (warren-owned; mirrored separately into
  `Warren_OS_Local/vault/_skills/`).