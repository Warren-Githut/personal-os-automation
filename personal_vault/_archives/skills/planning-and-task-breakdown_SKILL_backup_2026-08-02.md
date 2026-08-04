---
name: planning-and-task-breakdown
description: Breaks work into ordered tasks. Use when you have a spec or clear requirements and need to break work into implementable tasks. Use when a task feels too large to start, when you need to estimate scope, or when parallel work is possible.
---

# Planning and Task Breakdown

## Overview

Decompose work into small, verifiable tasks with explicit acceptance criteria. Good task breakdown is the difference between an agent that completes work reliably and one that produces a tangled mess. Every task should be small enough to implement, test, and verify in a single focused session.

## When to Use

- You have a spec and need to break it into implementable units
- A task feels too large or vague to start
- Work needs to be parallelized across multiple agents or sessions
- You need to communicate scope to a human
- The implementation order isn't obvious

**When NOT to use:** Single-file changes with obvious scope, or when the spec already contains well-defined tasks.

## The Planning Process

### Step 1: Enter Plan Mode

Before writing any code, operate in read-only mode:

- Read the spec and relevant codebase sections
- Identify existing patterns and conventions
- Map dependencies between components
- Note risks and unknowns

**Do NOT write code during planning.** The output is a plan document, not implementation.

### Step 2: Identify the Dependency Graph

Map what depends on what:

```
Database schema
    │
    ├── API models/types
    │       │
    │       ├── API endpoints
    │       │       │
    │       │       └── Frontend API client
    │       │               │
    │       │               └── UI components
    │       │
    │       └── Validation logic
    │
    └── Seed data / migrations
```

Implementation order follows the dependency graph bottom-up: build foundations first.

### Step 3: Slice Vertically

Instead of building all the database, then all the API, then all the UI — build one complete feature path at a time:

**Bad (horizontal slicing):**
```
Task 1: Build entire database schema
Task 2: Build all API endpoints
Task 3: Build all UI components
Task 4: Connect everything
```

**Good (vertical slicing):**
```
Task 1: User can create an account (schema + API + UI for registration)
Task 2: User can log in (auth schema + API + UI for login)
Task 3: User can create a task (task schema + API + UI for creation)
Task 4: User can view task list (query + API + UI for list view)
```

Each vertical slice delivers working, testable functionality.

### Step 4: Write Tasks

Each task follows this structure:

```markdown
## Task [N]: [Short descriptive title]

**Description:** One paragraph explaining what this task accomplishes.

**Acceptance criteria:**
- [ ] [Specific, testable condition]
- [ ] [Specific, testable condition]

**Verification:**
- [ ] Tests pass: `npm test -- --grep "feature-name"`
- [ ] Build succeeds: `npm run build`
- [ ] Manual check: [description of what to verify]

**Dependencies:** [Task numbers this depends on, or "None"]

**Files likely touched:**
- `src/path/to/file.ts`
- `tests/path/to/test.ts`

**Estimated scope:** [Small: 1-2 files | Medium: 3-5 files | Large: 5+ files]
```

### Step 5: Order and Checkpoint

Arrange tasks so that:

1. Dependencies are satisfied (build foundation first)
2. Each task leaves the system in a working state
3. Verification checkpoints occur after every 2-3 tasks
4. High-risk tasks are early (fail fast)

Add explicit checkpoints:

```markdown
## Checkpoint: After Tasks 1-3
- [ ] All tests pass
- [ ] Application builds without errors
- [ ] Core user flow works end-to-end
- [ ] Review with human before proceeding
```

## Cross-Profile Skill Plan Pattern (New)

When planning a distributable Hermes skill across multiple profiles, use this phased structure:

### Plan Document Template (Skill-Specific)

```markdown
# Implementation Plan: [Skill Name]

## Overview
[One paragraph: skill wraps shared vault code, multi-profile install]

## Architecture Decisions
- **Vault → Skill (runtime import):** Single source in `vault/scripts/`
- **Auto-detect + VAULT_ROOT override:** Zero config for standard setup
- **Local install + install_all_profiles.sh:** Run once, all profiles
- **Thin wrapper skill:** <100 lines total, all logic in vault

## Task List

### Phase 1: Foundation (Skill Skeleton + Vault Resolver)
- [ ] Task 1.1: Create skill package structure (SKILL.md, pyproject.toml)
- [ ] Task 1.2: Implement vault resolver with auto-detect + override
- [ ] Task 1.3: Create CLI entrypoint (ops-cases)

**Checkpoint: Foundation**
- [ ] All tests pass: `pytest skill/tests/`
- [ ] `hermes skill validate .` passes
- [ ] Manual: `python -m skill.cli --help` works

### Phase 2: Command Wrappers (Thin Dispatchers)
- [ ] Task 2.1: Create 9 command wrapper modules (repetitive pattern)
- [ ] Task 2.2: Wire CLI to command wrappers

**Checkpoint: Core Commands**
- [ ] `ops-cases --help` shows all commands
- [ ] Each subcommand `--help` works

### Phase 3: Install Script + Multi-Profile Support
- [ ] Task 3.1: Create `install_all_profiles.sh`
- [ ] Task 3.2: Test install in all 3 profiles

**Checkpoint: Multi-Profile Install**
- [ ] All 3 profiles have skill installed
- [ ] `ops-cases` works in each profile

### Phase 4: Smoke Tests + CI Integration
- [ ] Task 4.1: Create post-install smoke tests
- [ ] Task 4.2: Verify existing 16 tests still pass

**Checkpoint: Complete**
- [ ] All 18+ tests pass
- [ ] Skill installs in all 3 profiles

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Vault path detection fails | High | Clear error + env var override |
| Hermes skill API changes | Medium | Pin version, test on upgrade |

## Task Sizing for Repetitive Wrappers
- Repetitive command wrappers (9 files) = **M** scope (pattern is identical)
- Single-file tasks (resolver, CLI entrypoint) = **XS/S**
- Verification tasks = **XS** (run existing tests)
```

## Task Sizing Guidelines

| Size | Files | Scope | Example |
|------|-------|-------|---------|
| **XS** | 1 | Single function or config change | Add a validation rule |
| **S** | 1-2 | One component or endpoint | Add a new API endpoint |
| **M** | 3-5 | One feature slice | User registration flow |
| **L** | 5-8 | Multi-component feature | Search with filtering and pagination |
| **XL** | 8+ | **Too large — break it down further** | — |

If a task is L or larger, it should be broken into smaller tasks. An agent performs best on S and M tasks.

**When to break a task down further:**
- It would take more than one focused session (roughly 2+ hours of agent work)
- You cannot describe the acceptance criteria in 3 or fewer bullet points
- It touches two or more independent subsystems (e.g., auth and billing)
- You find yourself writing "and" in the task title (a sign it is two tasks)

## Plan Document Template

```markdown
# Implementation Plan: [Feature/Project Name]

## Overview
[One paragraph summary of what we're building]

## Architecture Decisions
- [Key decision 1 and rationale]
- [Key decision 2 and rationale]

## Task List

### Phase 1: Foundation
- [ ] Task 1: ...
- [ ] Task 2: ...

### Checkpoint: Foundation
- [ ] Tests pass, builds clean

### Phase 2: Core Features
- [ ] Task 3: ...
- [ ] Task 4: ...

### Checkpoint: Core Features
- [ ] End-to-end flow works

### Phase 3: Polish
- [ ] Task 5: ...
- [ ] Task 6: ...

### Checkpoint: Complete
- [ ] All acceptance criteria met
- [ ] Ready for review

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| [Risk] | [High/Med/Low] | [Strategy] |

## Open Questions
- [Question needing human input]
```

## Parallelization Opportunities

When multiple agents or sessions are available:

- **Safe to parallelize:** Independent feature slices, tests for already-implemented features, documentation
- **Must be sequential:** Database migrations, shared state changes, dependency chains
- **Needs coordination:** Features that share an API contract (define the contract first, then parallelize)

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "I'll figure it out as I go" | That's how you end up with a tangled mess and rework. 10 minutes of planning saves hours. |
| "The tasks are obvious" | Write them down anyway. Explicit tasks surface hidden dependencies and forgotten edge cases. |
| "Planning is overhead" | Planning is the task. Implementation without a plan is just typing. |
| "I can hold it all in my head" | Context windows are finite. Written plans survive session boundaries and compaction. |

## Red Flags

- Starting implementation without a written task list
- Tasks that say "implement the feature" without acceptance criteria
- No verification steps in the plan
- All tasks are XL-sized
- No checkpoints between tasks
- Dependency order isn't considered

### ⏱️ Micro-Task Time Budget (Yamikishi-inspired)

**Hard rule:** Every task MUST be executable in **2–5 minutes** of agent work. If a task would take longer, it's a plan — not a task — and must be broken down further.

| Task time estimate | Action |
|---|---|
| ≤5 min | ✅ Good — single focused action, easy to verify |
| 5–15 min | ⚠️ Too large — split into 2-3 sub-tasks |
| >15 min | 🔴 Plan, not task — re-decompose from scratch |

**Ops-specific examples:**

| Too big (plan) | Correct (micro-tasks) |
|---|---|
| "Phân tích revenue W29-W32" (~30 min) | (1) Parse raw data (3 min) → (2) Tính KPI per store (3 min) → (3) So sánh WoW (3 min) → (4) Viết kết luận (2 min) |
| "Tạo dashboard mới" (~45 min) | (1) Sketch layout (3 min) → (2) Build data query (4 min) → (3) Render chart (3 min) → (4) Style + deploy (4 min) |
| "Fix parser bể format" (~20 min) | (1) Reproduce bug (2 min) → (2) Identify root cause (3 min) → (3) Patch + test (3 min) → (4) Verify end-to-end (2 min) |

**Why this matters:** Micro-tasks force atomicity. A 2-minute task either succeeds or fails cleanly — no partial state to untangle. Warren can see progress every 2-5 minutes instead of waiting 30 minutes for "done." Each micro-task's output can be independently verified before proceeding.

## Verification

Before starting implementation, confirm:

- [ ] Every task has acceptance criteria
- [ ] Every task has a verification step
- [ ] Every task fits the 2-5 minute budget
- [ ] Task dependencies are identified and ordered correctly
- [ ] No task touches more than ~5 files
- [ ] Checkpoints exist between major phases
- [ ] The human has reviewed and approved the plan

### 🧩 Session Chunking (token budget — quy tắc 150k)

**Tại sao:** LLM code sắc nhất ~150k token context. Quá mức → sinh bug lặp, quên đầu.
**Quy tắc (HARD):** Chia session theo TOKEN, KHÔNG theo số bước.

1. Sau khi bẻ plan N bước → Bố hỏi: *"Plan này chia mấy session cho an toàn 150k?"*
2. Con ước lượng token từng bước, chia chunk (mỗi chunk ≤ ~140k, chừa đệm):
   - 7 bước × ~20k = 140k → **1 session luôn**, ĐỪNG handoff.
   - 7 bước × ~40k = 280k → **2-3 session** (cut ở cuối bước 3, bước 5).
3. Làm tới cuối chunk → `handoff` (ghi: xong bước mấy, state gì, tiếp bước nào).
4. Session sau: Bố gõ *"tiếp tục từ handoff"* → con nạp file, làm tiếp.

🚫 **SAI:** handoff ở bước 2 khi context còn thấp (<80k) = lãng phí 1 vòng nạp lại.
✅ **ĐÚNG:** handoff khi context sắp chạm 150k HOẶC Bố thực sự dừng.