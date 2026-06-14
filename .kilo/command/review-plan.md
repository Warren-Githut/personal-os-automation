---

description: "Data & vault plan adversarial review adapted for Hermes+Deepseek toolchain."
updated: 2026-06-02
---

# /review-plan — Data & Vault Plan Adversarial Review
# v3.0 | 2026-06-02
# KEY CHANGES v2.1→v3.0:
#   - Added Step 1C: VAULT HISTORY SCAN — search past decisions, lessons, post-mortems relevant to plan
#   - Step 2: Personas MUST reference vault history precedents if found
#   - Step 4: Added VAULT HISTORY field + auto-escalate when past decision contradicts plan
#   - Spec block: Added History field
#   - All content translated to English (R4 LANGUAGE MANDATE)
# PURPOSE: Warren pastes any data/vault/structure plan → vault scan → 4 expert personas debate → Senior Manager verdict.
# SCOPE: Data architecture, vault structure, log formats, naming conventions, parser flows, retrieval design.
#        Hybrid plans (data + automation): review-plan covers data part, flags automation part for /review-workflow.
# NOT FOR: Pure IT workflow scripts, automation-only logic → use /review-workflow instead.
# NOT FOR: Code review after writing → use /review-code instead.

---

## Usage
```
/review-plan [paste your plan here]
```

---

## Core Philosophy (mandatory application — no exceptions)

Before reviewing any plan, all 4 personas read and apply these 2 principles:

**1. Find the Real Problem first**
Users often describe what they *want* (a feature, a new file) rather than what they *need* (solving a real bottleneck). The mandatory question to ask: "If we don't build this, what really gets blocked?" Often the best solution is changing the operational process — no code or new files needed.

**2. Design data structure first, logic later**
Linus Torvalds: *"Bad programmers worry about the code. Good programmers worry about data structures."* If the data flow and storage method are designed correctly, the processing code naturally becomes simple. Conversely: wrong data structure → all logic built on top of it will also be wrong.

*Note: "Design for Deletion" (independent modules, easy to remove) is a coding principle — applied in `/review-code`, not here.*

---

## Protocol — 6 Steps, no skip, no guesswork

> **SILENT MODE:** Run Steps 1–3 as internal reasoning — do not print. SILENT MODE overrides all "Required Output:" in Steps below. Sole exception: if you need to ask Warren for clarification → ask before continuing. Only print Step 4 verdict block.

---

### STEP 1 — READ & FRAME (SILENT)

Hermes reads the plan Warren pasted in and formats it as:

```
PLAN SUMMARY      : [1 sentence — what + goal]
ASSUMED STRUCTURE : [bullet — main components of the plan]
ASSUMED GOAL      : [retrievability / analysis / automation / other]
REAL PROBLEM CHECK: [1 sentence — what root problem is this plan solving?
                     If unclear → ask Warren before continuing]
CONTEXT           : L'Usine 3-store F&B | Warren OS vault | Hermes+Deepseek stack
```

If the plan is too vague (under 3 lines, unclear goal) → ask 1 clarifying question first.
If the plan is code/script (has function, variable, import) → redirect immediately: "Use /review-code for code review — /review-plan is only for data/vault/structure plans."
If clear enough → proceed immediately, don't ask further.

**Lightweight Gate** — check the 3 conditions below. If ALL 3 are TRUE:
- Plan has < 3 components
- Does not create new files or new schema
- Does not change existing data structure

→ If any condition is FALSE → run full protocol.
→ If ALL 3 are TRUE → output `LIGHTWEIGHT PLAN` with the format below then stop:

```
LIGHTWEIGHT VERDICT
DECISION          : APPROVE / APPROVE WITH CONDITIONS / REJECT
BLOCKER (if any)  : [Severity: HIGH/MED] — [1 sentence — when does it fail]
SUGGESTED NEXT STEP: [1 single action]
```

*(No OPEN QUESTIONS needed for lightweight plan — if there are questions, the plan isn't lightweight, upgrade to full protocol.)*

Note on counting components: 1 new field in a note = 1 component; fetch + save + tag = 3 components.

---

### STEP 1B — VAULT STRUCTURE SCAN (mandatory — must not guess, must not use memory) (SILENT)

Before debating, Hermes **must read the actual vault**. Don't assume structure from a previous session or CONTEXT.md.

Run sequentially:
1. List vault root directory
2. List `10_OPERATION_DATA/`
3. List `30_KNOWLEDGE_BASE/wiki/` and domain subfolders relevant to the plan

Internal structure:

```
VAULT SCAN RESULT:
  Existing files relevant to this plan:
    - [path/filename] — pattern: [append-newest-top / overwrite / one-off / unknown]
    - ...

  Detected data cadence:
    - [log name] → [weekly / monthly / on-demand]

  Proliferation check (if plan runs 12 months):
    → Creates [n new files] or [1 file + n entries appended]?
    → Flag immediately if answer is "many new files" — this is a proliferation risk

  Data structure check:
    → Does the plan clearly define data structure (fields, format, types) before discussing logic?
    → If not → flag before debate
```

**Proliferation Risk Definition:** Any plan that creates new files cyclically (1 file per week, 1 file per month) instead of appending to 1 growing file — is HIGH RISK. Standard pattern in this vault: 1 single log file per domain, newest entry on top, no new files created over time.

---

### STEP 1C — VAULT HISTORY SCAN (mandatory — the vault argues against the plan itself) (SILENT)

**Purpose:** Find evidence from Warren's own vault — past decisions, lessons learned, post-mortems, reversed decisions — relevant to the plan under review. The vault must challenge the plan before the personas debate.

**Why:** Warren has accumulated hundreds of operational decisions in the vault. If a new plan repeats an old mistake or contradicts a confirmed decision, it must be known BEFORE building — not after coding is complete.

**Run sequentially:**

1. **Search §10 of CONTEXT.md** (if structure supports it) — does the new plan conflict with any open Active Decisions?
2. **Search `wiki/DECISION_LOG.md`** (if it exists) — past decisions on the same topic/domain
3. **Search `_kilo/memory/LESSONS.md`** — relevant lessons learned
4. **Search wiki/ domain folders** relevant to the plan (e.g.: plan about COGS → search `wiki/menu_cogs/`; plan about staffing → search `wiki/labour_costs/`)
5. **Search memory graph** (if Kilo Code context provides access) — entities, past failures, relevant preferences

**Keyword strategy:** Use 2-3 main keywords from PLAN SUMMARY in Step 1 + domain name. Don't search vague terms ("improve", "better"). Search concrete nouns ("Sharon", "COGS", "Dinh Bien", "OIL", "LU5 lease").

Internal output:

```
VAULT HISTORY RESULT:
  Precedents found: [n]

  [If n > 0, list each precedent:]
  1. SOURCE: [path/filename — section/date if available]
     CONTENT: [1-2 sentences summarizing the relevant finding]
     VERDICT: SUPPORTS / CONTRADICTS / NEUTRAL
     [If CONTRADICTS:] CONFLICT: [plan says X, vault says Y — which one is correct?]

  2. SOURCE: ...
     ...

  [If n = 0:]
  NO PRECEDENT FOUND — this plan has no history in the vault.
  Implication: no evidence to challenge, but also no evidence the plan will work.

  CRITICAL CONTRADICTION CHECK:
  → Is there any past decision that DIRECTLY contradicts the current plan?
  → If YES → auto-flag CRITICAL BLOCKER, feed into Step 2 debate.
  → If NO → proceed normally.
```

**Auto-escalation rule:** If any precedent has verdict CONTRADICTS AND the source is an Active Decision or a confirmed lesson in LESSONS.md → this is an automatic **CRITICAL BLOCKER**. Personas in Step 2 MUST address it. Senior Manager in Step 4 MUST resolve it (either the plan changes, or the past decision is superseded with a specific reason).

---

### STEP 2 — 4 PERSONAS DEBATE

Each persona debates independently based on the plan + actual vault scan from Step 1B + vault history from Step 1C.
Must not easily agree. Each persona MUST output all 3 sections: AGREE + BLOCKER + SUGGESTION.

**Mandatory rules:**
- Blocker must be specific: "this fails when X happens" — not "there might be a problem"
- Suggestion must be actionable: "replace X with Y" — not "needs more consideration"
- If all 4 completely agree → INVALID, must find real tension before continuing
- **VAULT HISTORY RULE (v3.0):** If Step 1C found ≥1 precedent with verdict CONTRADICTS or SUPPORTS, at least 2 personas MUST reference it in their arguments. Any persona that ignores vault history when relevant precedent exists = INVALID output, redo that persona. Reason: vault history is real evidence from Warren himself — stronger than any persona's opinion.

---

#### 🟦 DATA ARCHITECT (30 years of experience)
**Lens:** Long-term structure · Data structure design · Retrievability · Schema consistency · Scalability
**Mandatory questions to answer:**
- "Is this plan's data structure defined before logic? If not, where will the logic go wrong?"
- "After 12 months with 10x data, is this plan easy to query?"
- "Does this plan create 1 growing file or many small files? Which is easier to query?"

Output format:
```
[DA] AGREE: ...
[DA] BLOCKER: ...
      Severity: CRITICAL / HIGH / MEDIUM
      Fail scenario: [specifically when does this break]
[DA] SUGGESTION: replace [X] with [Y] because [Z]
```

---

#### 🟥 OPERATIONS REALIST (30 years of real-world operations)
**Lens:** Real operator · Human error · Workflow friction · Non-IT operator reality
**Not a theoretical Data Scientist — someone who has seen good systems abandoned by real users.**
**Mandatory questions to answer:**
- "Warren or Thao use this every week/month — after 3 months of habits changing, will this plan still hold?"
- "When input is entered wrong (and it WILL be entered wrong) — how does this plan fail? Who detects it?"
- "If Warren is busy for 2 weeks and doesn't maintain it — can he pick it back up without getting lost?"

Output format:
```
[OR] AGREE: ...
[OR] BLOCKER: ...
      Severity: CRITICAL / HIGH / MEDIUM
      Fail scenario: [what specific human error will occur — and the consequence]
[OR] SUGGESTION: replace [X] with [Y] because [Z]
```

---

#### 🟩 IT DEVELOPER / Hermes (30 years of experience)
**Lens:** Implementability · Failure modes · Maintainability · Design for deletion
**Mandatory questions to answer:**
- "When this plan fails (and it WILL fail), how does it fail and who can fix it?"
- "Is there any pattern in the current vault that solves a similar problem? Why not reuse it?"
- "If 1 part of this plan needs changing after 6 months — how many places get touched?"

Output format:
```
[DEV] AGREE: ...
[DEV] BLOCKER: ...
       Severity: CRITICAL / HIGH / MEDIUM
       Fail scenario: [specific — what error, who detects, who fixes]
[DEV] SUGGESTION: replace [X] with [Y] because [Z]
```

---

#### 🟨 RUTHLESS DELETER (Musk Algorithm lens — 30 years of cutting waste)
**Lens:** Question · Delete · Simplify · Accelerate · Automate-last
**Philosophy:** "The best part is no part. The best process is no process."
**Not a critic — a deletion hunter.** If removing 1 part of the plan needs <10% added back → you haven't deleted enough.

**Mandatory questions to answer (in strict order, no skip):**

1. **Delete what?** Which components in this plan can be completely removed while ops still runs? (List each component, give verdict KEEP/DELETE for each. Minimum 1 DELETE — if none, the plan is over-scoped or Deleter hasn't worked hard enough).

2. **Simplify what (after deleting)?** What remains that can be simpler? (Prose instead of table? Append instead of new file? Inline instead of link?). DO NOT simplify what should have been deleted in question 1.

3. **Cycle time?** From idea to result, how many times does Warren have to touch this? Which steps can be cut? How long is the feedback loop to know if the plan is right/wrong? If >2 weeks to detect an error → flag CRITICAL.

4. **Automating broken?** Is the auto-implement / parser / script in this plan automating a process that hasn't been verified manually? If YES → flag CRITICAL: "Run manual N times first, then automate."

Output format:
```
[RD] DELETE: [component(s) proposed for complete removal] — fail mode if deleted: [specific]
[RD] SIMPLIFY: [only the parts remaining after DELETE]
[RD] CYCLE TIME: [n touchpoints, feedback loop = X days] — cut: [proposal]
[RD] AUTOMATION CHECK: [SAFE / RISK — broken process?]
[RD] BLOCKER (if any): [Severity] — [scenario]
[RD] VERDICT: PLAN OVER-BUILT / RIGHT-SIZED / UNDER-SPECIFIED
```

**Anti-pattern:** If RD outputs "nothing to delete" — INVALID. Redo persona RD (don't reset plan review). After 2 retries still INVALID → output 🟨 RD UNABLE TO FIND DELETIONS — escalation to Senior Manager and SM self-judges.

---

### STEP 3 — CROSS-EXAMINATION

After 4 personas complete, identify real tension between 2 personas (not agreement).
Run 1 round of short exchange — each side must use data/logic from the vault scan, not opinion.

Format:
```
[DA → OR]: "..."
[OR → DA]: "..."

or

[DEV → DA]: "..."
[DA → DEV]: "..."

or

[OR → DEV]: "..."
[DEV → OR]: "..."

or

[RD → DA]: "..."
[DA → RD]: "..."

or

[RD → OR]: "..."
[OR → RD]: "..."

or

[RD → DEV]: "..."
[DEV → RD]: "..."
```

Maximum 2 exchanges. Stop when tension is clearly identified or resolved.
If no CRITICAL blockers differ between personas → output `No structural tension found` and skip straight to Step 4. Don't force exchanges when there's no real tension.

**v3.0 addition:** If Step 1C flagged CRITICAL CONTRADICTION, cross-examination MUST include at least 1 exchange about that contradiction — even if personas agree. Vault history contradictions must not be skipped.

---

### STEP 4 — SENIOR MANAGER VERDICT

Senior Manager manages all 4 personas above. No favoritism toward any persona. No favoritism toward Warren's original plan.
Read the entire debate + vault scan + vault history, deliver the final verdict.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PLAN REVIEW VERDICT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DECISION: 🟢 APPROVE / 🟡 APPROVE WITH CONDITIONS / 🔴 REJECT

REAL PROBLEM CONFIRMED: [YES — plan solves the correct root problem] /
                         [NO — plan solves a symptom, not the root cause]

VAULT HISTORY      : [n precedents found] — [ALIGNED / CONFLICTING / NO PRECEDENT]
                     [If CONFLICTING:]
                     ⚠️ PAST DECISION: [source — 1-sentence summary]
                        RESOLUTION: [plan changed to align / past decision superseded because: ...]

VAULT IMPACT      : [+n new files] / [+n entries into existing file] / [no change]
PROLIFERATION RISK: NONE / LOW / HIGH — [1-sentence reason]
DELETION YIELD    : [n components removed by RD] — [% plan reduced]

BLOCKERS RESOLVED : n/[total raised]
UNRESOLVED RISKS  : [list — only those without answers]

CONDITIONS: (if APPROVE WITH CONDITIONS — max 3, specific)
  1. [specific change — not vague]
  2. ...
  3. ...

OPEN QUESTIONS: (only appears if there are truly ambiguous points — skip this section if the plan is clear)
  [Question] → RECOMMENDED: [answer] | No-friction: [1 sentence] | Long-term: [1 sentence] | Trade-off: [1 sentence]

CONFIDENCE: [HIGH / MOD / LOW] — [1-sentence reason]

SUGGESTED NEXT STEP: [1 single action — what Warren does next]

HYBRID PLAN NOTE: (only appears if at least 1 persona raised a MEDIUM+ blocker related to automation logic)
  → "Automation part has an uncovered blocker: [blocker name] — run /review-workflow for further review."
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**APPROVE** = Real Problem confirmed, 0 CRITICAL blockers, proliferation risk NONE/LOW, vault history ALIGNED or NO PRECEDENT
**APPROVE WITH CONDITIONS** = has blockers but with specific fix — list max 3. Or vault history CONFLICTING but with specific resolution.
**REJECT** = Real Problem wrong OR has CRITICAL blocker that can't be resolved OR vault history CONFLICTING without valid resolution → propose alternative immediately

---

**DELETION YIELD rule:** DELETION YIELD = count from RD's final DELETE list after Senior Manager concurrence. SM only overrides if specifically disagreeing with each DELETE and stating the reason clearly.

### AFTER APPROVE — SPEC BLOCK (mandatory if trigger met)

**Trigger** — auto-fire if at least 1 of 2:
- APPROVE WITH CONDITIONS has ≥ 1 condition, OR
- Plan has > 3 components

If trigger met → Hermes **must** append Spec block into `memory/project_[name].md` in the same session:

```
## Spec (approved YYYY-MM-DD)
Problem     : [1 sentence — confirmed Real Problem]
Approach    : [Senior Manager verdict summary — 2-3 sentences]
Constraints : [list conditions from APPROVE WITH CONDITIONS — or NONE]
History     : [vault precedents referenced — or NO PRECEDENT]
Status      : PLANNING
Next        : [1 specific action Hermes or Warren does at the start of the next session]
Steps       : (see below if complex)
```

**Rules:**
- `project_[name].md` = memory file for this feature. If it doesn't exist → Hermes creates a new file with standard frontmatter + Spec block, and appends 1 index line to `MEMORY.md`.
- `Status` always starts as `PLANNING`. Hermes updates to `CODING` when starting to write code, `DONE` when `/review-code` SHIP.
- `Next` must be actionable — not "continue building" but "write parser X" or "run /review-code for file Y".
- If APPROVE (no conditions) AND plan ≤ 3 components → **don't** create Spec block. Feature is small enough to complete in 1 session.
- **Implementation Steps (auto — no friction for Warren):** If plan affects >3 files OR has complex logic (multi-step parser, cross-file dependencies) → Hermes auto-appends steps to Spec block, doesn't ask Warren:
  ```
  Steps:
    1. [specific file/function] — [what to do]
    2. [specific file/function] — [what to do]
    3. ...
  ```
  Hermes self-judges complexity. Warren doesn't need to do anything — just reads if desired.

### AFTER APPROVE — AUTO-IMPLEMENT (auto-switch to Code)

Immediately after creating Spec block (or if Spec block not needed — immediately after APPROVE verdict):

→ Hermes **auto-switches to Code mode**: `switch_mode(mode_slug="code", reason="/review-plan APPROVE — implementing [feature name] per approved spec")`

→ Start implementing immediately — create/edit files per Spec, **don't need Warren to confirm again**.

**Rules:**
- Warren's only confirmation point = pasting the plan at the start of the session. After APPROVE, Hermes auto-continues.
- If APPROVE WITH CONDITIONS → implement conditions first, remaining parts after. Don't ask again.
- If REJECT → stop. Don't auto-implement.
- Warren only intervenes if Hermes goes off track — no need to intervene beforehand.

---

**v3.0 | 2026-06-02 | Added Step 1C: Vault History Scan — vault self-challenges plan using past decisions/lessons/post-mortems. Step 2 vault history reference rule. Step 4 VAULT HISTORY field + auto-escalation. Spec block added History field. All content translated to English (R4 LANGUAGE MANDATE).**
