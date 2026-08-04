---
name: speckit-constitution
description: "Spec-Kit constitution gate — establish project governing principles once per project, before ideation. Use when starting a new project/feature that needs lasting governance rules (auth/data/stack/budget/compliance). Not for one-off fixes."
version: 1.0.0
author: Hermes
trigger: "/speckit.constitution"
category: core
---

# /speckit.constitution — Project Constitution Gate

> **Purpose:** Capture non-negotiable governance rules BEFORE any ideation/spec/plan. This is the "luật chơi" layer.

## When to Use

- New project, feature, or initiative with multi-session lifecycle
- Lasting governance is likely (data policy, stack constraints, budget/compliance, team conventions)
- Anything that will outlive a single chat session

**When NOT to use:** One-off fixes, ops daily, simple config tweaks, throwaway experiments.

## Output

A single constitution markdown document. Minimum sections:

```markdown
# <Project> Constitution

## Governing Rules
- [Non-negotiable rule 1]
- [Non-negotiable rule 2]

## Allowed / Preferred
- [Thing we actively want]

## Prohibited
- [Hard boundary: do NOT do this]

## Open Governance Questions
- [ ] [Question needing human input]
```

## Execution Rules

- Run **once per project**, before `interview-me` / `idea-refine`.
- Do NOT silently overwrite an existing constitution. If one exists, surface the delta and ask Warren for re-ratification.
- If Spec-Kit project exists: save at `.specify/templates/constitution.md`
- Else: save at `vault/_docs/<project>-constitution.md`
- Keep it short: 1–2 screens max. If it's longer, it's not a constitution, it's a policy doc.
- End with exact 3 questions: "Bố chốt nguyên tắc này có ổn không? Cần sửa chỗ nào trước khi vào việc?"

## Non-IT Framing (Warren)

"Luật chơi" của dự án — nếu sau này 2 người cùng làm sẽ đọc cái này để biết ranh giới đỏ/được phép/không được phép.