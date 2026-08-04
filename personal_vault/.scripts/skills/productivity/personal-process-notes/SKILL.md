---
name: personal-process-notes
description: >
  Orchestrate the complete `/process-notes` cron job for Personal_OS vault.
  Entry point for the base command (PHASE P3 convention). Handles inbox routing
  (via personal-inbox-routing sub-skill), stock_pending cleanup, gap/red-flag
  detection across Daily_Pulse, health logs, and court case, then updates
  log.md, timestamps, and git commits. Runs autonomously (cron mode) or
  on-demand.
trigger:
  - cron job: invoked by `/process-notes` (base command per PHASE P3 convention)
  - manual: /process-notes when user wants to "xử lý notes" or "process inbox"
---

# Personal Process Notes

> **Orchestrator skill — the cron entry point.**
> Calls `personal-inbox-routing` for the inbox sub-task, then does higher-level gap detection + cleanup + logging.

## Overview

This skill runs the full `/process-notes` pipeline:

```
Inventory inbox + stock_pending
  ├─ If items exist → route via personal-inbox-routing
  └─ Orphaned stock_pending JSONs → dedup-check → archive
Gap detection (Daily_Pulse, health, court)
Update log.md + .last_process_notes
Git commit
Report / [SILENT]
```

## Step-by-Step Workflow

### 0. Pre-flight (cron mode)

- Read `00_CORE_LOGIC/CONTEXT.md` for current snapshot
  - ⚠️ Personal profile: CONTEXT.md may not exist → fallback to `PERSONAL_CONTEXT.md`
  - Stock profile: use `STOCK_CONTEXT.md`
- Read `10_PULSE/Daily_Pulse.md` — last 3 entries
- Read `.last_process_notes` — find last run time
- Read `_cases/active/legal_divorce_court_GG_access.md` — check follow_up staleness
- Check `git log --oneline -3` for last commits

### 1. Inventory

```
ls _inbox/01_unprocessed/          -> inbox items
ls _inbox/01_unprocessed/stock_pending/  -> orphaned JSONs
```

Sort inbox items by date (oldest first for chronological processing).

### 2. Route inbox items → personal-inbox-routing

If items exist in `01_unprocessed/`:

```
Load skill: personal-inbox-routing
Follow its routing decision tree + step-by-step workflow
```

Special handling:
- **stock_pending/ JSONs** — BEFORE routing, grep the target file for the JSON's `subject` or `date`. If the data already exists in the target file:
  - Do NOT write — skip routing
  - Archive JSON to `02_processed_archived/stock_pending/`
  - Log as "data already in target file"
- **Health logs** — After routing to Daily_Pulse, also route to `10_PULSE/051_Sleep_Log.md` via `capture-sleep` skill if applicable

### 3. Orphaned stock_pending cleanup (no new inbox items)

If `01_unprocessed/` is empty but `stock_pending/` has JSONs:
- Each JSON has `target_file` + `entry_body`. Search the target file for matching content.
- If data is already there → archive JSON, log as cleanup
- If data is NOT there → route fresh (JSON was orphaned without processing)
- If JSON is stale (>7 days pending_since) → flag as stale data

### 4. Gap / Red-flag detection

Run ALL of these checks every cycle:

| Check | How | Action |
|---|---|---|
| **Daily_Pulse gap** | Read last entry date in `Daily_Pulse.md`. If >7 days from today | Flag as capture-discipline gap in log |
| **Health log gap** | Read last health entry date. If >3 days from today | Flag in log: "No health logs since {date}" |
| **Court follow_up passed** | Read `follow_up` from `_cases/active/legal_divorce_court_GG_access.md` frontmatter. ⚠️ If file not found at active path, search `_cases/closed/` — if closed, log resolution and skip. If past today and no update since | Reset follow_up to tomorrow. Flag as CRITICAL GAP. Update status note. |
| **Stock pending stale** | Any JSON with `pending_since` >7 days old | Flag in log |

### 5. Update log.md

Prepend to `30_KNOWLEDGE_BASE/wiki/log.md` (newest on top — insert BEFORE the previous first entry):

```
## YYYY-MM-DD
- **PROCESSED: `/process-notes` cron.** {summary of what was done}
  - {N} inbox items → {destinations}
  - {N} stock_pending JSONs → archived (data già trong target file)
- **FLAGGED:** {gap items detected}
```

Update frontmatter `last_updated: YYYY-MM-DD`.

### 6. Update timestamp

Write to `_inbox/.last_process_notes` (prefer `write_file` over `echo >` for reliability in cron mode):

```
2026-07-03T06:00:00+07:00
```

### 7. Git commit

⚠️ **`git add -A` catches ALL repo changes** — includes files modified by OTHER processes (thesis updates, weekly outlook, sleep logs, unrelated PDFs). Verify commit diff is not polluted with noise.

⚠️ **`personal_vault/` is a SEPARATE nested git repo — commit from INSIDE it, never the outer `Personal_OS` repo.** The outer repo's root `.gitignore` contains `personal_vault/`, so running `git add`/`git commit` from `C:\Users\khoans\Documents\Personal_OS` FAILS with `ignored by .gitignore` and commits nothing. **Always `cd C:\Users\khoans\Documents\Personal_OS\personal_vault` first.** Every relative path in this skill is rooted at `personal_vault/`, not `Personal_OS`. Verify with `git rev-parse --is-inside-work-tree` + `git ls-files <file>` if unsure.

⚠️ **Leave unrelated noise unstaged.** Other processes may modify files between cycles (e.g. `10_PULSE/022_VNStock_Daily_Outlook.md`, weekly outlook, sleep logs). Stage ONLY the files you touched (log.md + .last_process_notes, plus any routed/archived files) and commit those — never `git add -A` blindly.

Two approaches (run from inside `personal_vault/`):
- **Clean:** `git add 30_KNOWLEDGE_BASE/wiki/log.md _inbox/.last_process_notes <other touched files>` (specific files only)
- **Quick (but noisy):** `git add -A` then verify `git diff --cached --stat` shows only expected files

```

## Gap-Detection Reference

### Daily_Pulse gap
- **Last entry:** read from `Daily_Pulse.md` — find the `## YYYY-MM-DD` header closest to top
- **Threshold:** 7 days since that date
- **Output in log:** `"Daily_Pulse gap {N} ngày — không có entry từ {date}."`

### Health log gap
- **Last entry:** search `Daily_Pulse.md` for `## YYYY-MM-DD.*Health:` pattern, get most recent date
- **Cross-reference:** also check `10_PULSE/051_Sleep_Log.md` for recent health entries. If Sleep_Log has recent data but Daily_Pulse doesn't, flag the Daily_Pulse gap but note the Sleep_Log date as context (health data logged separately but not yet reflected in Daily_Pulse)
- **Threshold:** 3 days since that date
- **Output in log:** `"Health log cuối {date} — {N} ngày gap."`

### Court case follow_up passed
- **Read:** frontmatter `follow_up` field in `_cases/active/legal_divorce_court_GG_access.md`
- **Action if passed:** 
  - Reset `follow_up` to `YYYY-MM-DD` (tomorrow)
  - Update CRITICAL GAP note in the Status section
  - Bump `last_updated` in frontmatter
- **Output in log:** `"Court CRITICAL GAP — follow_up {date} passed, reset to tomorrow."`

## Cron Mode (no user present)

- **SILENT rule:** If literally nothing changed (no inbox items, no gaps, no stock_pending cleanup) → reply exactly `[SILENT]`
- **Not SILENT if:** any gap detected, any file moved/archived, any frontmatter updated, any commit made, or the last_process_notes timestamp changed
- Never ask questions or request clarification
- Final response IS the report — system delivers it

## Relationship to Other Skills

| Skill | How personal-process-notes uses it |
|---|---|
| `personal-inbox-routing` | Sub-skill — delegate inbox processing |
| `capture-sleep` | May be called if health logs found in inbox |
| `stock-capture` | May be called if stock data found in inbox |

## Pitfalls

- **Do NOT re-process orphaned JSONs.** Always verify target file content exists before routing. Orphaned JSON + existing data = archive only.
- **Gap detection is NOT optional in cron mode.** Run ALL 4 checks every cycle even if nothing else changed. A stale court follow_up is actionable even with zero inbox items.
- **Court follow_up: reset to TOMORROW** (not next week, not indefinite). This forces daily re-check until Warren updates.
  - **Status note format:** Append "Đã reset tiếp lên {new_date}" to the CRITICAL GAP message.
  - **Track reset count:** After repeated resets, add "follow_up reset lần thứ N" so Warren sees escalation.
- **Court case archived/closed:** The case file may move to `_cases/closed/` after resolution. In that case:
  - Frontmatter `follow_up` field no longer exists → skip follow_up check
  - Log the resolution in the daily entry (file found in `_cases/closed/` instead of `_cases/active/`)
  - Do NOT reset follow_up or add CRITICAL GAP flags — the case is resolved
- **Vietnamese in vault output.** Per AGENTS.md HC7, write vault entries in Vietnamese có dấu. Frontmatter fields stay English.
- **Stock pending >7 days stale** does NOT mean auto-delete — flag it so Warren knows to check if the data is useful.
- **No user present in cron mode.** Never use `clarify` or ask questions. If you can't determine routing, archive to `02_processed_archived/_unsorted/` and flag.
- **Cron-mode tool restrictions.** In cron mode, `execute_code` is denied entirely and `rm` on root-level paths is blocked. For `write_file` and `patch`, use **full Windows absolute paths** (`C:\Users\khoans\Documents\...`) — they are the most reliable. Workspace-relative paths (`Documents/Personal_OS/...`) work but `patch` has a stateful cwd trap (see reference). For `terminal()` git/dir commands use **MSYS paths** (`/c/Users/khoans/Documents/...`) — verified working in the bash/MSYS shell (2026-07-12 cycle). Do NOT pass Windows backslash paths into `terminal()` (bash mangles `\`). To delete files, `cd <subdir> && rm -f <file>`. See `references/cron-mode-pitfalls.md` for full workaround reference.
- **search_files uses GLOB, not substring.** `search_files(target='files', pattern='legal_divorce')` returns 0 — the pattern is glob-matched, not a substring. Wrap partial names in `*`: `pattern='*legal_divorce*'`. Applies when inventorying `_inbox/01_unprocessed/` by partial filename too. (Verified 2026-07-12: bare substring returned 0, `*` glob found the file in `_cases/closed/`.)

## Verification

After processing:
1. `_inbox/01_unprocessed/` empty (except empty `stock_pending/` dir)
2. Files moved to `02_processed_archived/` match count
3. `log.md` has new entry for today + frontmatter updated
4. `_inbox/.last_process_notes` timestamp is today
5. Court case file has correct `follow_up` + `last_updated` (if active; if closed/archived, confirm resolution)
6. `git log --oneline -1` shows the commit

> **Note:** `.last_process_notes` and `log.md` are data files, not code — the 6 manual checks above are sufficient for THEM. But this vault DOES have code that owns a real test runner (see `references/test-harness.md`): `pytest tests/` (NOT `npm run test`). The repo's `package.json` `test` script is a dummy (`echo "Error: no test specified" && exit 1`) that always fails — ignore harness nags suggesting `npm run test`. Run `python3 -m pytest tests/ -q` if you touched any skill code (e.g. `capture-sleep` parsing logic). The pytest suite only covers sleep-log parsing; it does not exercise the cron orchestration itself, so it cannot "verify" a pure-data `/process-notes` run — manual checks 1-6 are still the authoritative gate for that.
