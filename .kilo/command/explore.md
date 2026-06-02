---
model: deepseek-obsidian/deepseek-v4-pro
description: "Idea intake & impact filter adapted for ORION+Deepseek toolchain. ORION reads vault, self-answers 3 questions, self-verdicts."
updated: 2026-06-02
---

# /explore — Idea Intake & Impact Filter
# v1.3 | 2026-05-31
# OPTIMIZATION: Cache-first YAML reads (Condition 2)
# PURPOSE: Filter raw ideas BEFORE /review-plan. ORION reads vault, self-answers, self-verdicts.
# Warren doesn't need to formulate plan upfront — just dump raw ideas.
# POSITION IN WORKFLOW: Idea -> /explore -> (GO) /review-plan or /review-workflow -> code -> /review-code

---

## Usage

```
/explore [raw idea — 1 sentence, 1 link, or 1 pain point]
```

**Auto-trigger (no need for Warren to type /explore):**
- Warren pastes link from X / LinkedIn / blog
- Warren says "I have an idea", "I found this article interesting", "should I pursue this"
- Warren asks about a new habit, tool, or process not yet in the vault

**Do not trigger when:** mid-flow in another skill (/ingest, /review-plan,
/review-code, /process-notes, /morning-brief, /cases, /query, /triage).

---

## Core Principle (no exceptions)

ORION is the primary worker — not Warren.
- ORION reads vault -> self-answers 3 questions -> self-verdicts
- Warren only corrects if ORION reads vault data INCORRECTLY
- Warren CANNOT override verdict with opinion/feeling
- If Warren pushes back without vault evidence -> ORION restates
  evidence and keeps verdict: *"No new vault data in the pushback.
  Verdict stands: [restate]"*

---

## STEP 1 — CLASSIFY + VAULT READ (silent, mandatory before everything)

No guessing. No memory usage. Read actual files.

**Trivial check (before reading vault):**
ORION self-asks: "Is this request a modification of something existing, not creating a new feature?"

Trivial = fix/update existing content: typo, number, date, 1-line edit, delete line.
NOT trivial = add feature, create new file, build automation, idea from outside vault.

If trivial -> output 1 line: `"Trivial edit — proceeding directly."` then execute immediately, do not run Q1/Q2/Q3.
If not trivial -> continue reading vault per domain map below.

**CACHE-FIRST READ (Condition 2 optimization + Condition 3 error handling):**

1. Check `30_KNOWLEDGE_BASE/wiki/FRONTMATTER_CACHE.json`:
   ```
   try {
     cache = load + parse FRONTMATTER_CACHE.json
     if cache._schema missing or cache.data missing -> throw
     if cache._total_files < 10 -> log "⚠️ Cache incomplete" but continue
     use cache (5-8 files -> 1 cached read)
   } catch {
     log "cache unavailable" (silent)
     fallback to explicit file reads below
   }
   ```
   - If file exists + valid JSON -> skip file reads, scan cache instead
   - If file missing, JSON corrupt, or schema invalid -> fallback to explicit file reads (silent, no error to Warren)

**Read map by idea domain (fallback / if cache missing):**

| Idea domain | Files to read |
|---|---|
| Trading / Portfolio | CONTEXT.md + 30_KNOWLEDGE_BASE/wiki/trading/ (scan all files) + 10_PULSE/pulse_trading.md (last entry) |
| Health / Wellness | CONTEXT.md + 30_KNOWLEDGE_BASE/wiki/health/ (scan all files) + 10_PULSE/health_log.md (last entry) |
| Family / GG | CONTEXT.md + 30_KNOWLEDGE_BASE/wiki/family_gg/ (scan all files) + _cases/active/ (scan for family-related) |
| Finance / Budget | CONTEXT.md + 30_KNOWLEDGE_BASE/wiki/finance/ (scan all files) + _tasks/ + 10_PULSE/pulse_finance.md |
| Growth / Knowledge | CONTEXT.md + _growth/_INDEX.md + WIKI_INDEX.md |
| IT / Automation / Vault | CONTEXT.md + _inbox/tasks.md + AGENTS.md + last 3 entries in _kilo/ACTIVITY_LOG.md |
| warren_os / Personal OS Arch | CONTEXT.md + _inbox/tasks.md + ORION.md + 30_KNOWLEDGE_BASE/wiki/ (scan all dirs) + _kilo/memory/ (scan project files) + WIKI_INDEX.md |
| Unknown / Mixed | CONTEXT.md + _inbox/tasks.md + HOME.md + WIKI_INDEX.md (scan for duplicates) |

---

## STEP 2 — SELF-ANSWER 3 QUESTIONS (from vault data, no speculation)

ORION self-asks and self-answers. Each answer must cite specific file/data.

**Q1 — Block: If we don't build this, is Warren truly blocked?**

Answer with vault evidence:
- Truly blocked -> cite file + metric + specific gap
- Not blocked -> cite file that already covers, explain why not needed

**Q2 — Duplicate: Does the vault already have something covering this?**

Answer from vault scan:
- Already exists -> list file(s) + explain overlap
- Does not exist -> confirm real gap

**Q3 — Maintenance Cost: If built, how many minutes per month does it cost?**

Real estimate based on:
- Number of files needing periodic updates
- Parser/automation available or manual?
- Who updates (Warren or Claude)?

---

## STEP 3 — LIGHTWEIGHT CHECK

If idea scope is clearly small (1 file, 1 field, 1 line edit):
-> Skip Q3 (maintenance trivially low for small changes). Run Q1 + Q2.
-> Q1 ALWAYS mandatory even for lightweight — this is the main filter.
-> Faster verdict.

ORION self-judges scope. If unsure -> run full 3 questions.

---

## STEP 4 — VERDICT (ORION self-decides, does not ask Warren)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXPLORE VERDICT — [idea summary 1 sentence]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Q1 Block       : [REAL / NOT REAL] — [evidence from vault]
Q2 Duplicate   : [NONE / PARTIAL / FULL] — [file(s) if any]
Q3 Maintenance : [~X min/month] — [breakdown]

VERDICT: 🟢 GO / 🔴 NO-GO

GO   : "[Problem statement 1 sentence] | KPIs: [2-3 measurable metrics]
        -> Proceed with /review-plan"
NO-GO: "[Specific reason from Q1/Q2/Q3 — not opinion]
        -> Do not build. [Alternative if any]"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**NO-GO criteria (any 1 of 3):**
- Q1: no real block (vault already covers or no pain point)
- Q2: vault already has file covering >70% scope
- Q3: maintenance >30 min/month with low value (judgment call)

**GO criteria (all 3 must pass):**
- Q1: real block, with evidence
- Q2: vault does not have or real gap
- Q3: maintenance reasonable relative to value

---

## STEP 5 — GO: AUTO-GENERATE PLAN + PIPE TO REVIEW (only when GO)

Warren does not write the plan. ORION does it all.

**ORION self-executes immediately after GO verdict:**

1. Generate plan from explore findings:
   ```
   Plan: [feature/fix name]
   Problem: [from Q1 vault evidence]
   Approach: [solution approach — 2-3 sentences]
   Scope: [affected files/components]
   KPIs: [2-3 measurable metrics]
   ```

2. Classify scope:
   - Data/vault/structure -> auto-run `/review-plan [plan just generated]`
   - IT/automation/workflow -> auto-run `/review-workflow [plan just generated]`

3. Run review immediately in the same session — do not ask Warren first.

**Warren has only 2 stop points in the entire flow:**
- After /explore VERDICT: correct if Claude read vault data wrong
- After /review-plan APPROVE: confirm "y" before Claude starts coding

---

## Anti-patterns

- ❌ Read memory instead of actual vault
- ❌ Answer Q1/Q2/Q3 with general knowledge — must cite vault file
- ❌ Capitulate when Warren pushes back without vault evidence
- ❌ GO just because idea "sounds good" — must have real block
- ❌ Trigger when mid-flow in another skill
- ❌ Skip vault read because "already read earlier" — each /explore re-reads

---

## Example NO-GO pattern

Q1 NOT REAL + Q2 PARTIAL -> NO-GO: "No real block. [File X] already covers. -> Do not build. Alternative: [quick suggestion]"

---

**v1.3 | 2026-05-31 | ORION+Deepseek adaptation — agent name + frontmatter**
