# Spec-Driven Development: Telegram Bot Feature

## Process Followed

### Phase 1: Specify (Interview → Spec)
```
Phase 1: Interview-Me → Interview were key requirements:
- "I want to add real Telegram integration"
- "Zero friction for Warren"
- "Works across 3 profiles"
- "Non-IT user friendly"

Phase 2: Spec Document (lusine-ops-spec.md)
- 6 core areas: Objective, Tech Stack, Commands, Project Structure, Code Style, Testing, Boundaries
- Success criteria: 8/8 orchestrator + 8/8 NL tests + 3 profiles smoking
- Boundaries: Always/Vault→Skill runtime import, Ask first/Adding deps, Never/Hardcode paths
```

### Phase 2: Plan (Decompose)
```
Task breakdown:
1. Foundation: Skill package + vault_resolver + CLI entrypoint
2. Commands: 9 thin wrappers (6 original + 3 NL)  
3. Install: Script for 3 profiles + NSSM service
4. Tests: Smoke + regression (16 existing + new)
```

### Phase 3: Tasks (Vertical Slices)
Each task = One complete vertical slice with:
- Acceptance criteria
- Verification step
- Dependencies mapped

### Phase 4: Implement
```
TDD cycle per task:
RED   → Write failing test
GREEN → Minimal code to pass
REFACTOR → Clean up (code-simplification skill)
```

## Key Spec Decisions

| Decision | Rationale |
|----------|-----------|
| Vault→Skill (runtime import) | Single source of truth in vault/scripts/ |
| Auto-detect VAULT_ROOT | Zero-config for Warren, overrideable for CI |
| Thin wrapper skill | ~100 lines wrapper, ~1000 lines in vault |
| `--no-calendar` default True | Zero-friction for non-IT user |
| Webhook vs Polling | Polling simpler, no HTTPS cert needed |

## Spec Validation Checklist

Before implementation:
- [ ] Spec covers all 6 core areas
- [ ] Human reviewed and approved spec
- [ ] Success criteria specific & testable
- [ ] Boundaries (Always/Ask First/Never) defined

## Lessons Learned

| What Worked | What Didn't |
|-------------|-------------|
| Spec first = fewer reworks | Initial NSSM script failed on PATH |
| Polish spec → fewer bugs | Initial NL phrase "fix parser" vs "add _slugify" |
| Tests first = confidence | Initial NL test didn't cover Vietnamese chars |

## Template for Future Features

```
# Spec: [Feature Name]

## Objective
[What & why, user stories, success criteria]

## Tech Stack
[Framework, language, key deps with versions]

## Commands
[Build, test, lint, dev - full commands]

## Project Structure
[Directory layout with descriptions]

## Code Style
[Example snippet + key conventions]

## Testing Strategy
[Framework, test locations, coverage, test levels]

## Boundaries
- Always: [...]
- Ask first: [...]
- Never: [...]

## Success Criteria
[Specific, testable conditions]

## Open Questions
[Anything unresolved]
```

## Verification
Before implementation:
- [ ] Spec covers all 6 areas
- [ ] Human approved spec
- [ ] Success criteria measurable
- [ ] Boundaries defined
- [ ] Spec saved in repo