# Commit Message Patterns from L'Usine Session (2026-06-19)

## Feature Commit Template

```markdown
feat: add natural-language case management commands (update/edit/close-nl)

Distributable Hermes skill wrapping L'Usine case management workflow:
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

CHANGES MADE:
- scripts/case_brain_nl_parser.py: shared _match_keywords helper, detect_prefix 3-tuple return
- scripts/case_brain_nl_handler.py: removed WORKSPACE_ROOT, unused imports, simplified build_case_body_from_payload
- scripts/ops_cases_cli.py: 3 new NL commands, dead code removed, yaml import hoisted
- scripts/tests/test_nl_parser_handler.py: battle test suite (16 tests)

THINGS I DIDN'T TOUCH (intentionally):
- case_followup_orchestrator.py: core logic unchanged, behavior preserved
- existing _cases/ active/closed files: no data migration

POTENTIAL CONCERNS:
- close_case_with_review file move timing: closed file shows old content (investigate on next close)
- fuzzy match threshold (0.35) may need tuning with more cases
- sys.path.insert repeated in each command wrapper (could centralize in commands/__init__.py)
```

---

## Test Commit Template

```markdown
test: add battle test suite for NL case parser/handler (16 tests)

5 flexible scenarios + 3 A/B tests covering:
- prefix parsing, dated blocks, newest-on-top injection
- free-form + structured body building
- thread append vs in-place edit behavior
- close auto lesson learned/insight vs success criteria
- fuzzy matching (token overlap on slug + title)

All 16 tests passing. Runs in isolation with temp vault.
```

---

## Fix Commit Template

```markdown
fix: restore frontmatter_template.md at root for orchestrator tests

Orchestrator expects template at _cases/frontmatter_template.md but it was in _cases/active/.
Restored from active/ copy. All 8/8 battle tests now pass.
```

---

## Docs Commit Template

```markdown
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

## Commit Message Format (L'Usine Standard)

```markdown
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
- <file>: <what changed>

THINGS I DIDN'T TOUCH (intentionally):
- <file>: <reason>
- <file>: <reason>

POTENTIAL CONCERNS:
- <issue>: <mitigation/investigation>
- <concern>: <note>
```

---

## Types Used

| Type | Usage |
|------|-------|
| `feat` | New NL commands, new skill |
| `test` | Battle test suites |
| `fix` | Template path, close file move |
| `docs` | README, QUICK_REFERENCE, RULES.md |
| `refactor` | Code simplifications (9 patterns) |

---

## Verification Checklist (Pre-Commit)

- [ ] `git diff --staged` reviewed
- [ ] No secrets in diff
- [ ] All tests pass (run relevant test suites)
- [ ] No formatting-only changes mixed with behavior
- [ ] `.gitignore` covers standard exclusions