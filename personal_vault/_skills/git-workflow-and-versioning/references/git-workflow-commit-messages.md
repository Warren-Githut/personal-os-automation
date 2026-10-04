# Git Workflow for L'Usine Case Management System

## Commit Message Format

```
<type>: <short description>

<body explaining why, not what>

CHANGES MADE:
- file1: description
- file2: description

THINGS I DIDN'T TOUCH (intentionally):
- file3: reason

POTENTIAL CONCERNS:
- concern1
- concern2
```

## Types

| Type | Meaning |
|------|---------|
| `feat` | New feature |
| `fix` | Bug fix |
| `refactor` | Code change, no behavior change |
| `test` | Adding/updating tests |
| `docs` | Documentation only |
| `chore` | Tooling, deps, config |

## Real Examples from This Project

### Feature Commit
```
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

### Bug Fix Commit
```
fix: make Google Calendar integration optional (push_gcal)

- Orchestrator: try/except import push_gcal, _CALENDAR_AVAILABLE flag
- All calendar functions check _CALENDAR_AVAILABLE before proceeding
- Graceful degradation: case operations work without push_gcal, calendar skipped with warnings
- CLI wrapper: --no-calendar default=True for zero-friction UX
- Works across all 3 profiles (warren, lusine, personal)

CHANGES MADE:
- scripts/case_followup_orchestrator.py: optional import, _CALENDAR_AVAILABLE flag, graceful degradation
- scripts/lusine-ops/lusine_ops/commands/new.py: --no-calendar default=True

TESTS: 30/30 pass
```

### Documentation Commit
```
docs: add case workflow README + IT quick reference + RULES pointer

- _cases/README.md: Full technical documentation for case management workflow
- scripts/QUICK_REFERENCE.md: One-page cheat sheet for IT/on-call
- RULES.md: Added _cases/README.md to mandatory pointer map

Hermes now must read _cases/README.md before any case operation.
```

### Feature with Tests
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

## Commit Best Practices

| Practice | Why |
|----------|-----|
| Atomic commits | Each commit = one logical change |
| Descriptive messages | Future readers understand WHY |
| Atomic + descriptive | Easy to revert, bisect, review |
| Reference tickets | Link to issue/requirement |

## Branch Strategy

```
main (always deployable)
  ├── feature/telegram-bot    (short-lived, < 3 days)
  ├── fix/calendar-optional
  └── fix/slug-vietnamese
```

## Merge Strategy

```bash
# Squash and merge for feature branches
git checkout main
git merge --squash feature/telegram-bot
git commit -m "feat: add Telegram bot integration..."
```

## Pre-Commit Checklist

- [ ] Tests pass (`python -m pytest` or project test command)
- [ ] No secrets in diff (`git diff --staged | grep -i secret`)
- [ ] Message follows format
- [ ] CHANGES MADE section lists key files
- [ ] THINGS I DIDN'T TOUCH listed (shows scope discipline)
- [ ] POTENTIAL CONCERNS documented (risk awareness)

## Version Tagging

```bash
# Semantic versioning
git tag -a v1.2.0 -m "feat: add Telegram bot integration"
git push origin v1.2.0
```

---

## This Project's Git History

```
91095a6 feat: add Telegram bot integration (aiogram)
954fa6c fix: make Google Calendar integration optional (push_gcal)
41a5c55 feat: add lusine-cases skill with NL case management (update/edit/close-nl)
ec7dd36 docs: add case workflow README + IT quick reference + RULES pointer
c141dc0 feat: add natural-language case management commands (update/edit/close-nl)
7d6589c fix: restore frontmatter_template.md at root for orchestrator tests
64432b8 feat: add natural language brain dump parser and Telegram-style case handler
...
```

Each commit is atomic, descriptive, and includes context for future maintainers.