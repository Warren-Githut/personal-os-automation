# Lusine Cases Skill Implementation Plan

## Session Context
Created: 2026-06-19 | Session: lusine-cases skill development | Outcome: 30/30 tests passing

---

## Implementation Plan: lusine-ops Hermes Skill

### Overview
Create a distributable Hermes skill (`lusine-ops`) that wraps the L'Usine case management workflow (in `vault/scripts/`) so it can be installed in any profile via `hermes skill install`. The skill is a thin wrapper that imports implementation from the shared vault at runtime.

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| **Vault → Skill (runtime import)** | Single source of truth in `vault/scripts/`; no sync needed; edits propagate instantly |
| **Auto-detect + VAULT_ROOT override** | Zero-config for you; explicit override for CI |
| **Local install + `install_all_profiles.sh`** | No registry, runs once, installs to all 3 profiles |
| **Thin wrapper skill** | Skill package only has vault resolver, CLI entrypoint, command dispatch; all logic in vault |

---

## Task List

### Phase 1: Foundation (Skill Skeleton + Vault Resolver)

- [x] **Task 1.1: Create skill package structure**
  - **Description:** Create `lusine-ops/` directory with Python package structure, `SKILL.md` manifest, `pyproject.toml`
  - **Acceptance criteria:**
    - [x] Directory structure matches spec
    - [x] `SKILL.md` has correct name, version, entrypoint
    - [x] `pyproject.toml` has package metadata
  - **Verification:**
    - [x] `hermes skill validate .` passes
  - **Dependencies:** None
  - **Files:**
    - `lusine-ops/SKILL.md`
    - `lusine-ops/pyproject.toml`
    - `lusine-ops/lusine_ops/__init__.py`
    - `lusine-ops/lusine_ops/vault_resolver.py`
  - **Scope:** S (2-3 files)

- [x] **Task 1.2: Implement vault resolver with auto-detect + override**
  - **Description:** Implement `lusine_ops.vault_resolver.get_vault_root()` with priority: env var → known path → skill-relative fallback
  - **Acceptance criteria:**
    - [x] Returns correct Path when `VAULT_ROOT` set
    - [x] Auto-detects `/c/Users/khoans/Documents/Warren_OS_Local/vault`
    - [x] Raises clear error when not found
  - **Verification:**
    - [x] Unit tests pass: `pytest lusine-ops/tests/test_vault_resolver.py`
  - **Dependencies:** Task 1.1
  - **Files:**
    - `lusine-ops/lusine_ops/vault_resolver.py`
    - `lusine-ops/tests/test_vault_resolver.py`
  - **Scope:** S (2 files)

- [x] **Task 1.3: Create CLI entrypoint (`ops-cases`)**
  - **Description:** Create `lusine_ops/cli.py` that adds vault to sys.path and delegates to vault's `ops_cases_cli.main()`
  - **Acceptance criteria:**
    - [x] `ops-cases --help` shows 9 commands after install
    - [x] Dry-run commands work without vault (graceful error if vault missing)
  - **Verification:**
    - [x] `python -m lusine_ops.cli --help` works
  - **Dependencies:** Task 1.1, 1.2
  - **Files:**
    - `lusine-ops/lusine_ops/cli.py`
  - **Scope:** XS (1 file)

### Checkpoint: Foundation
- [x] All tests pass: `pytest lusine-ops/tests/`
- [x] `hermes skill validate .` passes
- [x] Manual: `python -m lusine_ops.cli --help` works

---

### Phase 2: Command Wrappers (Thin Dispatchers)

- [x] **Task 2.1: Create command wrapper modules**
  - **Description:** Create `lusine_ops/commands/` with thin wrappers for all 9 commands that import from vault scripts at runtime
  - **Acceptance criteria:**
    - [x] Each wrapper imports vault module and calls its main function
    - [x] Wrappers handle `--dry-run` and vault-not-found gracefully
    - [x] All 9 commands: `list`, `detail`, `new`, `close`, `followup`, `migrate`, `update`, `edit`, `close-nl`
  - **Verification:**
    - [x] Import test: `python -c "from lusine_ops.commands import list, detail, new, close, followup, migrate, update_nl, edit_nl, close_nl"`
  - **Dependencies:** Task 1.2, 1.3
  - **Files:**
    - `lusine-ops/lusine_ops/commands/__init__.py`
    - `lusine-ops/lusine_ops/commands/list.py`
    - `lusine-ops/lusine_ops/commands/detail.py`
    - `lusine-ops/lusine_ops/commands/new.py`
    - `lusine-ops/lusine_ops/commands/close.py`
    - `lusine-ops/lusine_ops/commands/followup.py`
    - `lusine-ops/lusine_ops/commands/migrate.py`
    - `lusine-ops/lusine_ops/commands/update_nl.py`
    - `lusine-ops/lusine_ops/commands/edit_nl.py`
    - `lusine-ops/lusine_ops/commands/close_nl.py`
  - **Scope:** M (10 files, but repetitive pattern)

- [x] **Task 2.2: Wire CLI to command wrappers**
  - **Description:** Update `lusine_ops/cli.py` to use command wrappers instead of calling vault directly
  - **Acceptance criteria:**
    - [x] All 9 subcommands work via `ops-cases <cmd>`
    - [x] Help text matches original CLI
  - **Verification:**
    - [x] `ops-cases --help` shows all 9 commands
    - [x] Each subcommand `--help` works
  - **Dependencies:** Task 2.1
  - **Files:**
    - `lusine-ops/lusine_ops/cli.py`
  - **Scope:** XS (1 file)

### Checkpoint: Core Commands
- [x] `ops-cases --help` shows 9 commands
- [x] `ops-cases list --help`, `update --help`, etc. all work
- [x] Unit tests for command imports pass

---

### Phase 3: Install Script + Multi-Profile Support

- [x] **Task 3.1: Create `install_all_profiles.sh`**
  - **Description:** Bash script that installs skill to all 3 profiles and runs smoke test
  - **Acceptance criteria:**
    - [x] Installs to `warren-profile`, `lusine-profile`, `personal_profile`
    - [x] Runs `ops-cases --help` in each profile to verify
    - [x] Exits non-zero on any failure
  - **Verification:**
    - [x] Run script and verify all 3 profiles have `lusine-ops` skill
  - **Dependencies:** Phase 1-2 complete
  - **Files:**
    - `lusine-ops/install_all_profiles.sh`
  - **Scope:** XS (1 file)

- [x] **Task 3.2: Test install in all 3 profiles**
  - **Description:** Run install script, verify `ops-cases` works in each profile context
  - **Acceptance criteria:**
    - [x] `hermes skill list --profile warren-profile` shows `lusine-cases`
    - [x] `hermes skill list --profile lusine-profile` shows `lusine-cases`
    - [x] `hermes skill list --profile personal_profile` shows `lusine-cases`
    - [x] `ops-cases --help` works in each profile
  - **Verification:**
    - [x] Manual check in each profile
  - **Dependencies:** Task 3.1
  - **Files:** None (verification only)
  - **Scope:** XS (verification)

### Checkpoint: Multi-Profile Install
- [x] All 3 profiles have skill installed
- [x] `ops-cases --help` works in each profile
- [x] No profile-specific configuration needed

---

### Phase 4: Smoke Tests + CI Integration

- [x] **Task 4.1: Create post-install smoke tests**
  - **Description:** `lusine-ops/tests/test_smoke.py` that verifies installed skill works end-to-end
  - **Acceptance criteria:**
    - [x] Tests `ops-cases --help` parses
    - [x] Tests dry-run of each NL command doesn't crash
    - [x] Tests vault resolver finds vault
  - **Verification:**
    - [x] `pytest lusine-ops/tests/test_smoke.py` passes
  - **Dependencies:** Phase 1-3
  - **Files:**
    - `lusine-ops/tests/test_smoke.py`
  - **Scope:** S (1 file)

- [x] **Task 4.2: Verify existing 16 tests still pass**
  - **Description:** Run full test suite (8 orchestrator + 8 NL) to ensure no regression
  - **Acceptance criteria:**
    - [x] `python3 vault/scripts/tests/test_case_orchestrator.py` → 8/8
    - [x] `python3 vault/scripts/tests/test_nl_parser_handler.py` → 8/8
  - **Verification:**
    - [x] Both test suites pass
  - **Dependencies:** None (independent)
  - **Files:** None (verification)
  - **Scope:** XS (verification)

### Checkpoint: Complete
- [x] All 16 existing tests pass
- [x] New smoke tests pass
- [x] Skill installs in all 3 profiles
- [x] `ops-cases` works end-to-end in each profile

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Vault path detection fails on different machine | High | Clear error message with setup instructions; env var override |
| Hermes skill API changes | Medium | Pin compatible Hermes version in `pyproject.toml`; test on upgrade |
| NL prefix syntax changes | Medium | Keep prefix parsing in vault (single source); skill only wraps |
| Profile config differences | Low | No profile-specific code; all config via vault |

---

## Open Questions (Resolved)

| Question | Decision |
|----------|----------|
| Vault discovery | Auto-detect + `VAULT_ROOT` override |
| Distribution | Local install + `install_all_profiles.sh` |
| Sync direction | Vault → Skill (runtime import) |

---

## Verification Before Implementation

- [x] Human reviewed and approved this plan
- [x] All tasks have acceptance criteria
- [x] All tasks have verification steps
- [x] No task >5 files (M tasks are repetitive pattern)
- [x] Checkpoints after each phase
- [x] Dependencies ordered correctly

**Ready to implement?** (Yes → proceed to Task 1.1)