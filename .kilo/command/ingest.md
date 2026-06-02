---
model: deepseek-obsidian/deepseek-v4-pro
description: "Data ingestion protocol (Validate → Gate 1 → Delta Mode → 8-step Analysis → Gate 2 → ACTION BLOCK → Debate → Gate 3 → Write) adapted for Personal_OS — personal domains (trading, health, family, finance)."
updated: 2026-06-02
---

# /ingest — Ingest Protocol (Personal_OS)
# v4.2 | 2026-06-02
# Personal_OS adaptation — L'Usine-specific domains/stores replaced with personal domains
# v4.0 base: Delta Mode + ACTION BLOCK + Conditional Debate
# v4.2: Removed GATE 0 (Smart Compress) — Gemini compression deprecated. Raw files read directly.

---

## Usage
```
/ingest [filename] [domain]
```

Parameters:
- **[filename]** = file in `personal_vault/30_KNOWLEDGE_BASE/raw/` (without path)
- **[domain]** = `trading` | `health` | `family_gg` | `finance`

---

## VALIDATE (auto — no confirm needed)

Stop immediately if any fail.

- **File exists?** → Check `personal_vault/30_KNOWLEDGE_BASE/raw/[filename]`. NO → `list_files()` to show available files, STOP.
- **Domain valid?** → Must match exactly. NO → list valid domains, STOP.
- **Duplicate?** → `search_files(path="personal_vault/30_KNOWLEDGE_BASE/wiki/[domain]/", regex="source: \"[filename]\"")` in frontmatter. YES → ask Warren: re-ingest? (y/n)
- **Stub check?** → `search_files(path="personal_vault/30_KNOWLEDGE_BASE/wiki/", regex="data_status.*stub", file_pattern="*.md")` across entire wiki for `data_status.*stub`. Exclude `archive/` directory by filtering results. If found → display list:
  ```
  ⚠️ STUB FILES DETECTED — does this data fill any of these stubs?

  [1] name: "[stub name]" | file: [domain/filename] | related: [...]

  Type number (1, 2...) to fill that stub, or "none" to create new wiki page.
  ```
  **Must wait for Warren to type a specific number or "none" — do not accept blank, do not accept y/n.**
  If Warren types a number outside range → re-display list, ask to re-enter. Do not proceed.
  If Warren chooses a valid number:
  - Use that stub file as target (keep frontmatter: name, tags, related)
  - Add/update: `source: "[filename]"`, `last_updated: "[date]"`, remove line `data_status: stub`
  - Fill content body from analysis
  - If stub's domain differs from ingest domain → write to stub's domain folder, use stub's domain in frontmatter
  If Warren types "none" → continue to create new file normally.
  If no stubs found → skip silently, display nothing.

---

## READ + AUTO-FILL

Read full file directly. Never modify raw file.

ORION infers: file type | period | key metrics | page name | contradictions with existing wiki.

---

## ═══ GATE 1 — DATA GATE ═══

*Purpose: Verify file was read correctly before spending tokens on analysis.*

```
📋 DATA GATE — [filename]

Period  : [inferred]
Metrics : [top 3–5 columns that matter]
Wiki    : [domain]/[Page_Name].md

Corrections? Or y to proceed.
```

Wait for Warren. Correct and re-display if needed.

---

## DELTA MODE (auto after Gate 1 — no confirm needed)

*Purpose: Temporal comparison. Each ingest knows what changed vs last period.*

1. From Gate 1, take the inferred `period` (e.g., April 2026) and compute previous period (March 2026).
2. `search_files(path="personal_vault/30_KNOWLEDGE_BASE/wiki/[domain]/", regex="(March|2026-03|202603)")` for files matching EITHER:
   - `source:` frontmatter containing previous period keyword (e.g., "March", "2026-03", "202603"), OR
   - Filename containing previous period pattern (e.g., `*March*`, `*2026_03*`, `*Q1*` for Q2 ingest)
3. If multiple matches → pick the one with latest `last_updated`. If zero matches → set `DELTA_CONTEXT = null`, skip silently.
4. If match found → Read its **Summary** and **Key Insights** sections only (not full analysis).
5. Store as `DELTA_CONTEXT` for use in Steps 1-7. Do NOT display separately.

ORION MUST reference DELTA_CONTEXT in analysis when available:
- Step 1 (Steel Man): "vs [prev period]: [metric] moved from X → Y"
- Step 2 (Real Problems): "this is new vs last period" or "this persists from [prev period]"
- Step 7 (Commitment): KPI table includes prev period column for comparison

**Condition 4 — Delta Mode Monitoring:**
Next `/ingest` run will verify:
1. DELTA_CONTEXT finds previous period correctly (search matches actual wiki file)
2. Analysis references previous period (Step 1 + Step 2 cite comparison)
3. ACTION BLOCK (after Gate 2) outputs 3 concrete actions
4. Debate skips if data routine (no new problems vs DELTA_CONTEXT)

---

## ANALYZE — 8-STEP CRITICAL THINKING

**PRE-ANALYSIS: ESTIMATE BLIND**
Form independent read from this file only. State raw read explicitly. THEN cross-reference CONTEXT.md.
If divergence → lead with divergence, not confirmation.

Tag every factual claim:
`[HIGH]` = verified in file | `[MOD]` = reasonable inference | `[LOW]` = assumption | `[UNKNOWN]` = insufficient data

---

**Step 1 — Steel Man**
Strongest reading of the data. State confidently — uncertainty lives in the tag, not in softening language.

**Step 2 — Real Problems**
What does this data reveal that current operating assumption misses?
- Short-term: [what changes immediately] `[tag]`
- Long-term: [consequence over 3–12 months] `[tag]`
- The dependency this finding bets on: [what must be true for analysis to hold] `[tag]`

**Step 3 — Hardest Question**
The single uncomfortable question Warren is probably avoiding. Must be specific.
Wrong: "Will we have budget?" Right: "If portfolio drawdown hits 20% but income stays at floor, does this strategy solve the structural problem or delay it?"
State directly. Do NOT soften.
If Warren pushes back without new data → hold it: *"No new data in the pushback. Question stands: [restate]"*

**Step 4 — Two Concrete Alternatives**

**ALTERNATIVE A:** [Approach]
- How: [1–2 sentences] `[tag]`
- Effort: [short-term cost] `[tag]`
- Impact: [long-term benefit] `[tag]`
- When to use: [scenario]

**ALTERNATIVE B:** [Approach]
- How: [1–2 sentences] `[tag]`
- Effort: [short-term cost] `[tag]`
- Impact: [long-term benefit] `[tag]`
- When to use: [scenario]

**Step 5 — Ruthless Evaluation**
Run each gate on proposals from Steps 1–4:
1. Root cause? (does this address cause, not symptom)
2. Evidence? (specific numbers from this file or same-period wiki)
3. Actionable? (can be executed in 30/90 days)
4. Impact-sized? (cost/benefit proportionate)
5. Honest risk? (failure mode named)

If any gate fails → flag which, ask: *"Revise to close failing gates? [y/n]"*
If yes → revise Steps 1–4, re-display. If no → continue.

**Step 6 — Cross-domain Synthesis**
Check same-period wiki pages in OTHER domains. Surface combined signals only if data exists.
Example: Trading P&L↓ + Health✅ + Finance✅ → trading is the real problem, not health/finance.
If no same-period data → skip silently. Do not speculate.

**Step 7 — ORION's Commitment**
Auto-fill from data only (no speculation):
- Tracking plan: [specific metric] → [owner] → [review date]
- Next ingest trigger: [what data would update this analysis]

Output: 70% qualitative (why / so what) + 30% quantitative evidence.

---

## ═══ GATE 2 — ANALYSIS GATE ═══

*Purpose: Validate quality of thinking before decision. Warren checks logic, not decides action.*

```
📊 ANALYSIS GATE — [filename]

[Display Steps 1–7 output]

Analysis solid? y / [correction] / hold
```

Wait for Warren. Revise and re-display if needed. Hold under pushback without new data.

---

## ACTION BLOCK (auto after Gate 2 — mandatory output)

*Purpose: Actionables upfront. Warren sees what to DO before reading full analysis.*

Immediately after Gate 2 approval, output:

```
⚡ TOP 3 ACTIONS (from this data)
1. [action verb + specific target] — [owner] — [deadline or trigger]
2. [action verb + specific target] — [owner] — [deadline or trigger]
3. [action verb + specific target] — [owner] — [deadline or trigger]
```

Rules:
- Actions must come from Steps 1-5 findings. No generic advice.
- Each action must be executable within 30 days.
- Owner = specific person (Warren, family member name), not "team".
- This block is written into the wiki page immediately after Summary, before full analysis.

---

## DEBATE TRIGGER CHECK (auto — decides if debate fires)

Check these 3 conditions from the analysis just completed:

1. Step 2 Real Problems identifies a **newly emerged** problem — NOT present in DELTA_CONTEXT (previous period). If no delta available, treat any `[HIGH]` Real Problem as new.
2. Step 3 Hardest Question challenges a current operating assumption in CONTEXT.md
3. Step 5 Ruthless Evaluation has ≥1 gate failure

**If ANY condition is TRUE → fire full Debate Panel below.**
**If ALL conditions are FALSE → skip debate.** Output:
```
💤 DEBATE SKIPPED — routine data, no decision point detected.
Proceeding to Gate 3.
```

---

## DEBATE PANEL (fires only when triggered above)

3 roles argue from data in THIS ingest + same-period wiki ONLY. No speculation.

- **Trader** → P&L, risk/reward ratio, position sizing, drawdown limits only.
- **Health Coach** → biomarkers, consistency trends, recovery metrics, sleep quality only.
- **Life Strategist** → time allocation, priorities balance, 12-month trajectory. Must frame time horizon (30-day / 90-day / 12-month). Never resolves tension.

Rules:
- Tension MUST exist. If all 3 agree → debate is invalid, escalate until genuine conflict.
- Every argument cites a specific number from this ingest or wiki.
- Role borrowing another role's metric → invalid, restart that role.

```
Option A: [action] → Cost: [X effort/capital] | Upside: [+Y%] | Risk: [failure mode]
Option B: [action] → Cost: [X effort/capital] | Upside: [+Y%] | Risk: [failure mode]

Your call? A / B / hold
```

Warren's A/B choice feeds into Step 8 and the wiki page. "hold" = pause, no write.

**Step 8 — ORION's Commitment** (auto-fills after Warren's call)
- Tracking plan tied to Warren's chosen option
- Next ingest trigger: [what data would update this analysis]

---

## ═══ GATE 3 — ACTION GATE ═══

*Purpose: Final sanity check before permanent write.*

```
⚡ ACTION GATE

Write  : wiki/[domain]/[Page_Name].md
Commit : "Ingest: [filename] → [domain]/[Page_Name] | [date]"

Proceed? y / n
```

Wait for Warren. n = discard (raw file untouched).

---

## WRITE + COMMIT (automatic after Gate 3 approval)

**Wiki page:** `personal_vault/30_KNOWLEDGE_BASE/wiki/[domain]/[Page_Name].md`

YAML frontmatter:
```yaml
---
name: "Page Title"
domain: "[domain]"
type: "analysis | reference | tracking"
status: "active"
last_updated: "YYYY-MM-DD"
source: "[filename]"           # REQUIRED — raw source file triggering this ingest
tags: ["tag1", "tag2"]
related: ["Related_File.md"]
---
```

Body template (this order):
1. **Summary** — 2-3 sentences, what this data says
2. **⚡ Actions** — TOP 3 ACTIONS block (from ACTION BLOCK step above)
3. **Key Insights** — bullet points, each with confidence tag
4. **Δ vs Previous Period** — delta comparison table (omit section if DELTA_CONTEXT was null)
5. **Supporting Data** — key tables/numbers from source file
6. **Full 8-step Analysis** — Steps 1-7 with confidence tags
7. **Debate** — debate panel output (omit section if debate was skipped)
8. **Cross-References** — related wiki pages

Rules: Do NOT overwrite existing files. Name conflict → append `_v2`, flag to Warren.

**Update index:** `wiki/WIKI_INDEX.md` → add row to the correct domain table (name, period, type, key insights).

**Update log:** `wiki/log.md` → append `[date] | /ingest [filename] | [domain]/[Page_Name] | [1-line finding]`.

**[[Links]] injection:** After writing wiki file, check `related:` frontmatter. If it has values → append `## Related` section at end of file with `[[stem_name]]` for each entry in related[]. Format:
```
## Related

- [[File_Name_Without_Extension]]
- [[Another_File]]
```
Obsidian Graph View reads these [[links]] to render the graph. No need to run manual scripts.

**WIKI_GRAPH reminder:** Count how many /ingest runs in this session. If ≥ 3 → after commit, remind Warren: "Ingested [n] files — run `/rebuild-index --graph` to update WIKI_GRAPH for accurate /query."

**Git commit (run from personal_vault/ directory):**
```
cd c:/Users/khoans/Documents/Personal_OS/personal_vault
git add 30_KNOWLEDGE_BASE/wiki/[domain]/[Page_Name].md
git add 30_KNOWLEDGE_BASE/wiki/index.md
git add 30_KNOWLEDGE_BASE/wiki/log.md
git commit -m "Ingest: [filename] → [domain]/[Page_Name].md | [date]"
```

---

## FINAL REPORT

```
✅ INGEST COMPLETE

📄 File   : [filename]
📝 Page   : [domain]/[Page_Name].md
🔗 Commit : [hash]
⏱️ Time   : [X]s

⚠️ [Warnings if any — name conflict, etc.]
```

---

**v4.2 | 2026-06-02 | Personal_OS adaptation — L'Usine domains/stores replaced with personal domains (trading, health, family_gg, finance). Debate panel roles adapted to personal contexts.**
**Flow: Validate → Gate 1 → Delta Mode → 8-step Analysis → Gate 2 → ACTION BLOCK → Debate (conditional) → Gate 3 → Write**
