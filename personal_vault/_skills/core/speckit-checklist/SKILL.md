---
name: speckit-checklist
description: "Spec-Kit checklist gate — lightweight artifact completeness/quality check after spec, before planning. Use when a spec exists and needs validation before task breakdown."
version: 1.0.0
author: Hermes
trigger: "/speckit.checklist"
category: core
---

# /speckit.checklist — Artifact Checklist Gate

> **Purpose:** Catch missing/weak parts of a spec BEFORE planning. lightweight blocker, not audit theater.

## When to Use

- `spec-driven-development` completed and Warren has reviewed the spec
- Before `planning-and-task-breakdown`
- After spec changes mid-flight and before re-entering planning

**When NOT to use:** Before spec exists; after planning already started; for one-line fixes.

## Output

Either:

- `PASS` — minor optional notes only
- `BLOCKED` — exact missing items, stop before planning

## Minimum Checklist

```markdown
- [ ] Objective and user story exist
- [ ] Assumptions are explicit
- [ ] Boundaries defined: Always / Ask first / Never
- [ ] Success criteria are testable
- [ ] Open questions resolved or deferred with owner
```

## Execution Rules

- Keep lightweight — 1 screen max.
- Never re-ask questions already answered in the spec.
- Do NOT extend this into redoing the spec; output blocker items only.
- If `BLOCKED`: stop, summarize gaps, ask Warren which to fix now vs defer.
- If `PASS`: proceed to `planning-and-task-breakdown`.
- This is a **single checkpoint**, not repetitive ritual.

## Non-IT Framing (Warren)

"Kiểm tra đơn hàng" sau khi viết spec: còn thiếu mục gì không? Nếu còn → dừng, bổ sung xong mới chia task.