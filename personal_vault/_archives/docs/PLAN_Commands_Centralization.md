# Implementation Plan: Hermes Commands Centralization

## Overview
Migrate 60 command files from 2 legacy `.kilo/command` folders to canonical `~/.hermes/profiles/personal_profile/commands/{shared,lusine}/`, update 2 hub skills, verify, then delete legacy folders.

## Architecture Decisions
- **No personal/ folder** — per user decision
- **Duplicate resolution** — per agreed mapping table
- **DUAL_VAULT_PAIRS.md reference** — remove from adopt.md (file doesn't exist)
- **Skill version bump** — 1.0 → 1.1 in both hub SKILL.md

## Task List

### Phase 1: Foundation & Test Infrastructure
- [ ] **Task 1:** Create test script to validate command file structure (frontmatter + required sections)
- [ ] **Task 2:** Create canonical directory structure `~/.hermes/profiles/personal_profile/commands/{shared,lusine}/`

### Phase 2: Migration - Shared Commands (5 files)
- [ ] **Task 3:** Migrate 5 shared commands from `personal_vault/.kilo/command/` → `commands/shared/`
- [ ] **Task 4:** Verify shared commands pass structure test + update adopt.md (remove DUAL_VAULT_PAIRS.md ref)

### Phase 3: Migration - Lusine Commands (24 files)
- [ ] **Task 5:** Migrate 24 lusine commands from `Personal_OS/.kilo/command/` → `commands/lusine/`
- [ ] **Task 6:** Verify lusine commands pass structure test

### Phase 4: Skill Updates
- [ ] **Task 7:** Update `personal-commands` skill: add shared commands reference, bump version to 1.1
- [ ] **Task 8:** Update `lusine-ops` skill: add lusine commands reference, bump version to 1.1

### Phase 5: Functional Verification
- [ ] **Task 9:** Test `/skill personal-commands` → `/restate "test"` works (reads from shared/)
- [ ] **Task 10:** Test `/skill lusine-ops` → `/ops-compare revenue w22` works (reads from lusine/)

### Phase 6: Cleanup
- [ ] **Task 11:** Verify no legacy refs in skills: `grep -r "\.kilo/command" ~/.hermes/profiles/personal_profile/skills/`
- [ ] **Task 12:** Delete legacy folders `personal_vault/.kilo/command/` and `Personal_OS/.kilo/command/`
- [ ] **Task 13:** Git commit with descriptive message

## Checkpoints

### Checkpoint 1: After Task 4 (Shared done)
- [ ] 5 files in `commands/shared/` pass structure test
- [ ] adopt.md no longer references DUAL_VAULT_PAIRS.md
- [ ] Skills not yet updated (expected)

### Checkpoint 2: After Task 6 (Lusine done)
- [ ] 24 files in `commands/lusine/` pass structure test
- [ ] All 29 command files present and valid

### Checkpoint 3: After Task 10 (Skills functional)
- [ ] Both hub skills route to canonical commands
- [ ] Commands execute correctly

### Checkpoint 4: After Task 13 (Complete)
- [ ] Legacy folders deleted
- [ ] Git history clean
- [ ] All acceptance criteria met

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Skill update breaks routing | High | Test each skill immediately after update |
| Missing command file | Medium | Structure test validates all 29 files |
| Legacy refs remain | Low | Grep verification before delete |

## File Count Summary
- **Source:** 36 (personal_vault) + 24 (Personal_OS) = 60 files
- **Target:** 5 shared + 24 lusine = 29 files (deduped)
- **Personal-only (31 files):** NOT migrated — stay in sub-skills