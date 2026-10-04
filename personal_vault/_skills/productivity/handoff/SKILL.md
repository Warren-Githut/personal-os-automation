---
name: handoff
description: Compact the current conversation into a handoff document so a fresh agent/session can continue the work. Use when ending a session with incomplete work, before /new, or when delegating a half-done task to another agent/profile.
argument-hint: "What will the next session focus on?"
disable-model-invocation: true
---

# Handoff

Write a handoff document that lets a fresh session (or another agent/profile) pick up incomplete work without re-deriving context.

## When to invoke
- Ending a session with work still in progress
- About to run /new
- Delegating a half-done task to a subagent or another profile

## Process
1. **Collect** — From the current conversation, capture:
   - Goal: what we were building towards
   - Done: completed steps with verification evidence (link or one-line proof)
   - Stuck: open blockers, unanswered questions, risks
   - Decisions: ADRs or key calls already made (reference path, don't re-write)
2. **Suggest skills** — List 2-4 skills the next session should invoke (e.g. `ops-col`, `warren-ops-pipeline`, `incremental-implementation`).
3. **Redact** — Strip API keys, passwords, PII before writing.
4. **Write** — Save to vault (never temp dir):
   - If tied to a case → `_cases/<case>/HANDOFF_<YYYY-MM-DD>.md`
   - Else → `_inbox/HANDOFF_<YYYY-MM-DD>.md`
   - YAML frontmatter required: `date: YYYY-MM-DD`, `type: handoff`, `related_case: <case id or none>`
5. **Reference, don't duplicate** — Point to existing spec/plan/ADR by path. Never copy their content.
6. **Git reminder** — If uncommitted code exists, note it and remind to run `git-workflow-and-versioning` before /new.

## Completion criterion
Handoff is done when: a reader with zero context can resume the work from the doc alone, and every factual claim links to a source file or session artifact.

## Do NOT
- Save to OS temp dir (lost on shutdown) — always vault
- Paste secrets — step 3 already strips them
- Re-state content already in spec/plan/ADR — step 5 already forbids this
