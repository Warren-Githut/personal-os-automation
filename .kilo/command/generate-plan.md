---

description: "Plan generator — formalize raw ideas / brainstorm output into structured implementation plan. Bridge between ideation and /review-plan."
updated: 2026-06-02
---

# /generate-plan — Structured Plan Generator
# v1.0 | 2026-05-30
# PURPOSE: Formalize raw requirements (from brainstorm, direct ideas, or pain points) into structured plan ready for /review-plan.
# POSITION IN WORKFLOW:
#   /brainstorm → /generate-plan → /review-plan → code → /review-audit
#   Direct ideas → /generate-plan → /review-plan → code → /review-audit
#   /explore (GO) → [auto-gen plan internally within /explore] → /review-plan
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
- Warren needs ops feasibility filter first → use /explore

---

## Core Principle

/generate-plan **does not filter** — Warren has already decided to build. It only formalizes:
- Input: raw concept (may be messy, not yet structured)
- Process: ORION reads input + vault context → structures into 6 sections
- Output: plan ready-to-paste into /review-plan
- No Python coding, no data changes, no index entry creation

---

## STEP 1 — CLASSIFY INPUT

ORION reads input, self-classifies:

**Trivial check:**
Input is 1 clear sentence, small scope (fix 1 line, update 1 field, rename 1 file)?
→ If YES: output lightweight plan directly + "Lightweight — paste into /review-plan to review if needed."
→ If NO: continue to Step 2.

**Vague check:**
Input <3 words, unclear domain or unclear purpose?
→ If YES: ask 1 clarifying question before generating.

**Sufficiently clear → Step 2.**

---

## STEP 2 — VAULT CONTEXT (optional — lightweight scan)

ORION self-judges: is reading vault necessary?
- If input is self-contained enough (e.g.: "create script to calculate average cover per store") → skip, plan only.
- If input needs cross-reference with vault (e.g.: "create command for new workflow") → light read:
  1. Check CONTEXT.md — existing workflows, cadence
  2. List related files based on input domain (use domain map similar to /explore)
  3. Do not read full content — only scan title + frontmatter

**Limit:** max 3 files. If input needs >3 files → recommend running /explore first.

---

## STEP 3 — GENERATE PLAN

ORION generates plan with **6 mandatory sections**:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PLAN: [name — 2-5 words]

PROBLEM: [1-2 sentences — root problem. If input relates to vault → cite evidence.
          If input from brainstorm → use commit summary.]

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
- No vague language: "might", "should consider" → replace with "will", "needs"
- Each KPI must have a measurement method — not just "increase efficiency" but "reduce 5 minutes per run"
- File paths must exist in vault (or will be created) — ORION verifies

---

## STEP 4 — CONFIRM GATE

After outputting plan block, ORION **must ask Warren**:

```
📋 Plan ready.

Any changes? Or proceed to /review-plan?
```

### Rules:
- ORION waits for Warren's response. Do not auto-proceed.
- **If Warren suggests changes** → ORION updates the plan accordingly → re-output the updated plan → ask again: "Any changes? Or proceed to /review-plan?"
- **If Warren says "review-plan" or "/review-plan"** → ORION auto-loads /review-plan and pipes the plan in. Warren does NOT need to manually paste — the plan is already in context.
- **If Warren says "ok" / "go ahead" / "yes"** → same as "review-plan" — auto-pipe.

→ /review-plan will run 3 personas debate + Senior Manager verdict.
→ After APPROVE: auto-implement.
→ After implement: /review-audit → SHIP.

---

## CAPTURE GATE (optional — ask once)

After outputting plan, ask **once only**:

```
📝 Save this plan to _ideas/generated_plans/? y / n
```

**Rules:**
- Only ask once. This plan is saved so Warren can come back later (if not implementing immediately).
- If y → create file `_ideas/generated_plans/YYYY-MM-DD_[plan-name].md`:
  - YAML: `created: YYYY-MM-DD`, `title: [plan name]`, `domain: [domain]`, `status: generated`
  - Content: 6 sections from Step 3 + 1 line "Paste into /review-plan to review."
- If n → stop. Write nothing.
- If Warren implements immediately → default n (no need to save).
- **If this plan creates a NEW COMMAND →** remind Warren: "Remember to update .kilo/agent/lusine.md SLASH COMMANDS section with the new command."
  (ORION does not auto-update — Warren reviews manually first.)

---

## Anti-patterns

- ❌ Filter idea — /generate-plan is not /explore. If input needs filtering → recommend /explore
- ❌ Auto-pipe to /review-plan without asking Warren first — must ask "Any changes or /review-plan?" and wait for confirm
- ❌ Vault scan too deep — /generate-plan only needs lightweight scan, not full content
- ❌ Create file without going through capture gate
- ❌ Write index entry — plan is a temporary artifact, no index needed
- ❌ Output plan longer than 1 screen — must be concise, Warren understands in 30 seconds

---

## Example

```
Warren: /generate-plan create script to auto-calculate average cover per hour for all 3 stores

ORION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PLAN: Auto Average Cover Calculator

PROBLEM: Currently Warren has to manually calculate average cover/hour
         from PowerBI screenshots every week — takes ~10 minutes.

APPROACH: Create 1 Python script to parse hourly cover from current log format,
          output weekly average table. Run manually when new data arrives.

SCOPE: 1 new script + 1 existing log file

KPIs:
  - Time reduction: from 10 minutes → 30 seconds per run
  - Zero copy-paste error (currently has silent wrong-number risk)

FILES:
  - vault/scripts/avg_cover_calculator.py — CREATE
  - vault/10_OPERATION_DATA/09_Hourly_Cover_Revenue_Log.md — READ only

STEPS:
  1. Create scripts/avg_cover_calculator.py — parse data + calculate average
  2. Test with 2 most recent weeks
  3. /review-audit → SHIP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Plan ready. Any changes? Or proceed to /review-plan?

📝 Save this plan? y / n
```

---

**v1.0 | 2026-05-30 | Initial version — Structured plan generator. Bridges brainstorm/ideas → /review-plan. No auto-pipe, optional capture gate.**

