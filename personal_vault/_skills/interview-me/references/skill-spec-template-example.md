# Skill Spec Template — Concrete Example from 2026-06-25
> ⚠️ **Pattern update 2026-07-14:** the `vault/_inbox/` step is **removed** (see SKILL.md §Handoff: Skill Creation Spec). Specs are now held **inline in the conversation** or in the skill's `references/` dir — never `_inbox/`. This example reflects the *older* workflow (spec written to `_inbox/`); keep it only as a structural template, not as a process to copy.

> Session: `/ops-review-response` skill spec after 7-round interview with Warren.
> This file is a reference for the pattern documented in SKILL.md §Handoff: Skill Creation Spec.

## What Worked

- **7 Q&A rounds** to reach 100% confidence before writing spec
- **Self-contained spec** at `vault/_inbox/skill-spec-ops-review-response.md` (314 lines, Vietnamese có dấu)
- **13 sections** covering every edge case surfaced during interview:
  1. Purpose
  2. Core Rules (SOP 005 v2.2 — language, banned chars, store naming, signature)
  3. Input Format & Platform Detection (Google/FB/IG/GrabFood with examples)
  4. Store Mapping (name variants → LU3/LU5/LU7)
  5. Operational Matrix (4 paths + Red Flag with sentence counts)
  6. Gold Standard Template (reference, not rigid copy)
  7. Output Format (Part 1 + Part 3 + Part 4, exact markdown)
  8. GSheet Append (sheet name, gid, SA key path, 17 columns, append logic)
  9. SLA Windows
  10. Workflow Diagram (ASCII)
  11. Constraints & Out of Scope
  12. Full Worked Example (input → complete output)
  13. Fresh Session Instructions

## What Required Extra Rounds

- **Platform scope creep**: Original spec was Google-only → expanded to FB/IG/GrabFood in Q7
- **Part 2 removal**: Menu Recommendation was in SOP → Warren removed it in Q3
- **Red Flag behavior**: Initially guessed "block + no draft" → corrected to "block + draft + 5 clarify questions" in Q6
- **GSheet verification**: Warren asked me to actually check the sheet structure before confirming (between Q5-Q6)

## Key Pattern: Don't Create Skill in Interview Session

Warren explicitly said "qua bên chat session khác để hermes viết skill qua command learn." The handoff pattern is:
1. Interview reaches 100%
2. Hold spec inline in the conversation (or paste into the skill's `references/` dir) — **inbox step removed 2026-07-14**
3. User copies spec → fresh session → `skill_manage(action='create')`

This keeps the skill creation session clean — no interview context leaking into the skill's SKILL.md.
