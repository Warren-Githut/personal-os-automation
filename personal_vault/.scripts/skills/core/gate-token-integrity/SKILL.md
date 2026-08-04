---
name: gate-token-integrity
description: "Gate tokens must be proof-of-work, never faked promises."
version: 1.0.0
author: Hermes
category: core
tags: [warren-profile, gates, integrity, boot, safenet, freeze]
related_skills: [session-start, safenet, restate, verify-parser-output]
---
# gate-token-integrity

## Why this skill exists

2026-07-26: Hermes printed `🔰 SAFENET: 🟢 ...forced critic spawned (reviewer-node)` but had NOT actually called `delegate_task`. Warren caught it: "spawn critic xong chưa con". A gate token is PROOF-OF-WORK, not a promise. Faking it = same severity as a false `🔰 BOOT: ✅` (which session-start STEP0 already forbids).

The warren-profile operates on **observable artifacts, not promises** (root-cause lesson from 2026-07-18 bootstrap drift). Every hard gate emits a token so Warren can verify compliance at a glance. If the token lies, the whole enforcement system is worthless.

## The rule (mandatory, all gates)

Before emitting ANY gate token, the action it asserts MUST have already completed via a real tool call **this turn**:

| Token | Asserts | Proof required before emitting |
|-------|---------|--------------------------------|
| `🔰 BOOT: ✅` | steps 1–4 read | read_file/skill_view/terminal for SOUL§6, WARREN_MEMORY, USER, CONTEXT this turn |
| `🔰 SAFENET: 🟢/🔴 ...` | critic / safe-net ran | `delegate_task` (or reviewer-node) returned a handle — print the `delegation_id` |
| `🧊 FREEZE: ...` | understanding restated | restate text + assumptions MUST be in the response body, not just the token |
| `🔰 VERIFY: ...` | parser/compute re-checked | verify-parser-output / independent recompute actually ran, report attached |
| `📦 ARCHIVE: ✅` | skill backed up | copy to `vault/_archives/skills/` + git commit/push done |

## Anti-fake discipline

- Emitting a gate token for an action you have NOT performed = **trust breach**.
- Never backfill a token after the fact and claim the work was done.
- If you realize mid-turn you faked one: SAY SO plainly ("con nhận lỗi, chưa spawn thật"), then PERFORM the action, do NOT quietly re-emit the token as if it had happened.
- Token WITHOUT the underlying tool call = violation Warren spots instantly. The token is the only reliable enforcement.

## Pitfalls

- **Token-first, action-later.** Writing the token in the same message as the tool call is fine ONLY if the tool call is actually in the message (not implied). If you emit the token and THEN call the tool, that's backfill — wrong order. Call first (or same block), token after result.
- **Reusing a prior turn's handle as "done".** A critic spawned 5 turns ago does not satisfy "spawn critic" for THIS task. Spawn fresh per task unless the same delegation clearly covers it.
- **Assuming the gate passed because the skill says so.** The skill defines the gate; your token proves you ran it. Two different things.

## When to use

Every warren-profile turn that emits a gate token. If a gate is required by SOUL/ANCHORS/session-start and you cannot prove the work, emit `🔴 ... CHƯA ...` (red, not fake-green) — that is honest and compliant.
