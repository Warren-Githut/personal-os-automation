---
model: deepseek-obsidian/deepseek-v4-pro
description: "Plan generator — formalize raw ideas / brainstorm output into structured implementation plan. Bridge between ideation and /review-plan."
updated: 2026-06-02
---

# /generate-plan — Structured Plan Generator
# v1.0 | 2026-05-30
# PURPOSE: Formalize raw requirements (from brainstorm, direct ideas, or pain points) into structured plan ready for /review-plan.
# POSITION IN WORKFLOW:
#   /brainstorm -> /generate-plan -> /review-plan -> code -> /review-audit
#   Direct ideas -> /generate-plan -> /review-plan -> code -> /review-audit
#   /explore (GO) -> [auto-gen plan internally within /explore] -> /review-plan
# DIFFERENCE FROM /explore:
#   /explore = ops feasibility filter (should we build?) + auto-gen plan if GO
#   /generate-plan = only generate structured plan (already know what to build), no filter
#   Use /generate-plan when Warren has ALREADY passed the filter — no need to /explore again

---

## Usage

```
/generate-plan [raw requirement — 1-5 sentences]
/generate-plan [paste brainstorm output / top ideas / feature concept]
```

**Auto-trigger (WEAK — check context):**
- Warren says "generate plan", "write spec for", "formalize idea"
- Warren just finished a brainstorm and says "create the plan"

**Do not trigger when:**
- Warren asks "what's the plan", "create plan" (easy false positive — check context: calendar vs feature build)
- Mid-flow in another skill (/explore, /review-plan, /morning-brief, /process-notes)
- Warren needs ops feasibility filter first -> use /explore

---

## Core Principle

/generate-plan **does not filter** — Warren has already decided to build. It only formalizes:
- Input: raw concept (may be messy, not yet structured)
- Process: ORION reads input + vault context -> structures into 6 sections
- Output: plan ready-to-paste into /review-plan
- No Python coding, no data changes, no index entry creation

---

## STEP 1 — CLASSIFY INPUT

ORION reads input, self-classifies:

**Trivial check:**
Input is 1 clear sentence, small scope (fix 1 line, update 1 field, rename 1 file)?
-> If YES: output lightweight plan directly + "Lightweight — paste into /review-plan to review if needed."
-> If NO: continue to Step 2.

**Vague check:**
Input <3 words, unclear domain or unclear purpose?
-> If YES: ask 1 clarifying question before generating.

**Sufficiently clear -> Step 2.**

---

## STEP 2 — VAULT CONTEXT (optional — lightweight scan)

ORION self-judges: is reading vault necessary?
- If input is self-contained enough (e.g.: "create script to calculate net worth trend") -> skip, plan only.
- If input needs cross-reference with vault (e.g.: "create command for new personal workflow") -> light read:
   1. Check CONTEXT.md — existing life domains, cadence, active decisions (§7)
   2. List related files based on input domain (use domain map similar to /explore)
   3. Do not read full content — only scan title + frontmatter

**Limit:** max 3 files. If input needs >3 files -> recommend running /explore first.

---

## STEP 3 — GENERATE PLAN

ORION generates plan with **6 mandatory sections**:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PLAN: [name — 2-5 words]

PROBLEM: [1-2 sentences — root problem. If input relates to vault -> cite evidence.
          If input from brainstorm -> use commit summary.]

APPROACH: [2-3 sentences — solution. Specific, not generic.]

SCOPE: [list affected files/components — list or bullet]

KPIs: [2-3 success metrics — specific, measurable]

FILES:
  - [path/file] — [CREATE/UPDATE/DELETE] — [1-line reason]

STEPS:
   1. [specific step — which file, what to do]
   2. [specific step — which file, what to do]
   3. ...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Rules:**
- No vague language: "might", "should consider" -> replace with "will", "needs"
- Each KPI must have a measurement method — not just "increase efficiency" but "reduce 5 minutes per run"
- File paths must exist in vault (or will be created) — ORION verifies

---

## STEP 4 — NEXT ACTION

After outputting plan block:

```
📋 Plan ready.

Next step: Paste block above into:
  /review-plan [paste plan here]
  
-> /review-plan will run 3 personas debate + Senior Manager verdict.
-> After APPROVE: auto-implement.
-> After implement: /review-audit -> SHIP.
```

**Do not auto-pipe** — Warren pastes manually to control the flow.

---

## CAPTURE GATE (optional — ask once)

After outputting plan, ask **once only**:

```
📝 Save this plan to _ideas/generated_plans/? y / n
```

**Rules:**
- Only ask once. This plan is saved so Warren can come back later (if not implementing immediately).
- If y -> create file `_ideas/generated_plans/YYYY-MM-DD_[plan-name].md`:
  - YAML: `created: YYYY-MM-DD`, `title: [plan name]`, `domain: [domain]`, `status: generated`
  - Content: 6 sections from Step 3 + 1 line "Paste into /review-plan to review."
- If n -> stop. Write nothing.
- If Warren implements immediately -> default n (no need to save).
- **If this plan creates a NEW COMMAND ->** remind Warren: "Remember to update .kilo/agent/lusine.md SLASH COMMANDS section with the new command."
  (ORION does not auto-update — Warren reviews manually first.)

---

## Anti-patterns

- ❌ Filter idea — /generate-plan is not /explore. If input needs filtering -> recommend /explore
- ❌ Auto-pipe to /review-plan — Warren pastes manually for control
- ❌ Vault scan too deep — /generate-plan only needs lightweight scan, not full content
- ❌ Create file without going through capture gate
- ❌ Write index entry — plan is a temporary artifact, no index needed
- ❌ Output plan longer than 1 screen — must be concise, Warren understands in 30 seconds

---

## Example

```
Warren: /generate-plan create net worth tracking script

ORION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PLAN: Net Worth Tracker Script

PROBLEM: Warren manually tracks net worth across cash, BTC, and equity
         holdings — currently using mental math, easy to miss.

APPROACH: Create 1 Python script that reads from pulse logs and TCBS 
           exports, outputs monthly net worth table with trend.

SCOPE: 1 new script + 1 existing pulse log

KPIs:
  - Time reduction: from 15 minutes -> 1 minute per month
  - Zero calculation error (currently has silent wrong-number risk)

FILES:
  - scripts/net_worth_tracker.py — CREATE
  - 10_PULSE/pulse_finance.md — READ only

STEPS:
   1. Create scripts/net_worth_tracker.py — parse TCBS export + BTC price
   2. Test with 2 most recent months
   3. /review-audit -> SHIP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Paste plan into /review-plan [paste] to review.

📝 Save this plan? y / n
```

---

**v1.0 | 2026-05-30 | Initial version — Structured plan generator. Bridges brainstorm/ideas -> /review-plan. No auto-pipe, optional capture gate.**
