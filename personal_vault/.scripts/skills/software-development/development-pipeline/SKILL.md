---
name: development-pipeline
description: "Warren's full development methodology: spec-driven-development → plan → incremental-implementation → battle-test → AB-test → code-simplification → 5-axis code-review → debugging-and-error-recovery → verification (Definition of Done). Apply to EVERY non-trivial build."
version: 1.0
tags: [methodology, pipeline, quality-gates, warren]
---

# Development Pipeline — Methodology Stack

> Apply this full stack to every non-trivial build. Do NOT skip phases.
> For trivial changes (1 file, <10 lines, no logic change), use judgment to trim.

## Phase 1: Spec-Driven Development
Before any code:
1. **Surface assumptions** — list what you're assuming about the task
2. **Write spec** — cover 6 areas:
   - **Objective** — what, why, success looks like
   - **Commands** — exact build/test/lint commands
   - **Project Structure** — directory layout with descriptions
   - **Code Style** — example snippet + conventions
   - **Testing Strategy** — framework, coverage, levels
   - **Boundaries** — Always / Ask first / Never
3. **Get Warren approval** before proceeding to Phase 2

## Phase 2: Planning & Task Breakdown
1. Map dependency graph (what depends on what)
2. Slice vertically (one complete feature path at a time)
3. Each task: acceptance criteria + verification step
4. Task size: S (1-2 files) or M (3-5 files). Never L or XL
5. Add checkpoints after every 2-3 tasks
6. Save plan to `.hermes/plans/`

## Phase 3: Incremental Implementation
Each slice:
1. **Implement** smallest complete piece
2. **Test** — run test suite or write tests
3. **Verify** — build, lint, manual check
4. **Commit** — descriptive message
5. Move to next slice (carry forward, don't restart)

## Phase 4: Battle Test
Before declaring any slice done:
- 10+ edge cases covering: invalid input, missing fields, network failure, corrupt state, duplicate data, timeout, unicode, extreme lengths, empty/null, concurrent access
- ALL must pass before moving on
- Log results per phase

## Phase 5: A/B Test (when parallel path exists)
- Run old + new paths on identical input
- Compare output: same format, same quality
- Only source label should differ

## Phase 5.5: Refinement → Deploy QA Pipeline (Warren default)

When Warren asks for improvement/verification/QA after a fix, use this exact checkpoint sequence:
1. **improve-codebase-architecture** — refactor to cleaner structure without changing behavior.
2. **verify parser output** — run `verify-parser-output` gate; no parser result is trusted without a fresh independent recompute + cross-assert report.
3. **AB-test** — compare old vs new on identical input; exact-match required for format/quality.
4. **debugging-and-error-recovery** — if AB-test fails, stop-the-line, reproduce, localize, fix root cause, guard with regression test.
5. **speckit-converge** — align spec, implementation, tests, and docs; eliminate drift.
6. **QA** — edge cases + error paths; ensure no dead code or debug output remains.

If Warren says "approved commit push": list changes, get approval, commit only the reviewed files, then push.

### Embedded QA rules from live sessions
- **Line-by-line compute:** show each arithmetic transform, not only the final value. Example: payment delta = new amount - old amount = 25 - 20 = 5.
- **Honest failure reporting:** if verification cannot run because of environment/setup state, report the blocker and prefer an alternative method or ask; never substitute fabricated output.

## Phase 6: Code Simplification (pre-review)
Apply 5 principles to EVERY new/modified file:
1. **Preserve behavior exactly** — tests pass unchanged
2. **Follow project conventions** — match existing script style
3. **Clarity over cleverness** — no nested comprehension, no reduce
4. **Maintain balance** — extract helpers at 50+ lines
5. **Scope to change** — only touch task-required files

## Phase 7: 5-Axis Code Review
1. **Correctness** — edge cases + error paths handled
2. **Readability** — naming reveals intent, if/else flow straight
3. **Architecture** — imports helpers vs duplicating, clean state machine
4. **Security** — secrets never logged, input validated at boundary
5. **Performance** — no unbounded loops, no N+1

## Phase 8: Debugging & Error Recovery (Stop-the-Line)
When something breaks:
1. **STOP** adding features
2. **PRESERVE** evidence (error, state files, logs)
3. **REPRODUCE** — minimal case
4. **LOCALIZE** which layer
5. **REDUCE** to minimal reproduction
6. **FIX** root cause (not symptom)
7. **GUARD** with regression test
8. **RESUME** only after verification passes

## Phase 9: Verification (Definition of Done)
Every task clears:
- [ ] Acceptance criteria met
- [ ] All existing tests still pass
- [ ] New behavior covered by tests
- [ ] Edge cases + error paths handled
- [ ] No dead code, debug output, commented-out blocks
- [ ] Changes scoped to task only
- [ ] Code follows project conventions
- [ ] Build/compile passes
- [ ] Security implications reviewed
- [ ] Warren reviewed + approved before deploy
