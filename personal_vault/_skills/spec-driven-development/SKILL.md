---
name: spec-driven-development
description: Creates specs before coding. Use when starting a new project, feature, or significant change and no specification exists yet. Use when requirements are unclear, ambiguous, or only exist as a vague idea.
---

# Spec-Driven Development

## Overview

Write a structured specification before writing any code. The spec is the shared source of truth between you and the human engineer — it defines what we're building, why, and how we'll know it's done. Code without a spec is guessing.

## When to Use

- Starting a new project or feature
- Requirements are ambiguous or incomplete
- The change touches multiple files or modules
- You're about to make an architectural decision
- The task would take more than 30 minutes to implement

**When NOT to use:** Single-line fixes, typo corrections, or changes where requirements are unambiguous and self-contained.

## The Gated Workflow

Spec-driven development has four phases. Do not advance to the next phase until the current one is validated.

```
SPECIFY → PLAN → TASKS → IMPLEMENT
   │          │        │          │
   ▼          ▼        ▼          ▼
 Human      Human    Human      Human
 reviews    reviews  reviews    reviews
```

### Phase 1: Specify

Start with a high-level vision. Ask the human clarifying questions until requirements are concrete.

**Surface assumptions immediately.** Before writing any spec content, list what you're assuming:

```
ASSUMPTIONS I'M MAKING:
1. This is a web application (not native mobile)
2. Authentication uses session-based cookies (not JWT)
3. The database is PostgreSQL (based on existing Prisma schema)
4. We're targeting modern browsers only (no IE11)
→ Correct me now or I'll proceed with these.
```

Don't silently fill in ambiguous requirements. The spec's entire purpose is to surface misunderstandings *before* code gets written — assumptions are the most dangerous form of misunderstanding.

**Write a spec document covering these six core areas:**

1. **Objective** — What are we building and why? Who is the user? What does success look like?

2. **Commands** — Full executable commands with flags, not just tool names.
   ```
   Build: npm run build
   Test: npm test -- --coverage
   Lint: npm run lint --fix
   Dev: npm run dev
   ```

3. **Project Structure** — Where source code lives, where tests go, where docs belong.
   ```
   src/           → Application source code
   src/components → React components
   src/lib        → Shared utilities
   tests/         → Unit and integration tests
   e2e/           → End-to-end tests
   docs/          → Documentation
   ```

4. **Code Style** — One real code snippet showing your style beats three paragraphs describing it. Include naming conventions, formatting rules, and examples of good output.

5. **Testing Strategy** — What framework, where tests live, coverage expectations, which test levels for which concerns.

6. **Boundaries** — Three-tier system:
   - **Always do:** Run tests before commits, follow naming conventions, validate inputs
   - **Ask first:** Database schema changes, adding dependencies, changing CI config
   - **Never do:** Commit secrets, edit vendor directories, remove failing tests without approval

**Spec template:**

```markdown
# Spec: [Project/Feature Name]

## Objective
[What we're building and why. User stories or acceptance criteria.]

## Tech Stack
[Framework, language, key dependencies with versions]

## Commands
[Build, test, lint, dev — full commands]

## Project Structure
[Directory layout with descriptions]

## Code Style
[Example snippet + key conventions]

## Testing Strategy
[Framework, test locations, coverage requirements, test levels]

## Boundaries
- Always: [...]
- Ask first: [...]
- Never: [...]

## Success Criteria
[How we'll know this is done — specific, testable conditions]

## Open Questions
[Anything unresolved that needs human input]
```

**Reframe instructions as success criteria.** When receiving vague requirements, translate them into concrete conditions:

```
REQUIREMENT: "Make the dashboard faster"

REFRAMED SUCCESS CRITERIA:
- Dashboard LCP < 2.5s on 4G connection
- Initial data load completes in < 500ms
- No layout shift during load (CLS < 0.1)
→ Are these the right targets?
```

This lets you loop, retry, and problem-solve toward a clear goal rather than guessing what "faster" means.

### Phase 2: Plan

With the validated spec, generate a technical implementation plan:

1. Identify the major components and their dependencies
2. Determine the implementation order (what must be built first)
3. Note risks and mitigation strategies
4. Identify what can be built in parallel vs. what must be sequential
5. Define verification checkpoints between phases

The plan should be reviewable: the human should be able to read it and say "yes, that's the right approach" or "no, change X."

### Phase 3: Tasks

Break the plan into discrete, implementable tasks:

- Each task should be completable in a single focused session
- Each task has explicit acceptance criteria
- Each task includes a verification step (test, build, manual check)
- Tasks are ordered by dependency, not by perceived importance
- No task should require changing more than ~5 files

**Task template:**
```markdown
- [ ] Task: [Description]
  - Acceptance: [What must be true when done]
  - Verify: [How to confirm — test command, build, manual check]
  - Files: [Which files will be touched]
```

### Phase 4: Implement

Execute tasks one at a time following `skills/incremental-implementation/SKILL.md` (`incremental-implementation`) and `skills/test-driven-development/SKILL.md` (`test-driven-development`). Use `skills/context-engineering/SKILL.md` (`context-engineering`) to load the right spec sections and source files at each step rather than flooding the agent with the entire spec.

## Keeping the Spec Alive

The spec is a living document, not a one-time artifact:

- **Update when decisions change** — If you discover the data model needs to change, update the spec first, then implement.
- **Update when scope changes** — Features added or cut should be reflected in the spec.
- **Commit the spec** — The spec belongs in version control alongside the code.
- **Reference the spec in PRs** — Link back to the spec section that each PR implements.

## Cross-Profile Skill Spec Pattern (New)

When the deliverable is a **distributable Hermes skill** that wraps shared vault code for multiple profiles, add these sections to the standard spec:

### Skill Distribution Section
```markdown
## Skill Distribution
- **Target profiles:** [warren-profile, lusine-profile, personal_profile]
- **Distribution method:** Local install + `install_all_profiles.sh`
- **Registry:** None (local file install via `hermes skill install`)
- **Versioning:** Semver in `pyproject.toml`
```

### Vault→Skill Runtime Import Section
```markdown
## Sync Strategy: Vault → Skill (Runtime Import)
- **Source of truth:** `vault/scripts/` (single source)
- **Skill wraps:** Thin dispatchers that import at runtime via `sys.path.insert(0, VAULT_ROOT/scripts)`
- **No sync scripts needed** — edits in vault propagate instantly
- **Vault discovery:** Auto-detect + `VAULT_ROOT` env var override
```

### Multi-Profile Install Section
```markdown
## Multi-Profile Install
- **Install script:** `install_all_profiles.sh` (runs `hermes skill install` for each profile)
- **Smoke test:** `ops-cases --help` in each profile post-install
- **No profile-specific code** — all config via vault
```

### Commands Section (Skill-Specific)
```markdown
## Commands
### Build/Validate
```bash
python3 -m py_compile vault/scripts/*.py
hermes skill validate .
```

### Test
```bash
pytest vault/scripts/tests/*.py
pytest skill/tests/test_smoke.py
```

### Install
```bash
./install_all_profiles.sh
```

## Boundaries (Skill-Specific Additions)
- **Always:** Use `VAULT_ROOT` env var for vault path
- **Ask first:** Adding external dependencies to skill package
- **Never:** Hardcode vault paths in skill code, duplicate parser/handler logic in skill package
```

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "This is simple, I don't need a spec" | Simple tasks don't need *long* specs, but they still need acceptance criteria. A two-line spec is fine. |
| "I'll write the spec after I code it" | That's documentation, not specification. The spec's value is in forcing clarity *before* code. |
| "The spec will slow us down" | A 15-minute spec prevents hours of rework. Waterfall in 15 minutes beats debugging in 15 hours. |
| "Requirements will change anyway" | That's why the spec is a living document. An outdated spec is still better than no spec. |
| "The user knows what they want" | Even clear requests have implicit assumptions. The spec surfaces those assumptions. |

## Pitfall: Preserve User Choice Labels Between Clarify and Spec

When you move from a `clarify` question (where the user picked "Option A" from choices you gave) to the spec document, **do not reuse the same labels to refer to different things.**

**Concrete failure from this session:**

```
clarify: A — Google Calendar event | B — Hermes cron | C — Both
user → "tôi chọn option a"  → means Google Calendar

spec:   "Option A (đã chọn): Chỉ fix follow_up field. Không tạo cron/calendar event."
       ↑ LABEL REUSED to mean something different
user → "ok nè" (trusts the framing)
later → "tôi vẫn chưa thấy set calendar" — legitimate correction
```

**Rule:** If you use lettered options in `clarify`, carry those same meanings into the spec. If you must re-label (e.g., because the spec divides work differently), explicitly map them at the top of the spec:

```markdown
## Clarify-to-Spec Mapping
- Option A (user's choice) = [what it's called in the spec: "Calendar Integration"]
- Option B = [deferred to Phase 2]
```

Without this bridge, the user approves the spec thinking it matches their clarify choice, but the spec actually describes something different. The spec passes review only because of trust, not understanding — and that trust erodes when the implementation doesn't match what they asked for.

## Red Flags

- Starting to write code without any written requirements
- Asking "should I just start building?" before clarifying what "done" means
- Implementing features not mentioned in any spec or task list
- Making architectural decisions without documenting them
- Skipping the spec because "it's obvious what to build"

## Pitfall: Trusting config.yaml Infrastructure Without Verification

**Problem:** A config.yaml entry for a proxy, API endpoint, or service exists and looks correct. You write it into the spec as an assumption, the user confirms, and you build the entire feature around it. When you finally test, the endpoint is dead.

**Example from this session:** Config.yaml had `base_url: http://127.0.0.1:8787` for DeepSeek. The spec assumed the proxy worked. It was dead — the "Hermes CLI spawn" approach in the spec had to be scrapped mid-build for direct API calls.

**Fix:** After listing assumptions in the spec, **test the ones that are testable** before finalizing the implementation approach. A 2-second `curl` or `python3` call confirms an endpoint is alive. Add verification as a column in the Architecture section:

```markdown
| Component | Assumption | Verify |
|-----------|-----------|--------|
| DeepSeek API | Proxy at port 8787 routes to DeepSeek | `curl http://127.0.0.1:8787/v1/...` |
```

If verification fails, update the spec before implementation begins.

## Adapting Specs for Non-Code Changes

When the deliverable is a configuration/documentation change (SKILL.md patch, template update, config fix), adapt the spec template:

- Drop: Tech Stack, Commands, Code Style, Testing Strategy
- Add: Files-to-change table, structure/flow diagrams, boundary rules
- See `references/spec-adaptation-for-skill-docs.md` for the adapted format used in stock-ingest Integrity Gate extension

## Verification

Before proceeding to implementation, confirm:

- [ ] The spec covers all six core areas
- [ ] The human has reviewed and approved the spec
- [ ] Success criteria are specific and testable
- [ ] Boundaries (Always/Ask First/Never) are defined
- [ ] The spec is saved to a file in the repository