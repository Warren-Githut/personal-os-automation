# Session: Spec-driven development for SKILL.md documentation patches (not code)

## When the deliverable is a Hermes skill definition (SKILL.md) patch

Standard `spec-driven-development` template assumes software (Commands, Code Style, Testing Strategy). For a SKILL.md-only change, adapt:

## Adapted spec structure (used for stock-ingest Integrity Gate 6→11 checks)

1. **Objective** — What changed and why
2. **Assumptions** — Confirmed via interview-me before spec
3. **Files cần sửa** — File list + priority
4. **Structure** — Tables, pipeline flow, output format, frontmatter changes
5. **Boundaries** — Always / Ask first / Never
6. **Success Criteria** — Checkboxes

## Flow: interview-me → spec → plan → tasks → implement

User (Warren) explicitly sequenced:
1. interview-me to nail threshold numbers
2. spec-driven-development Phase 1 (Specify) — write spec
3. planning-and-task-breakdown — decompose into 2 independent tasks
4. incremental-implementation — patch each file, verify

## Key differences from software spec

| Software spec | Skill-doc spec |
|---------------|----------------|
| Tech Stack section | Not needed |
| Commands (build/test) | Not needed |
| Code Style section | Not needed |
| Testing Strategy | Not needed (verify = YAML integrity) |
| Project Structure | Files-to-change table instead |
| Architecture | Pipeline flow diagram instead |

## Source session

2026-06-24: stock-ingest v3.6→v3.7 Integrity Gate 6→11 checks
- Spec: `stock-ingest/references/integrity-gate-extension-spec.md`
- Plan: `stock-ingest/plans/integrity-gate-extension-plan.md`
