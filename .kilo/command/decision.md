---
model: deepseek-obsidian/deepseek-v4-pro
description: "Decision log protocol (create/close life decisions) adapted for ORION+Deepseek toolchain."
updated: 2026-06-02
---

# Decision Protocol — Slash Command
# v2.2 | 2026-05-25

## Purpose
Formalize personal decisions: clarify context -> apply Critical Thinking -> draft entry -> approve -> log -> commit.

## Usage

**Create a new decision:**
```
/decision [decision_summary]
```

**Close an existing decision:**
```
/decision close [decision_summary]
```

**Examples:**
```
/decision Start BTC DCA strategy with 5% monthly allocation
/decision Set up emergency fund to 3 months burn
/decision Hire family lawyer for GG access
/decision close BTC DCA strategy pilot
```

## Parameters
- **[decision_summary]** = 2-8 word summary of the decision (clear intent)
- **close** = subcommand to archive an existing open decision from CONTEXT.md §7

---

## Steps ORION Will Execute

---

## FLOW A: `/decision [decision_summary]` (New Decision)

### 1. CLARIFY WITH WARREN

**Field A (trigger) requires Warren's answer — only Warren knows why this decision is happening.**

For fields B-F, ORION proposes answers based on CONTEXT.md and CLAUDE.md, then asks Warren to confirm or override.

**PAUSE — display this prompt:**

```
Decision: [decision_summary]

A. What triggered this? (REQUIRED — only you know this)
   -> [leave blank for Warren to fill]

B. Scope: [ORION's proposed scope based on decision summary]
   -> Override? (or press y to accept)

C. Timeline: [ORION's proposed timeline based on decision type + review date guidelines]
   -> Override? (or press y to accept)

D. Key stakeholders: [ORION's proposed list based on scope]
   -> Override? (or press y to accept)

E. Success metric: [ORION's proposed KPI based on decision domain]
   -> Override? (or press y to accept)

F. Constraints / trade-offs: [ORION's proposed constraints based on CONTEXT.md active decisions]
   -> Override? (or press y to accept)

Reply with A's answer + any overrides for B-F. Type y for any field you accept as-is.
```

**How ORION proposes B-F:**
- B (scope): infer from decision summary keywords (e.g., "trading" if finance-related; "family" if GG/parents)
- C (timeline): apply review date guidelines — finance/trading -> 4-8 weeks; family/legal -> 8-12 weeks; health -> 4-6 weeks; growth/learning -> 2-4 weeks
- D (stakeholders): default "Self"; add "ex" if family/GG decision; add "parents" if family finance; add "lawyer" if legal
- E (success metric): propose the most relevant KPI for the domain (net worth change for finance, access frequency for GG, BMI for health)
- F (constraints): check CONTEXT.md §7 for any active decisions that constrain this one; state "None identified" if none

**Wait for Warren's response. Do not proceed without field A answered.**

---

### 2. APPLY CRITICAL THINKING (4-Step Framework)

Using Warren's context, apply:

**Steel Man** (strongest version, 2-3 sentences)
- What does success look like?
- What assumption makes this decision optimal?
- State it as confidently as possible — don't hedge

**Real Problems** (broken assumption / unstated dependency)
- What could fail that the decision doesn't account for?
- Short-term fix vs. long-term impact — state both explicitly
- The dependency this decision is betting on

**Hardest Question** (the uncomfortable one Warren is probably avoiding)
- Single question that, if answered wrongly, breaks the decision
- Must be specific (not "will we have budget?" — that's easy)
- State it directly. Don't soften.
- If genuinely uncertain: ask Warren "What are you most uncertain about?"

**Concrete Alternative** (if building from scratch)
- One actionable change, not vague direction
- Wrong: "go slower" -> Right: "start with 2% DCA for 1 month before committing to 5%"

---

### 3. DRAFT ENTRY

```yaml
---
title: "[Decision_Summary]"
date: "YYYY-MM-DD"
scope: "[trading | health | family | finance | growth | relationship]"
status: "open"
initiated_by: "[Warren | external]"
timeline: "[Immediate | YYYY-MM-DD]"
stakeholders: ["Self", "ex", "parents", ...]
success_metric: "[KPI or outcome]"
review_date: "[YYYY-MM-DD]"
related: ["[[wiki/Page_1]]", "[[wiki/Page_2]]"]
tags: ["life", "trading", "family", "health", "finance", ...]
---

## Context
[Warren's A: What triggered this?]

## Scope & Timeline
Scope: [Warren's B]
Effective: [Warren's C]

## Steel Man
[ORION's 2-3 sentence strongest version]

## Real Problems & Trade-offs
**Short-term fix:** [immediate impact]
**Long-term impact:** [consequence over 3-12 months]

**Broken assumption:** [what this decision bets on]
**Dependency:** [what has to be true for this to work]

## Hardest Question
[The uncomfortable question Warren is probably avoiding]

## Concrete Alternative
[One specific change if building from scratch]

## Success Criteria
- [Metric 1: KPI, target, measurement method]
- [Metric 2: ...]
- [Metric 3: ...]

Review scheduled: [review_date]

## Status Log
| Date | Status | Note |
|---|---|---|
| [date] | open | Initial decision drafted |
| [review_date] | [open/closed/modified] | [outcome] |
```

**Review date guidelines** (set realistically):
- Finance / Trading decisions -> 4-8 weeks
- Family / Legal -> 8-12 weeks
- Health -> 4-6 weeks
- Growth / Learning -> 2-4 weeks

---

### 4. SHOW WARREN + WAIT FOR APPROVAL

Display full draft entry, then ask:

```
Here is the full decision entry for [decision_summary].

[full draft]

Options:
  y        -> approve as-is, save to Decision Log
  [edit]   -> type any specific changes, ORION will update and re-show
  
Note: once saved, Steel Man and Hardest Question are locked.
Status Log is where outcomes get added later.
```

**PAUSE — do not save until Warren types `y` or approves after edits.**

---

### 5. DETERMINE TARGET

**IF decision is OPEN** (will be reviewed in future):
-> Save full entry to `30_KNOWLEDGE_BASE/wiki/DECISION_LOG.md` with `status: open`
-> Add summary row to `CONTEXT.md §7 Active Life Decisions` table

**IF decision is CLOSED** (already happened, logging for record):
-> Save full entry to `30_KNOWLEDGE_BASE/wiki/DECISION_LOG.md` with `status: closed`
-> Do NOT add to CONTEXT.md §7

---

### 6. UPDATE FILES

**A. DECISION_LOG.md**
- `read_file(path="30_KNOWLEDGE_BASE/wiki/DECISION_LOG.md")`
- `apply_diff()` to append full YAML + body entry at the end
- `apply_diff()` to update frontmatter: `last_updated: [date]`

**B. CONTEXT.md §7 (if OPEN only)**
- `read_file(path="00_CORE_LOGIC/CONTEXT.md")`
- `apply_diff()` to append row to Active Life Decisions table:
  ```
  | [date] | [decision_summary] | [scope] | [review_date] |
  ```

---

### 7. UPDATE LOG
- `read_file(path="_kilo/ACTIVITY_LOG.md")`
- Read content, locate today's date section (or create if missing), append entry:
  ```
  | HH:MM | /decision [decision_summary] | [scope] | status=[open/closed] | review: [review_date] |
  ```

---

### 8. COMMIT
```
execute_command(command="git add 30_KNOWLEDGE_BASE/wiki/DECISION_LOG.md && git add _kilo/ACTIVITY_LOG.md")
execute_command(command="git add 00_CORE_LOGIC/CONTEXT.md")  # only if open decision
execute_command(command="git commit -m \"Decision: [decision_summary] | [scope] | Review: [review_date]\"")
execute_command(command="git log --oneline -1")
```
Paste commit hash as confirmation.

---

## FLOW B: `/decision close [decision_summary]`

Use when a previously open decision has been resolved and should move to archive.

### 1. FIND THE DECISION
- `read_file(path="00_CORE_LOGIC/CONTEXT.md")` -> scan §7 for a row matching `[decision_summary]`
- If not found: "⚠️ No open decision matching '[decision_summary]' found in CONTEXT.md §7. Check spelling or list current open decisions?"
- If found: display the row to Warren for confirmation

### 2. COLLECT OUTCOME

**Field A (what actually happened) requires Warren's answer — ORION was not present.**

For fields B and C, ORION proposes based on CONTEXT.md and Decision Log context.

**PAUSE — display this prompt:**

```
Closing: [decision_summary]
Originally decided: [date from Decision Log] | Scope: [scope] | Review date: [review_date]

A. Outcome: What actually happened? (REQUIRED — describe in 1-3 sentences)
   -> [leave blank for Warren to fill]

B. Result: [ORION's proposed result based on any known data in context]
   Options: Success ✅ | Partial 🟡 | Failed ❌ | Cancelled
   -> Override? (or press y to accept)

C. Learnings: [ORION's proposed learning based on the Hardest Question from original entry]
   -> Override, expand, or type y to accept (optional — type "skip" to leave blank)
```

**How ORION proposes B-C:**
- B (result): if any wiki pages or context mention outcome data (e.g., net worth changes, GG access progress), propose the matching result category; otherwise propose "Partial 🟡" as conservative default
- C (learnings): re-read the original Hardest Question from the Decision Log entry; propose a learning that directly answers whether that question played out

**Wait for Warren's response. Field A is required before proceeding.**

### 3. UPDATE DECISION_LOG.md
- `read_file(path="30_KNOWLEDGE_BASE/wiki/DECISION_LOG.md")` -> find existing entry by title
- Change `status: open` -> `status: closed`
- Append to Status Log table:
  ```
  | [today's date] | closed | [Warren's outcome summary] |
  ```
- Add `## Outcome` section after Status Log:
  ```
  ## Outcome
  Result: [Success / Partial / Failed / Cancelled]
  [Warren's A: what happened]

  ## Learnings
  [Warren's C, or "None recorded"]
  ```

### 4. REMOVE FROM CONTEXT.md §7
- `read_file(path="00_CORE_LOGIC/CONTEXT.md")` -> `apply_diff()` to delete the row for this decision from the Active Life Decisions table

### 5. UPDATE LOG
Append to `_kilo/ACTIVITY_LOG.md`:
```
| [date] | /decision close [decision_summary] | Result: [outcome] |
```

### 6. COMMIT
```
execute_command(command="git add 30_KNOWLEDGE_BASE/wiki/DECISION_LOG.md && git add _kilo/ACTIVITY_LOG.md")
execute_command(command="git add 00_CORE_LOGIC/CONTEXT.md")
execute_command(command="git commit -m \"Decision closed: [decision_summary] | Result: [outcome] | [date]\"")
execute_command(command="git log --oneline -1")
```

---

## Rules

- **Critical Thinking is mandatory.** No shortcuts, even for obvious decisions. The Hardest Question must be genuine.
- **Hardest Question cannot be easy.** If it's something Warren already knows the answer to, it's the wrong question.
- **Trade-offs are explicit.** Never hide short-term pain or long-term consequences.
- **3 required fields minimum** (A, B, C). Don't wait for D/E/F if Warren is moving fast.
- **Open decisions live in CONTEXT.md §7** — Warren reads this every session.
- **Closed decisions go to DECISION_LOG only** — queryable, dated, immutable.
- **Review dates are hard.** Set using the guidelines in Step 3, not arbitrary.
- **`/decision close` is the ONLY way to move decisions from §7 to archive.** Never remove from §7 without running this flow.
- **Context budget:** This command is large. For complex decisions requiring wiki lookups, run `/decision` first to capture context, then query wiki pages in a follow-up. Don't try to do both in one pass if the decision touches multiple domains.

---

## Example Workflow

### Create
```
Warren: /decision Start BTC DCA with 5% monthly allocation
ORION: [Step 1 — asks A/B/C required + D/E/F optional]
Warren: A. BTC is at $55k — my trigger price. B. Trading. C. Start June 2026.
ORION: [Step 2 — Critical Thinking] [Step 3 — draft] [Step 4 — shows Warren]
Warren: Approved. Add kill criteria: if BTC drops below $40k, pause DCA.
ORION: [Updates draft] [Steps 5-8 — saves, commits]
-> Commit: abc1234
```

### Close
```
Warren: /decision close BTC DCA strategy
ORION: Found in §7. Outcome?
Warren: A. Did 3 months DCA, +12% return. B. Success ✅. C. DCA at trigger price was correct entry strategy.
ORION: [Updates DECISION_LOG, removes from §7, commits]
-> Commit: def5678
```

---

**v2.2 | 2026-05-25 | Personal_OS adaptation: §10 -> §7, personal life scope, _kilo/ACTIVITY_LOG.md. | ORION+Deepseek adaptation: frontmatter, agent name update, toolchain wrappers (read_file/apply_diff/execute_command). | v2.1 | 2026-05-05 | Added: ORION-proposes pattern for fields B-F (Flow A Step 1) and B-C (Flow B Step 2). Field A always requires Warren. y to accept any ORION proposal, type to override.**
