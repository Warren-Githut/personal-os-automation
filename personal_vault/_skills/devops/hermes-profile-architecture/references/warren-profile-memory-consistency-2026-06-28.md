# Warren-Profile Memory Loop Consistency Fixes (2026-06-28)

## Context
Cross-file audit of SOUL.md, MEMORY.md, USER.md, AGENTS.md for warren-profile memory loop. Found 6 contradictions.

## Fixes Applied

| # | Problem | File | Fix |
|---|---------|------|-----|
| 1 | Vault root pointed to Stock_OS/stock_vault (wrong) | `MEMORY.md Preferences` | → Warren_OS_Local/vault |
| 2 | Sync path used `~/.hermes/` (wrong) | `SOUL.md §2.1 + §2.5` | → `AppData/Local/hermes/.../memories/MEMORY.md` |
| 3 | "End-of-session proposal" still in write governance | `SOUL.md §2.2` | → "Proposal on Git Commit" |
| 4 | Raw log desc "end-of-session" still in table | `SOUL.md §2.1 table` | → "khi Warren git commit" |
| 5 | Step 8 "sang profile" vague | `MEMORY.md Weekly Cycle step 8` | → exact AppData path |
| 6 | AGENTS.md missing MEMORY.md in session checklist | `AGENTS.md` | → added step 3 |

## Key Lesson
Cross-file consistency requires explicit audit after any change. A 14-point verification script caught all issues in one pass.
