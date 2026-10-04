---
name: source-audit-before-edit
description: Audit before deleting files. Prevents wrongful deletes.
status: active
created: 2026-07-28
version: 1.0
triggers:
  - about to create or edit or delete a file in profile/scripts or vault/.scripts
  - user says clean up or remove or delete or build X for me
  - grep or find returned empty or errored and you are tempted to conclude the file does not exist
  - audit the codebase or what scripts handle X
  - before any rm of a script a cron depends on
---

# Source Audit Before Edit

> **Core rule:** NEVER conclude a file is missing, unused, or yours-to-delete from a
> single grep/find that returned empty or errored. Audit properly first. On
> 2026-07-28 an agent built a duplicate Telegram review-approval bot, then on
> cleanup DELETED review_telegram_sender.py (thinking it was its own build) —
> it was the ORIGINAL system script cron review-telegram-sender depended on.
> Pipeline broke until restored from git. This skill prevents that class of error.

## When this gate fires (MANDATORY)

Before ANY of these, run the audit below:
- Creating a new script/skill that seems missing
- Editing an existing script/skill
- Deleting/removing any file (cleanup, rollback)
- Acting on a grep/find result that was empty or errored

## Audit procedure (do all 4)

### 1. Distinguish not found from command failed
On Windows/MSYS, find and rg frequently timeout or IO-error on large trees
and return EMPTY — NOT file absent. A blank result is ambiguous.
- If a search returned 0 matches, RE-RUN bounded: grep -rl PATTERN <specific_dir>
  on a known-small directory (e.g. profile/scripts/) instead of the whole ~/.
- If find timed out (exit 124), narrow the -maxdepth and path.
- Only treat missing as true after a bounded, successful (exit 0) search.

### 2. Find the ACTUAL system that already does the job
Before building a replacement, locate the existing pipeline:
- Grep the real script dirs: vault/.scripts/, profile/scripts/, skills/**/scripts/.
- For Telegram/review/COL: check vault/.scripts/review_intake.py,
  vault/.scripts/review_response_handler.py, vault/.scripts/lusine-ops/lusine_ops/telegram_bot.py.
- Read the SKILL.md BUT verify against disk — SKILL.md can have doc-drift
  (ops-review SKILL.md described a bot that did not exist on disk; a build plan
  review-approval-build-2026-07-28.md was approved but the real flow used
  [review] intake + ok review approve, already wired).

### 3. Check cron dependencies BEFORE deleting
```bash
cd profile && python3 -c "import json;d=json.load(open('cron/jobs.json'));[print(j['id'],j.get('name'),'->',j.get('script')) for j in d['jobs'] if 'FILE' in str(j.get('script',''))]"
```
If any cron references the file it is SYSTEM, not yours. Do not delete.

### 4. Git provenance check
```bash
git log --oneline -3 -- <rel/path>     # existed before your session = SYSTEM
git show <pre_agent_commit>:<rel/path>  # restore clean original if deleted
```
Prefer the commit BEFORE your agent session when restoring (not your own feat
commit, which may carry your modifications).

## Hard rules

- Do not delete system scripts you did not write. If unsure, move to
  _archives/scripts/ (reversible) instead of rm.
- Do not build a duplicate of an existing system. If a system already does X,
  wire into it; do not reinvent.
- Ask the user the real flow before building. ok review might mean
  approve pending not create new — confirm the actual intake/approval
  vocabulary (here: [review]=new intake, [col]=COL intake, ok review=approve).
- Bounded search only — never conclude from a timed-out/failed grep.

## Restore-if-deleted recipe (Windows/MSYS)

```bash
git show 0a0c4d5:scripts/review_telegram_sender.py > scripts/review_telegram_sender.py
# 0a0c4d5 = pre-agent weekly-backup commit (clean original, no agent edits)
```

## Related

- telegram-py-checklist — Telegram script quality gate (user-owned; adopt to patch).
- vault-parser-audit / vault-parser-review-pitfalls — parser-specific audit.
- ops-review (PINNED) — review queue watcher SKILL.md (has known doc-drift; only
  Warren can unpin and fix).
- review-approval-build-2026-07-28.md (under ops-cron-patterns/references) — the
  approved-but-misunderstood build plan; read it to see how doc-drift causes
  duplicate builds.
