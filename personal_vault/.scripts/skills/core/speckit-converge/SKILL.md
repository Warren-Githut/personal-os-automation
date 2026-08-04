---
name: speckit-converge
description: "Spec-Kit converge gate — reconcile built code against spec/plan/tasks after battle-test, before final review. Use when implementation is done and needs delta check before review/commit."
version: 1.0.0
author: Hermes
trigger: "/speckit.converge"
category: core
---

# /speckit.converge — Build-vs-Spec Reconcile Gate

> **Purpose:** Surface what was built, what drifted, and what is missing BEFORE final review/commit.

## When to Use

- After `battle-test` + `ab-test`
- Before `code-review-and-quality` and final commit — reconcile FIRST so review runs once on already-reconciled code
- After rework if spec/plan changed mid-build

**When NOT to use:** During implementation; for tiny fixes; after commit already pushed.

## Output

Delta report with 3 buckets:

- **Implemented as spec'd** — matches plan/tasks/spec
- **Missing** — task/spec item not built
- **Drifted** — built but different from spec/config/assumptions

## Execution Rules

- Compare **spec → plan → tasks → built artifacts**, not just spec vs code filenames.
- Keep it concise: 1 page max. List affected files/tasks only.
- If `Drifted` or `Missing` is non-empty:
  - MUST stop before review/commit
  - Present delta to Warren for acknowledgment
  - Ask whether to accept drift, revert, or continue rework
- If clean (`PASS`): proceed to `code-review-and-quality`.
- `Converge` can rerun after rework, but must be clean before final review.
- Do NOT use this to reopen approved design debates; only report factual deltas.

## Non-IT Framing (Warren)

"Đối chiếu thực tế" sau khi build xong: kế hoạch nói gì, thực tế làm ra gì, còn thiếu hay lệch chỗ nào rồi báo trước khi commit.