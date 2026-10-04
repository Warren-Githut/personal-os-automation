---
name: vault-audit-discipline
description: Audit Warren code first. Timeout search is not "not found".
status: active
created: 2026-07-28
version: 1.0
triggers:
  - about to create a new script/skill/cron in warren-profile
  - "X doesn't exist, I'll build it"
  - searching for an existing file/skill before building
  - audit source before code
  - broad find/grep returned timeout or IO error
---

# Vault Audit Discipline (Warren-profile)

> Load this BEFORE creating any new artifact in the Warren ops stack. The #1 failure
> mode observed (2026-07-28): an agent concludes "file X does not exist" from a
> TIMED-OUT or IO-ERRORING broad search, then builds X from scratch — when X (or its
> approved build plan) already exists. This wastes a full session and produces dead code.

## Hard Rule — Inconclusive Search ≠ Absence

A broad recursive search (`find /c/Users/khoans`, unbounded `search_files` across the
home tree) that returns:
- `Command timed out after 60s`, OR
- `IO error for operation on ... (os error 3)`

...is **INCONCLUSIVE**, not "empty". Concluding absence from it is a false negative.

**STOP-THE-LINE protocol before declaring anything missing:**
1. Broad search timed out / IO-errored? -> treat as "no answer", NOT "not found".
2. Re-scope to a BOUNDED directory you KNOW should contain the target:
   - profile scripts: `C:/Users/khoans/AppData/Local/hermes/profiles/warren-profile/scripts`
   - vault scripts: `C:/Users/khoans/Documents/Warren_OS_Local/vault/.scripts`
   - a specific skill dir you already located
3. Use a BOUNDED-COST tool:
   - `search_files(pattern='symbol', path=BOUNDED_DIR, file_glob='*.py')`
   - OR terminal `grep -rl "symbol" BOUNDED_DIR 2>/dev/null`
   - NEVER `find /c/Users/khoans` (unbounded -> 60s timeout every time).
4. ONLY a BOUNDED search returning 0 matches lets you conclude absence.
5. Still unsure? GREP the `skills/` tree for the feature NAME — an approved-but-unbuilt
   plan doc may already pin the design (see below). Then ask Warren.

## Hard Rule — Check for an Existing Build Plan Before Building

Warren's ops stack has features that are **designed and approved but not yet coded**,
documented in plan docs under:
- `skills/ops/ops-cron-patterns/references/*-build-*.md`
- other `references/` docs with "Build X Plan" / "APPROVED by Warren" headers

Before building from scratch, GREP `skills/` for the feature keyword. If a plan exists:
- Follow its approved destination/option (do NOT reinvent or pick a different target).
- Note its status (APPROVED-not-executed vs DONE) so you don't duplicate.

Example (2026-07-28): `review-approval-build-2026-07-28.md` documented the exact
telegram_bot.py + review_response_handler.py design (option A: append markdown SSOT,
NOT GSheet). An agent that skipped the plan search built a redundant bot.

## Why This Matters Here

Warren is non-IT and expects the agent to KNOW what exists. Building duplicate/dead code
contradicts his "hate over-engineering" rule (WARREN_MEMORY). A 2-minute bounded re-scope
saves a 30-minute wrong build.

## Red Flag to Self-Catch

If you are about to write "X does not exist, so I will create it" and your only evidence
is a timed-out `find` -> STOP, re-scope, grep skills/, then ask if still unclear.

## References
- `references/bounded-search-recipes.md` — copy-paste terminal/grep recipes that stay under the 60s timeout for the Warren home tree.
