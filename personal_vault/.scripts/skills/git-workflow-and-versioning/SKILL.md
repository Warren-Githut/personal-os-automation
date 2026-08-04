---
name: git-workflow-and-versioning
description: Structures git workflow practices. Use when making any code change. Use when committing, branching, resolving conflicts, or when you need to organize work across multiple parallel streams.
---

# Git Workflow and Versioning

## Overview

Git is your safety net. Treat commits as save points, branches as sandboxes, and history as documentation. With AI agents generating code at high speed, disciplined version control is the mechanism that keeps changes manageable, reviewable, and reversible.

## When to Use

Always. Every code change flows through git.

## Core Principles

### Trunk-Based Development (Recommended)

Keep `main` always deployable. Work in short-lived feature branches that merge back within 1-3 days. Long-lived development branches are hidden costs — they diverge, create merge conflicts, and delay integration. DORA research consistently shows trunk-based development correlates with high-performing engineering teams.

```
main ──●──●──●──●──●──●──●──●──●──  (always deployable)
        ╲      ╱  ╲    ╱
         ●──●─╱    ●──╱    ← short-lived feature branches (1-3 days)
```

This is the recommended default. Teams using gitflow or long-lived branches can adapt the principles (atomic commits, small changes, descriptive messages) to their branching model — the commit discipline matters more than the specific branching strategy.

- **Dev branches are costs.** Every day a branch lives, it accumulates merge risk.
- **Release branches are acceptable.** When you need to stabilize a release while main moves forward.
- **Feature flags > long branches.** Prefer deploying incomplete work behind flags rather than keeping it on a branch for weeks.

### 1. Commit Early, Commit Often

Each successful increment gets its own commit. Don't accumulate large uncommitted changes.

```
Work pattern:
  Implement slice → Test → Verify → Commit → Next slice

Not this:
  Implement everything → Hope it works → Giant commit
```

Commits are save points. If the next change breaks something, you can revert to the last known-good state instantly.

### 2. Atomic Commits

Each commit does one logical thing:

```
# Good: Each commit is self-contained
git log --oneline
a1b2c3d Add task creation endpoint with validation
d4e5f6g Add task creation form component
h7i8j9k Connect form to API and add loading state
m1n2o3p Add task creation tests (unit + integration)

# Bad: Everything mixed together
git log --oneline
x1y2z3a Add task feature, fix sidebar, update deps, refactor utils
```

### 3. Descriptive Messages

Commit messages explain the *why*, not just the *what*:

```
# Good: Explains intent
feat: add email validation to registration endpoint

Prevents invalid email formats from reaching the database.
Uses Zod schema validation at the route handler level,
consistent with existing validation patterns in auth.ts.

# Bad: Describes what's obvious from the diff
update auth.ts
```

**Format:**
```
<type>: <short description>

<optional body explaining why, not what>
```

**Types:**
- `feat` — New feature
- `fix` — Bug fix
- `refactor` — Code change that neither fixes a bug nor adds a feature
- `test` — Adding or updating tests
- `docs` — Documentation only
- `chore` — Tooling, dependencies, config

### 4. Keep Concerns Separate

Don't combine formatting changes with behavior changes. Don't combine refactors with features. Each type of change should be a separate commit — and ideally a separate PR:

```
# Good: Separate concerns
git commit -m "refactor: extract validation logic to shared utility"
git commit -m "feat: add phone number validation to registration"

# Bad: Mixed concerns
git commit -m "refactor validation and add phone number field"
```

**Separate refactoring from feature work.** A refactoring change and a feature change are two different changes — submit them separately. This makes each change easier to review, revert, and understand in history. Small cleanups (renaming a variable) can be included in a feature commit at reviewer discretion.

### 5. Size Your Changes

Target ~100 lines per commit/PR. Changes over ~1000 lines should be split. See the splitting strategies in `code-review-and-quality` for how to break down large changes.

```
~100 lines  → Easy to review, easy to revert
~300 lines  → Acceptable for a single logical change
~1000 lines → Split into smaller changes
```

## Branching Strategy

### Feature Branches

```
main (always deployable)
  │
  ├── feature/task-creation    ← One feature per branch
  ├── feature/user-settings    ← Parallel work
  └── fix/duplicate-tasks      ← Bug fixes
```

- Branch from `main` (or the team's default branch)
- Keep branches short-lived (merge within 1-3 days) — long-lived branches are hidden costs
- Delete branches after merge
- Prefer feature flags over long-lived branches for incomplete features

### Branch Naming

```
feature/<short-description>   → feature/task-creation
fix/<short-description>       → fix/duplicate-tasks
chore/<short-description>     → chore/update-deps
refactor/<short-description>  → refactor/auth-module
```

## Working with Worktrees

For parallel AI agent work, use git worktrees to run multiple branches simultaneously:

```bash
# Create a worktree for a feature branch
git worktree add ../project-feature-a feature/task-creation
git worktree add ../project-feature-b feature/user-settings

# Each worktree is a separate directory with its own branch
# Agents can work in parallel without interfering
ls ../
  project/              ← main branch
  project-feature-a/    ← task-creation branch
  project-feature-b/    ← user-settings branch

# When done, merge and clean up
git worktree remove ../project-feature-a
```

Benefits:
- Multiple agents can work on different features simultaneously
- No branch switching needed (each directory has its own branch)
- If one experiment fails, delete the worktree — nothing is lost
- Changes are isolated until explicitly merged

## The Save Point Pattern

```
Agent starts work
    │
    ├── Makes a change
    │   ├── Test passes? → Commit → Continue
    │   └── Test fails? → Revert to last commit → Investigate
    │
    ├── Makes another change
    │   ├── Test passes? → Commit → Continue
    │   └── Test fails? → Revert to last commit → Investigate
    │
    └── Feature complete → All commits form a clean history
```

This pattern means you never lose more than one increment of work. If an agent goes off the rails, `git reset --hard HEAD` takes you back to the last successful state.

## Commit Message Format (L'Usine Ops Standard)

**Format:**
```
<type>: <short description>

<optional body explaining why, not what>
```

**Types:**
- `feat` — New feature (NL case commands, parser, handler)
- `fix` — Bug fix (prefix parsing, body builder, close file move)
- `refactor` — Code change that neither fixes a bug nor adds a feature (simplifications)
- `test` — Adding or updating tests (battle test suite)
- `docs` — Documentation only
- `chore` — Tooling, dependencies, config

**Real example from this session:**
```
feat: add natural-language case management commands (update/edit/close-nl)

Adds Telegram-style natural language interface for case operations:
- [update case <fuzzy>] <payload> — appends dated thread entry (newest on top)
- [edit case <fuzzy>] <payload> — in-place frontmatter/body edit
- [close case <fuzzy>] — closes with auto lesson learned/insight vs success criteria

Three new modules:
- case_brain_nl_parser.py: prefix detection, fuzzy matching, tokenization
- case_brain_nl_handler.py: case create/update/edit/close with review flow
- ops_cases_cli.py: 3 new CLI commands (update/edit/close-nl) with --dry-run

Battle-tested: 8/8 NL tests + 8/8 orchestrator tests passing (16 total)
- 5 flexible scenarios covering prefix parsing, dated blocks, newest-on-top, body building, thread appending
- 3 A/B tests covering edit vs update behavior, close lesson learned, fuzzy matching

Code simplifications applied:
- Parser: shared _match_keywords helper, simplified title extraction
- Handler: removed WORKSPACE_ROOT alias, unused imports, now_time_str, simplified build_case_body_from_payload
- CLI: removed dead code, moved yaml import to top, simplified list_cases logic
```

**Change Summary Template (append to commit body):**
```
CHANGES MADE:
- scripts/case_brain_nl_parser.py: shared _match_keywords helper, detect_prefix 3-tuple return
- scripts/case_brain_nl_handler.py: removed WORKSPACE_ROOT, unused imports, simplified build_case_body_from_payload
- scripts/ops_cases_cli.py: 3 new NL commands, dead code removed, yaml import hoisted
- scripts/tests/test_nl_parser_handler.py: 5 flexible + 3 A/B battle tests

THINGS I DIDN'T TOUCH (intentionally):
- case_followup_orchestrator.py: core logic unchanged, behavior preserved
- existing _cases/ active/closed files: no data migration

POTENTIAL CONCERNS:
- close_case_with_review file move timing: closed file shows old content (investigate on next close)
- fuzzy match threshold (0.35) may need tuning with more cases
```

This level of detail lets future reviewers understand scope, risk, and intentional omissions at a glance.
```
<type>: <short description>

<what was added/changed>
- bullet list of capabilities

<battle-tested>: <test count> <category> tests passing (<total> total)
- <flexible scenarios covered>
- <a/b distinctions covered>

<code simplifications applied>:
- <module>: <specific simplifications>
```

This pattern catches wrong assumptions early and gives reviewers a clear map of the change. The "DIDN'T TOUCH" section is especially important — it shows you exercised scope discipline and didn't go on an unsolicited renovation.

## Pre-Commit Hygiene

Before every commit:

```bash
# 1. Check what you're about to commit
git diff --staged

# 2. Ensure no secrets
git diff --staged | grep -i "password\\|secret\\|api_key\\|token"

# 3. Run tests
npm test

# 4. Run linting
npm run lint

# 5. Run type checking
npx tsc --noEmit
```

### Warren Rule: ALWAYS Ask Before Commit or Push

Warren must approve every commit/push. NEVER auto-commit or auto-push.

Before committing:
1. Print a summary of files changed (+/- lines)
2. Show the diff or describe what each file changes
3. Ask "Muốn commit không?" or "Push luôn không?"
4. Wait for explicit approval ("ok", "commit", "push") before executing

This applies to ALL profiles (warren, personal, stock). Only Hermes chat TUI is the
approval channel — gateway/Telegram commits are never auto-approved.

**Pitfall (2026-07-13): "commit push" is NOT a blank check to commit the WHOLE tree.**
When Warren says "commit push" / "commit đi", the working tree may hold changes from
OTHER sources — e.g. the Monday auto-parser pipeline (07_COL, 03_COGS, 04_LTO, 05_Review,
06_GrabFood, 09_Hourly, 11_Item, 14_MenuGP, TODAY, synthesis, FRONTMATTER_CACHE) plus an
intentional file DELETE tied to a rename in a DIFFERENT session. Blind `git add -A` +
commit ships all of it under one message and can commit a BROKEN state (e.g. the rename
deleted the old file but 4 parser scripts still hardcode the old path → next pipeline run
crashes with FileNotFoundError).

Correct behavior when "commit push" arrives and the tree is mixed:
1. `git status --short` → triage WHAT is actually staged-to-be.
2. If tree contains foreign/unrelated changes + an intentional delete → STOP and surface it:
   - Confirm the delete is intentional (it may be a rename from another session).
   - Verify the rename is COMPLETE (all code consumers repointed — see `vault-ssot-edit`
     RENAME section) BEFORE committing the delete. If consumers still point at the deleted
     file, fix them FIRST, then commit.
   - Offer Warren options: (A) scope a single coherent commit, (B) let the auto-pipeline's
     own cron commit its slice, (C) leave it.
3. Never `git add -A` on the Warren vault repo (see "Hermes Artifact Hygiene" below) — stage
   explicitly by trusted subdir / file so unrelated artifacts don't ride along.
4. Present the 5-point pre-flight (WHAT/WHY/CONTENT/RISK/APPROVAL) and wait for "ok".


Automate this with git hooks:

```json
// package.json (using lint-staged + husky)
{
  "lint-staged": {
    "*.{ts,tsx}": ["eslint --fix", "prettier --write"],
    "*.{json,md}": ["prettier --write"]
  }
}
```

### Pitfall: `git reset --hard` to undo a BAD commit also NUKES GOOD edits bundled in it

When you make a bad commit (e.g. a backfill with a CRLF bug) and `git reset --hard <good-parent>` to undo it, **EVERYTHING** in that commit is wiped from the working tree — including unrelated GOOD edits that rode along in the same commit (e.g. a `_frontmatter.py` hardening that was committed together with the buggy backfill).

**Symptom (2026-07-13 COL session):** backfill commit `efab0fa` had a CRLF bug (`---created:` glued, 90 files corrupted). I `git reset --hard 1e7e05c` to undo it — but the `_frontmatter.py` `created` auto-inject (a separate good fix also in `efab0fa`) was ALSO destroyed. Pipeline-layer guard silently gone. Had to re-diagnose + re-apply + re-verify + force-push.

**Correct behavior when undoing a mixed/buggy commit:**
1. If the bad commit contains ONLY the bad change → `git reset --hard <parent>` is fine.
2. If the bad commit bundles a GOOD change you still need → **do NOT hard-reset the whole thing.** Instead:
   - `git revert <bad>` → new commit reversing the bad (keeps history, preserves siblings), OR
   - `git checkout <bad> -- <good-file>` to restore just the good file, then fix the bad part separately, OR
   - `git reset --soft <parent>` (keeps changes staged) → unstage, then `git checkout -- <bad-only-files>` to discard only the broken parts, keep the good parts.
3. After any reset/undo, **re-verify the good siblings are still present** (re-run their tests) before moving on. Don't assume "undo bad = only bad undone."

**Rule:** A commit that mixes a risky bulk operation (backfill 90 files, mass rename) with a logic fix should ideally be SPLIT — but if already bundled and you must undo, undo surgically, not with a sledgehammer `reset --hard`.

### Pitfall: `git checkout -- <file>` destroys uncommitted changes

Running `git checkout -- <file>` restores the file from HEAD -- ALL uncommitted changes are LOST. This includes unsaved edits from the current session.

**Before running destructive git commands:**
```bash
# Check for uncommitted changes
git status --short
# If there are staged or unstaged changes you want to keep, commit first:
git add <file> && git commit -m "savepoint: before destructive operation"
# Then proceed with checkout/reset
```

This applies to: `git checkout -- <file>`, `git reset --hard`, `git clean -fd`.

### Pre-Commit Hook Pitfall: Vault Frontmatter Validation

When committing vault markdown files (cases, wiki, MOCs), pre-commit hooks that validate YAML frontmatter (e.g., battle-test) may BLOCK the commit if required fields are missing:

```
[battle-test] COMMIT BLOCKED by battle-test pre-commit hook
CRITICAL: AGENTS.md -- Frontmatter: missing ['created']
```

**Fix:** Add the missing required field before retrying:
- Required fields per AGENTS.md: `type`, `created`, `updated`, `status`
- Use `patch` tool to insert missing fields
- Then `git add <file> && git commit` (retry passes)

**Detection before commit:**
```bash
# Check for missing frontmatter fields in staged files
for f in $(git diff --cached --name-only -- '*.md'); do
  head -15 "$f" | grep -q '^created:' || echo "⚠️ $f missing 'created'"
done
```

When writing a pre-commit hook that checks files within a subdirectory (e.g., a vault inside a monorepo), **`git diff --cached --name-only` returns paths relative to the repo root, not the subdirectory.**

```bash
# WRONG — double-nests the path:
VAULT_DIR="repo/vault"
STAGED=$(git diff --cached --name-only)  # returns "vault/foo.md"
fp="$VAULT_DIR/$STAGED"                  # resolves to "repo/vault/vault/foo.md" ✗

# RIGHT — use repo root:
REPO_ROOT=$(git rev-parse --show-toplevel)
STAGED=$(git diff --cached --name-only)  # returns "vault/foo.md"
fp="$REPO_ROOT/$STAGED"                  # resolves to "repo/vault/foo.md" ✓
```

This applies to any hook that needs to read staged file contents — always join against `REPO_ROOT`, not the working subdirectory. Test with a deliberately malformed file to verify both the detection and the path resolution before shipping.
```

### Pre-Commit Hook Pitfall: Windows/MSYS Path Double-Translation (Git for Windows)

When the vault lives under `C:\Users\...\` and git runs via MSYS bash (Git for Windows default shell), a hook that does `python "$VAULT_DIR/scripts/foo.py"` passes an MSYS-style path like `/c/Users/.../foo.py`. The `python` invoked is the **Windows** interpreter, which interprets `/c/Users/...` as `C:\c\Users\...` → `FileNotFoundError`. This silently blocks EVERY commit (exit 1) even though the script exists.

**Symptom (2026-07-08, Personal_OS vault):**
```
python: can't open file 'C:\c\Users\khoans\Documents\Personal_OS\stock_vault\scripts\diacritics_check.py': [Errno 2] No such file or directory
```
The file exists at `C:\Users\khoans\...` — the `c\` prefix is the bug.

**Fix:** convert the path to a Windows-native path inside the hook before invoking python/powershell:
```sh
WIN_SCRIPT="$(cygpath -w "$DIACRITICS_SCRIPT" 2>/dev/null || echo "$DIACRITICS_SCRIPT")"
python "$WIN_SCRIPT"
# for powershell:
WIN_YAML="$(cygpath -w "$YAML_SCRIPT" 2>/dev/null || echo "$YAML_SCRIPT")"
powershell.exe -ExecutionPolicy Bypass -NoProfile -File "$WIN_YAML" -StagedOnly
```
`cygpath -w` is available in the MSYS/Git-bash environment. The `|| echo` fallback keeps it working if `cygpath` is ever missing.

**Detection before shipping a hook:** run `git commit --allow-empty -m test` after writing the hook; if it errors with `C:\c\...` path, apply the `cygpath -w` fix.

### Pitfall: LF/CRLF False-Dirty on Batch Commit (Windows)

When staging many files edited by different tools (Obsidian = CRLF, Hermes = LF), `git status` may show a file as modified purely due to line-ending, even when content is identical. `git add` then reports it as staged, but the subsequent `git diff --cached` / commit may show it as unchanged (0 effective diff) — it silently drops out of the commit.

**Detection before batch commit (2026-07-08):**
```bash
# Verify a "modified" file actually changed content (ignores eol differences)
git diff --ignore-all-space HEAD -- path/to/file.md
# empty output = no real content change, only line-ending re-save — safe to skip
```
If empty, the file was only re-saved with different line endings — do NOT worry that it dropped from the commit; no data was lost. To avoid the noise entirely, set `core.autocrlf=input` or add `*.md text eol=lf` to `.gitattributes`.

## Handling Generated Files

- **Commit generated files** only if the project expects them (e.g., `package-lock.json`, Prisma migrations)
- **Don't commit** build output (`dist/`, `.next/`), environment files (`.env`), or IDE config (`.vscode/settings.json` unless shared)
- **Have a `.gitignore`** that covers: `node_modules/`, `dist/`, `.env`, `.env.local`, `*.pem`

## Warren Vault Repo: Hermes Artifact Hygiene (Pitfall)

Warren's vault repo (`Warren_OS_Local`) runs Hermes Desktop + multiple profiles. Over a session, Hermes pollutes `git status` with internal artifacts that are NOT vault source and must never be committed. The cleanup pattern from 2026-07-07:

**Artifacts to gitignore (add to `.gitignore`):**
```
# Hermes desktop attachments drop zone (PDFs/XLSX/CSV from Telegram/desktop — not vault source)
.hermes/desktop-attachments/

# Hermes internal state (plans, specs, qdrant flag)
.hermes/plans/
.hermes/specs/
.qdrant-initialized

# Temp verify scripts (Windows temp path artifacts from ad-hoc hermes-verify-*.py)
C:*/Users*AppData*Local*Temp*hermes-verify-*.py
```
Note: the temp-verify glob uses `*` wildcards because git status mangles the Windows path (`C:\Users\...` shows as `C\357\200\272Users...` UTF-8 bytes) — a literal path won't match.

**Hard-delete (not ignore) when found committed/untracked:**
- `*.orig` backup files (e.g. `COST_LOG.md.orig` from a patch conflict) — pure trash
- Orphan directories at repo ROOT that duplicate vault content (e.g. `30_KNOWLEDGE_BASE/` appearing at root when it belongs under `vault/`) — verify it's a duplicate/orphan first, then `rm -rf`
- Stray dashboard HTML dropped at root (e.g. `working_hours_dashboard_May_Jun_2026.html`) — move into vault or delete
- Ghost `hermes-verify-*.py` entries in `git status` that `find` cannot locate on disk — git status artifact from a mangled temp path; safe to ignore (cannot `git rm` an outside-repo path)

**Workflow:** before ANY `git add -A` or broad commit, run `git status --short` and triage: commit only vault source (cases, wiki, _inbox specs, automation state). Stage explicitly file-by-file or by trusted subdir — never `git add -A` on this repo. After adding gitignore rules, confirm with `git check-ignore <junk-path>` returns the path (ignored) while `git check-ignore vault/.../OIL_Tracking.md` returns non-zero (tracked).

**Stock-profile data leak:** `.hermes/desktop-attachments/` also catches stock BCTC PDFs (PNJ/VCB) that land in the warren vault via shared desktop. Ignore (don't delete — Warren may need them in stock-profile later); they are not warren-vault source.

## Using Git for Debugging

```bash
# Find which commit introduced a bug
git bisect start
git bisect bad HEAD
git bisect good <known-good-commit>
# Git checkouts midpoints; run your test at each to narrow down

# View what changed recently
git log --oneline -20
git diff HEAD~5..HEAD -- src/

# Find who last changed a specific line
git blame src/services/task.ts

# Search commit messages for a keyword
git log --grep="validation" --oneline
```

## Example Commit Messages from L'Usine Ops

### Feature: Add Telegram Bot Integration
```bash
feat: add Telegram bot integration (aiogram)

- telegram_bot.py: polling bot using aiogram 3.x
- Wires to existing NL handler (handle_message)
- Env config via .env: TELEGRAM_BOT_TOKEN, TELEGRAM_ALLOWED_USERS
- /start, /help commands + NL prefix handlers ([new/update/edit/close case ...])
- Allowlist via TELEGRAM_ALLOWED_USERS (empty = dev mode allow all)
- Graceful error handling with user-friendly messages

Added:
- scripts/lusine-ops/telegram_bot.py
- scripts/lusine-ops/.env.example
- Updated SKILL.md with bot usage docs
```

### Feature: Natural-Language Case Management Commands
```bash
feat: add natural-language case management commands (update/edit/close-nl)

Adds Telegram-style natural language interface for case operations:
- [update case <fuzzy>] <payload> — appends dated thread entry (newest on top)
- [edit case <fuzzy>] <payload> — in-place frontmatter/body edit
- [close case <fuzzy>] — closes with auto lesson learned/insight vs success criteria

Three new modules:
- case_brain_nl_parser.py: prefix detection, fuzzy matching, tokenization
- case_brain_nl_handler.py: case create/update/edit/close with review flow
- ops_cases_cli.py: 3 new CLI commands (update/edit/close-nl) with --dry-run

Battle-tested: 30/30 tests passing (16 existing + 14 new)
- 5 flexible scenarios covering prefix parsing, dated blocks, newest-on-top, body building, thread appending
- 3 A/B tests covering edit vs update behavior, close lesson learned, fuzzy matching

Code simplifications applied (per code-simplification skill):
- Parser: shared _match_keywords helper, simplified title extraction
- Handler: removed WORKSPACE_ROOT alias, unused imports, now_time_str, simplified build_case_body_from_payload
- CLI: removed dead code, moved yaml import to top, simplified list_cases logic
```

### Fix: Make Google Calendar Integration Optional
```bash
fix: make Google Calendar integration optional (push_gcal)

- Orchestrator: try/except import push_gcal, set _CALENDAR_AVAILABLE flag
- All calendar functions check _CALENDAR_AVAILABLE before proceeding
- Graceful degradation: case ops work without push_gcal, calendar skipped with warnings
- CLI wrapper: --no-calendar default=True for zero-friction UX
- Works across all 3 profiles (warren, lusine, personal)

CHANGES MADE:
- scripts/case_followup_orchestrator.py: optional import, _CALENDAR_AVAILABLE flag, graceful degradation
- scripts/lusine-ops/lusine_ops/commands/new.py: --no-calendar default=True

TESTS: 30/30 pass (8 orchestrator + 8 NL + 7 vault_resolver + 6 smoke)
```
## Red Flags

- Large uncommitted changes accumulating
- Commit messages like "fix", "update", "misc"
- Formatting changes mixed with behavior changes
- No `.gitignore` in the project
- Committing `node_modules/`, `.env`, or build artifacts
- Committing Hermes internal artifacts (`.hermes/desktop-attachments/`, `.hermes/plans/`, `.hermes/specs/`, `.qdrant-initialized`, temp `hermes-verify-*.py`, `*.orig` backups, orphan root dirs) into the Warren vault repo — see "Warren Vault Repo: Hermes Artifact Hygiene" above
- Long-lived branches that diverge significantly from main
- Force-pushing to shared branches
- Running destructive scripts (`git checkout -- <file>`, `git reset --hard`) on uncommitted work without checking `git status --short` first

## Verification

For every commit:

- [ ] Commit does one logical thing
- [ ] Message explains the why, follows type conventions
- [ ] Tests pass before committing
- [ ] No secrets in the diff
- [ ] No formatting-only changes mixed with behavior changes
- [ ] `.gitignore` covers standard exclusions
