# Code Review Session 2026-06-18 — Case Brain NL Parser/Handler/CLI

## Context
Reviewed 3 new modules (~800 lines total) implementing natural-language case management for L'Usine ops. All 16 tests passing (8 orchestrator + 8 NL).

## Five-Axis Review Results

### 1. Correctness ✅
| Check | Result |
|-------|--------|
| Matches spec | ✅ 4 prefixes, newest-on-top, lesson learned on close |
| Edge cases | ✅ Empty payload, malformed frontmatter, fuzzy threshold |
| Error paths | ✅ SystemExit on missing case, graceful fallback |
| Tests | ✅ 16/16 passing, behavior-focused not implementation |

### 2. Readability ⚠️ Nits Fixed
| Issue | File | Severity | Fix Applied |
|-------|--------|----------|-------------|
| Unused `Iterable` import | nl_parser.py | Nit | Removed |
| Duplicate `follow_up`/`followup_date` keywords | nl_parser.py | Nit | Consolidated |
| Unused `NO_CALENDAR_FLAG`, `WORKSPACE_ROOT` | nl_handler.py | Nit | Removed |
| Dead `pass` blocks in if/else | ops_cases_cli.py | Nit | Removed |
| `import sys` inside function | ops_cases_cli.py | Nit | Moved to top |

### 3. Architecture ✅
- **Clean module boundaries**: Parser (pure text→data) → Handler (business logic + I/O) → CLI (thin wrapper)
- **No circular deps**: Parser imported by Handler, both by CLI
- **Single responsibility**: Each function does one thing
- **Consistent patterns**: Follows orchestrator conventions (YAML frontmatter, `run_orchestrator`)

### 4. Security ✅
- No secrets, no shell injection (pathlib), no SQL, no exec

### 5. Performance ✅
- Fuzzy matching O(n) over cases (<100 files)
- No N+1, no unbounded loops, no hot-path allocations

## Categorized Findings

| Prefix | Meaning | Count |
|--------|---------|-------|
| *(no prefix)* | Required fix | 0 |
| **Critical** | Blocks merge | 0 |
| **Nit** | Minor, optional | 5 |
| **Optional** | Suggestion | 0 |
| **FYI** | Informational | 2 |

## Architecture Strength
**Module separation pattern** (Parser/Handler/CLI) is a model for future features:
- Parser: Pure functions, easily unit-testable, no I/O
- Handler: Single stateful operations, frontmatter + body manipulation
- CLI: Thin argparse wrapper, Telegram callback placeholder

## Verdict: **Approve with Nits**

All nits fixed before merge. Core behavior verified by 16 passing tests.

## Review Commands Used
```bash
# Syntax check
python3 -m py_compile scripts/case_brain_nl_parser.py scripts/case_brain_nl_handler.py scripts/ops_cases_cli.py

# Test suites (both must pass)
python3 scripts/tests/test_case_orchestrator.py
python3 scripts/tests/test_nl_parser_handler.py
```

## Lesson for Future Reviews
> **Separate parser/handler/CLI from start** — makes review tractable. A single 800-line file would have been harder to review axis-by-axis. The module boundaries force clean separation of concerns.