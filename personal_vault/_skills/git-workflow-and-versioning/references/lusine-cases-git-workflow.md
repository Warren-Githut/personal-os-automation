# Git Commit: lusine-cases Skill — Atomic Commits with Detailed Messages

## Session Context
Committed: 2026-06-19 | Session: lusine-cases skill development | Outcome: 30/30 tests passing

---

## Commit History

```bash
41a5c55 feat: add lusine-cases skill with NL case management (update/edit/close-nl)
ec7dd36 docs: add case workflow README + IT quick reference + RULES pointer
c141dc0 feat: add natural-language case management commands (update/edit/close-nl)
7d6589c fix: restore frontmatter_template.md at root for orchestrator tests
64432b8 feat: add natural language brain dump parser and Telegram-style case handler
```

---

## Commit Message Template (Case Management)

### Feature Commit Template
```bash
feat: add lusine-cases skill with NL case management (update/edit/close-nl)

Distributable Hermes skill wrapping L'Usine case management workflow:

Three new modules:
- scripts/lusine-ops/lusine_ops/vault_resolver.py: auto-detect vault (VAULT_ROOT -> known path -> skill-relative)
- scripts/lusine-ops/lusine_ops/cli.py: ops-cases entrypoint with 9 commands
- scripts/lusine-ops/lusine_ops/commands/: 9 thin wrappers delegating to vault/scripts/

Battle-tested: 30/30 tests passing
- 8/8 orchestrator (5 flexible + 3 A/B)
- 8/8 NL parser/handler (5 flexible + 3 A/B)  
- 7/7 vault_resolver (auto-detect, env override, errors)
- 6/6 smoke (3 profiles × 2 tests)

Code simplifications applied (per code-simplification skill):
- Parser: shared _match_keywords helper, simplified title extraction
- Handler: removed WORKSPACE_ROOT alias, unused imports, now_time_str, simplified build_case_body_from_payload
- CLI: removed dead code, hoisted yaml import, simplified list_cases logic

CHANGES MADE:
- scripts/lusine-ops/: new skill package (22 files)
- scripts/tests/test_nl_parser_handler.py: battle test suite (16 tests)

THINGS I DIDN'T TOUCH (intentionally):
- case_followup_orchestrator.py: core logic unchanged, behavior preserved
- existing _cases/ active/closed files: no data migration

POTENTIAL CONCERNS:
- close_case_with_review file move timing: closed file shows old content (investigate on next close)
- fuzzy match threshold (0.35) may need tuning with more cases
- sys.path.insert repeated in each command wrapper (could centralize in commands/__init__.py)
```

### Test Commit Template
```bash
test: add battle test suite for NL case parser/handler (16 tests)

5 flexible scenarios + 3 A/B tests covering:
- prefix parsing, dated blocks, newest-on-top injection
- free-form + structured body building
- thread append vs in-place edit behavior
- close auto lesson learned/insight vs success criteria
- fuzzy matching (token overlap on slug + title)

All 16 tests passing. Runs in isolation with temp vault.
```

### Fix Commit Template
```bash
fix: restore frontmatter_template.md at root for orchestrator tests

Orchestrator expects template at vault/_cases/frontmatter_template.md.
Migration moved it to _cases/active/frontmatter_template.md causing test failures.
Restored to root location.
```

### Docs Commit Template
```bash
docs: add case workflow README + IT quick reference + RULES pointer

- _cases/README.md: Full technical documentation for case management workflow
  - System architecture, file format, NL commands, CLI, Hermes protocol
  - Directory structure, battle tests, integration points
  - Hermes reads this before any case operation

- scripts/QUICK_REFERENCE.md: One-page cheat sheet for IT/on-call
  - Commands, Telegram format, file locations, frontmatter, sections
  - Common fixes, test commands, key files

- RULES.md: Added _cases/README.md to mandatory pointer map
```

---

## Key Patterns from This Session

### 1. Atomic Commits with Clear Types
```bash
feat: <what was added>
fix: <what was fixed>
refactor: <what was simplified>
test: <what was tested>
docs: <what was documented>
chore: <tooling/config changes>
```

### 2. Body Structure
```bash
<type>: <short description>

<what was added/changed>
- bullet list of capabilities

<battle-tested>: <test count> <category> tests passing (<total> total)
- <flexible scenarios covered>
- <a/b distinctions covered>

<code simplifications applied>:
- <module>: <specific simplifications>

CHANGES MADE:
- <file>: <what changed>

THINGS I DIDN'T TOUCH (intentionally):
- <file>: <why>

POTENTIAL CONCERNS:
- <issue>: <mitigation>
```

### 3. Pre-Commit Checks (Applied)
```bash
# 1. Check what you're about to commit
git diff --staged

# 2. Ensure no secrets
git diff --staged | grep -i "password\|secret\|api_key\|token"

# 3. Run tests
python3 scripts/tests/test_case_orchestrator.py
python3 scripts/tests/test_nl_parser_handler.py
cd scripts/lusine-ops && PYTHONPATH=. python3 -m pytest tests/

# 4. Run linting (if configured)
# 5. Run type checking (if configured)
```

---

## Lessons Learned

### 1. Silent Failure Pattern
**Problem:** CLI wrapper called orchestrator which tried to import `push_gcal` **before** file creation. Missing dependency → orchestrator crashed → file never created → silent failure (no file, no clear error to user).

**Pattern:** Wrapper → Orchestrator → External dependency check → **File write**. If dependency check fails early, file never written but user sees no clear error.

**Fix:** Make external deps optional with graceful degradation, or document required flags (`--no-calendar`).

### 2. Skill Naming Conflicts
**Problem:** `lusine-ops` already existed as a different skill (COL/CPH analysis). Our skill renamed to `lusine-cases`.

**Rule:** Check `hermes skills list --profile <name>` before naming new skills.

### 3. Obsidian Sync Delay
**Problem:** Files created via CLI exist in filesystem but Obsidian file watcher hasn't picked them up.

**Fix:** Press `Ctrl+R` (Windows/Linux) or `Cmd+R` (Mac) to force reload, or restart Obsidian.

### 4. Cross-Profile Skill Architecture
**Pattern:** Vault → Skill (runtime import)
- Single source of truth in `vault/scripts/`
- Skill adds vault/scripts to `sys.path` at runtime
- No sync scripts needed; edits propagate instantly
- Auto-detect + `VAULT_ROOT` env var override

---

## Commit Message Format Reference (L'Usine Ops)

```bash
<type>: <short description>

<what was added/changed>
- bullet list of capabilities

<battle-tested>: <test count> <category> tests passing (<total> total)
- <flexible scenarios covered>
- <a/b distinctions covered>

<code simplifications applied>:
- <module>: <specific simplifications>

CHANGES MADE:
- <file>: <what changed>

THINGS I DIDN'T TOUCH (intentionally):
- <file>: <why>

POTENTIAL CONCERNS:
- <issue>: <mitigation>
```

**Types:**
- `feat` — New feature (NL case commands, parser, handler)
- `fix` — Bug fix (prefix parsing, body builder, close file move)
- `refactor` — Code change that neither fixes a bug nor adds a feature (simplifications)
- `test` — Adding or updating tests (battle test suite)
- `docs` — Documentation only
- `chore` — Tooling, dependencies, config