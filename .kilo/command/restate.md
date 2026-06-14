---
model: deepseek-obsidian/deepseek-v4-flash
description: "Pre-flight check — Hermes reads raw input, emits RESTATE:/CLARIFY: scaffold, waits for Warren confirm before proceeding"
updated: 2026-06-04
---

# /restate — Pre-Flight Restate + Clarify Gate
# v1.1 | 2026-06-04
# PURPOSE: Warren brain-dump raw input → Hermes auto restate + clarify, wait for confirm → proceed.
# POSITION IN WORKFLOW: Raw input → /restate → Hermes restates/clarifies → Warren confirm "ok" → analysis.
# WHY: R1 (RESTATE GATE) in system prompt is reactive. /restate is proactive — Warren intentionally
#       triggers before Hermes touches the input, mechanical backup, not dependent on model "remembering".

---

## Usage

```
/restate [paste brain-dump, data, raw notes here]
```

---

## Protocol — do not skip

### STEP 1 — Read Input

Read all $ARGUMENTS (text after /restate). If empty or <10 characters → ask Warren to paste content to restate.
If >1500 characters → auto summarize into key points before restating (model attention finite).

### STEP 2 — Emit RESTATE + CLARIFY

Analyze input → generate 2 lines:

```
RESTATE: <summary of Warren's request in 1-2 sentences — exact, no additions, no omissions>
CLARIFY: <max 3 questions about ambiguities; if none, write exactly "None — proceeding">

**IMPORTANT v1.1:** Each CLARIFY question MUST include a **suggested/optimal answer** right after the question, so Warren can just confirm or correct instead of typing from scratch.

Format:
```
CLARIFY:
1. [question] → SUGGESTED: [optimal answer] | Alternative: [other option if applicable]
2. [question] → SUGGESTED: [optimal answer] | Alternative: [other option if applicable]
```
─────────────────
Confirm this restate is correct? If correct type "ok" — if wrong correct it.
```

### STEP 3 — Confirm Gate

- Warren says "ok" / "correct" → proceed STEP 4.
- Warren corrects/disagrees → Hermes adjust restate per feedback → re-emit → re-confirm.

### STEP 4 — Proceed with Analysis

Use all original content from $ARGUMENTS. Do NOT re-ask for input. Do NOT require Warren to resend.
Auto analyze and respond as a normal request.

---

## Anti-patterns

- Open-ended clarifying questions without suggested answers → WRONG. v1.1: every CLARIFY must include SUGGESTED answer.
- After confirm, ask again "what do you need analyzed?" → WRONG. $ARGUMENTS already available, Hermes auto proceeds.
- After confirm reply "ok, received" with no analysis → WRONG. Must complete the response.
- Modifying Warren's intent during restate → WRONG. Restate must be faithful.

---

## Side Effects

- No file writes. No API calls. No side effects.
- Input only used in session context, not persisted.
