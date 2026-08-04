# Lusine Cases Skill Spec — Cross-Profile Hermes Skill

## Session Context
Created: 2026-06-19 | Session: lusine-cases skill development | Outcome: 30/30 tests passing

---

## Spec: lusine-cases Hermes Skill

### Objective
Create a distributable Hermes skill (`lusine-cases`) that wraps the L'Usine case management workflow (NL parser, handler, CLI, orchestrator) so it can be installed in any Hermes profile via `hermes skill install lusine-cases`. All profiles share a single vault at `VAULT_ROOT` for cases, scripts, and docs.

**User stories:**
- As Warren (Ops), I want `ops-cases update "container cost" "..."` to work from warren-profile
- As L'Usine team member, I want the same commands from lusine-profile  
- As personal user, I want to use the workflow for personal cases from personal_profile
- As maintainer, I want to edit code in ONE place (`vault/scripts/`) and have all profiles pick up changes automatically

**Acceptance criteria:**
- `hermes skill install lusine-cases` succeeds in any profile
- `ops-cases --help` shows 9 commands (6 original + 3 NL) after install
- NL prefixes `[update case ...]`, `[edit case ...]`, `[close case ...]` work from any profile
- Vault path discovered via `VAULT_ROOT` env var (fallback: auto-detect from skill location)
- No profile-specific code in skill; all implementation in shared vault

---

## Tech Stack
- **Language:** Python 3.11+ (Hermes subprocess execution)
- **Skill format:** Hermes skill spec (YAML frontmatter + Python entrypoint)
- **Dependencies:** stdlib only (no external deps for parser/handler)
- **Distribution:** Local skill package (installable via `hermes skill install`)

---

## Commands

### Build
```bash
# From vault/scripts - validate syntax
python3 -m py_compile case_brain_nl_parser.py case_brain_nl_handler.py ops_cases_cli.py

# From skill package - validate skill manifest
hermes skill validate .

# Install into a profile
hermes skill install ./lusine-ops --profile warren-profile
hermes skill install ./lusine-ops --profile lusine-profile
hermes skill install ./lusine-ops --profile personal_profile
```

### Test
```bash
# Core tests (must pass 16/16)
python3 scripts/tests/test_case_orchestrator.py
python3 scripts/tests/test_nl_parser_handler.py

# Skill smoke test (after install)
ops-cases --help
ops-cases update "test" "dummy" --dry-run
```

### Run (after install in profile)
```bash
ops-cases list
ops-cases detail <slug>
ops-cases update "fuzzy name" "payload"
ops-cases edit "fuzzy name" "instruction"
ops-cases close-nl "fuzzy name"
```

---

## Project Structure

```
lusine-ops/                           # Skill package root
├── SKILL.md                          # Skill manifest (YAML frontmatter)
├── pyproject.toml                    # Python package metadata
├── install_all_profiles.sh           # Installs to all 3 profiles
├── lusine_ops/                       # Python package
│   ├── __init__.py
│   ├── vault_resolver.py             # VAULT_ROOT discovery logic
│   ├── cli.py                        # Entrypoint: ops-cases
│   └── commands/                     # Command implementations
│       ├── __init__.py
│       ├── list.py
│       ├── detail.py
│       ├── new.py
│       ├── close.py
│       ├── followup.py
│       ├── migrate.py
│       ├── update_nl.py
│       ├── edit_nl.py
│       └── close_nl.py
├── tests/
│   ├── test_smoke.py                 # Post-install smoke tests
│   └── test_vault_resolver.py        # Vault discovery tests
└── vault_sync/                       # Sync scripts (optional)
    └── sync_to_vault.py              # Copy skill modules → vault/scripts/
```

**Shared vault (source of truth):**
```
vault/
├── scripts/
│   ├── case_brain_nl_parser.py       # Parser (shared)
│   ├── case_brain_nl_handler.py      # Handler (shared)
│   ├── case_followup_orchestrator.py # Orchestrator (shared)
│   ├── ops_cases_cli.py              # CLI wrapper (shared)
│   └── tests/
│       ├── test_case_orchestrator.py
│       └── test_nl_parser_handler.py
├── _cases/README.md                  # Workflow docs
└── ...
```

---

## Code Style

### Python conventions
```python
# Type hints on all public functions
def find_case_by_query(query: str) -> Path | None: ...

# Docstrings on public classes/functions
def detect_prefix(text: str) -> tuple[str, str, str]:
    """Parse [new/update/edit/close case] prefix.
    
    Returns (prefix, query, payload) tuple.
    """
    ...

# Constants at module level
VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", auto_detect()))

# Stdlib only in shared modules
# External deps only in skill package (requests, etc. if needed)
```

### Naming
- Files: `snake_case.py`
- Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`

---

## Testing Strategy

| Level | Framework | Location | Coverage |
|-------|-----------|----------|----------|
| **Unit** | pytest + stdlib | `skill/tests/` | Vault resolver, CLI parsing |
| **Integration** | pytest | `vault/scripts/tests/` | Parser, handler, orchestrator (existing 16 tests) |
| **Smoke** | pytest | `skill/tests/test_smoke.py` | Post-install: `ops-cases --help`, dry-run works |

**Existing tests (must continue passing):**
- `vault/scripts/tests/test_case_orchestrator.py` — 8/8
- `vault/scripts/tests/test_nl_parser_handler.py` — 8/8

**New tests:**
- Vault resolver: env var, auto-detect, error cases
- CLI smoke: help, dry-run, invalid args
- Skill install verification

---

## Boundaries

| Category | Rules |
|----------|-------|
| **Always** | - Use `VAULT_ROOT` env var for vault path<br>- Stdlib only in `vault/scripts/` modules<br>- Run existing tests before any commit<br>- Keep `vault/scripts/` as single source of truth |
| **Ask first** | - Adding external dependencies to skill package<br>- Changing vault file structure<br>- Modifying NL prefix syntax |
| **Never** | - Hardcode vault paths in skill code<br>- Duplicate parser/handler logic in skill package<br>- Commit secrets or profile-specific config to vault<br>- Break backward compatibility of NL prefixes |

---

## Success Criteria

1. **Skill installs cleanly** in all 3 profiles via `hermes skill install ./lusine-ops --profile <name>`
2. **CLI works** after install: `ops-cases --help` shows 9 commands
3. **NL commands work**: `ops-cases update "x" "y"` / `edit` / `close-nl` with `--dry-run`
4. **Vault discovery**: Works with `VAULT_ROOT` env var + auto-detect fallback
5. **Tests pass**: 16 existing + new smoke tests = 23+ total
6. **Single source**: All implementation in `vault/scripts/`; skill package only wraps/entrypoints

---

## Open Questions (Resolved)

| Question | Decision |
|----------|----------|
| Vault discovery | Auto-detect + `VAULT_ROOT` override |
| Distribution | Local install + `install_all_profiles.sh` |
| Sync direction | Vault → Skill (runtime import) |

---

## Known Issues (Post-Launch)

| Issue | Root Cause | Fix Applied |
|-------|------------|-------------|
| File creation fails via CLI wrapper | `push_gcal` missing → orchestrator crashes before file write | Document `--no-calendar` flag; make calendar import optional in orchestrator |
| Closed file shows old content after move | `shutil.move` happens before final write completes | Investigate on next close; add flush/fsync |
| Fuzzy match threshold (0.35) | May need tuning with more cases | Monitor; document threshold |

---

## Session Artifacts

| Artifact | Path |
|----------|------|
| Spec | `vault/scripts/lusine-ops-spec.md` |
| Plan | `vault/scripts/lusine-ops-plan.md` |
| Skill package | `vault/scripts/lusine-ops/` |
| Tests | `vault/scripts/lusine-ops/tests/` |
| Battle tests (existing) | `vault/scripts/tests/test_case_orchestrator.py`, `test_nl_parser_handler.py` |