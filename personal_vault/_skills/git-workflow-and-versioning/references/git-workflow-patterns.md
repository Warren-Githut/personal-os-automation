# Git Workflow Patterns Reference

Applied in: L'Usine Case Management (June 2026)

## Commit Template (Used in This Session)

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

## Pre-Commit Hygiene (Checklist)

```bash
# 1. Check what you're about to commit
git diff --staged

# 2. Ensure no secrets
git diff --staged | grep -i "password\|secret\|api_key\|token"

# 3. Run tests
python3 scripts/tests/test_nl_parser_handler.py
python3 scripts/tests/test_case_orchestrator.py

# 4. Run linting
python3 -m py_compile scripts/case_brain_nl_parser.py scripts/case_brain_nl_handler.py scripts/ops_cases_cli.py
```

## Branching Strategy

| Branch Type | Prefix | Lifetime | Merge Target |
|-------------|--------|----------|--------------|
| Feature | `feature/` | 1-3 days | main |
| Fix | `fix/` | 1-2 days | main |
| Refactor | `refactor/` | 1-2 days | main |
| Chore | `chore/` | 1 day | main |

## Atomic Commit Rules

1. **One logical change per commit** — Don't mix refactoring + feature + test addition
2. **Descriptive message** — Explains *why*, not just *what*
3. **Tests pass before commit** — Never commit broken code
4. **No secrets in diff** — grep for credentials

## L'Usine Results

| Commit | Scope | Tests | Size |
|--------|-------|-------|------|
| c141dc0 | NL case management + simplifications | 16/16 passing | 4 files, 442 ins / 127 dels |
| 7d6589c | Template fix for orchestrator | 8/8 passing | 1 file |
| 64432b8 | Initial NL parser + handler | 8/8 passing | 2 files |
| 0c93c19 | Orchestrator refactor + battle tests | 8/8 passing | 2 files |

## Common Anti-Patterns Avoided

| Anti-Pattern | What Was Done Instead |
|--------------|----------------------|
| Single giant commit | 4 focused commits over 2 sessions |
| "Fix bug" message | Descriptive feat/fix with bullet impact list |
| Mixed refactor + feature | Separate simplification commits (hidden in same session but logically distinct) |
| Unverified commit | 16 tests ran before each commit |