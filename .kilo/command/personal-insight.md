---

description: "Free-form raw data → structured insight protocol (Validate → Read → Gate 1 → WIKI GATE → Delta Mode → 8-step Analysis → Gate 2 → ACTION BLOCK → Debate → Gate 3 → Write) adapted for Hermes+Deepseek toolchain."
updated: 2026-06-02
---

# /ops-insight — Insight Protocol
# v2.0 | 2026-05-26
# Port of /ops-ingest v4.2 for free-form raw data → structured insight
# Key changes v2.0:
#   - WIKI GATE added after Gate 1 — Warren MUST confirm "write wiki?" before 8-step analysis
#   - If Warren says "no" → save raw to journal, skip analysis (no wasted tokens)
#   - GATE 0 (Smart Compress) removed — deprecated with /ingest v4.2
# Flow: Validate → Read → Gate 1 → WIKI GATE → (yes) Delta Mode → 8-step Analysis → Gate 2 → ACTION BLOCK → Debate (conditional) → Gate 3 → Write

---

## Usage
```
/ops-insight [domain] [optional: title_or_reference]
```

Parameters:
- **[domain]** = `lusine_operations` | `labour_costs` | `menu_cogs` | `marketing_growth` | `lto_tracker` | `P&L_Budget` | `customer_experience` | `SOP_POLICY_LUSINE` | `archive/personal_os/*`
- **[title_or_reference]** = optional — short name for the insight (if blank, Hermes infers from content)

**Input modes (Hermes auto-detects):**
1. Warren pastes raw data inline (text, numbers, table, CSV, notes)
2. Warren references a file: `30_KNOWLEDGE_BASE/raw/[filename]` or any vault path
3. Warren says an idea/observation/lesson in conversation — Hermes captures it
4. Warren provides a URL or external reference

**Auto-trigger (no need to type /insight):**
- Warren says "remember this", "note this", "take note", "this insight"
- Warren shares a significant observation or lesson learned
- BUT: do not trigger if mid-flow of another skill

---

## VALIDATE (auto — no confirm needed)

Stop immediately if any fail.

### A — Detect input type
Determine how Warren provided the raw data:

| Signal | Type | Action |
|--------|------|--------|
| Warren pastes data in the same message or next message | `inline_text` | Use directly |
| Warren says "file [path]" or references a known vault file | `vault_file` | Read file from vault |
| Warren just says `/insight [domain]` with no data yet | `pending` | Ask: "What data/insight do you want me to process?" |
| Warren says an insight directly (e.g., "LU3 morning peak is consistently understaffed") | `conversation` | Use the statement as raw input |

If `pending` → ask Warren to provide data. Do NOT proceed without data.

### B — Domain valid?
Must match exactly. NO → list valid domains, STOP.

### C — Duplicate check?
If `title_or_reference` provided → search `wiki/[domain]/` for similar name, source, or key phrase.
YES → ask Warren: "Wiki already has similar entry: [filename]. Create new insight? (y/n)"
NO → continue.

### D — Stub check?
Same logic as `/ops-ingest`:
search_files(path="30_KNOWLEDGE_BASE/wiki", regex="data_status.*stub"). Exclude `archive/`, `finance/`.
If stub found matching domain/keyword → display list for Warren to choose fill.
If Warren selects a stub → fill into stub file instead of creating new.
If Warren types "none" → create new file as normal.
If no stubs found → skip silently.

---

## READ (auto — no confirm needed)

Based on input type:

| Input Type | Action |
|---|---|
| `inline_text` | Read directly from Warren's message. Estimate token count. |
| `vault_file` | Read file via read_file(). |
| `conversation` | Use Warren's statement as the raw data block. |
| `pending` | (Should not reach here — validation would have caught) |

Never modify the source file or original text.

**Auto-infer from content:**
Hermes infers: data type | period (if mentioned) | stores (if mentioned) | key themes | page name | contradictions with existing wiki

---

## ═══ GATE 1 — DATA GATE ═══

*Purpose: Confirm Hermes read/understood the raw data correctly before analysis.*

```
📋 DATA GATE — [inferred_title]

Input type : [inline_text | vault_file | conversation]
Source     : [paste snippet / file path / conversation quote]
Period     : [inferred or "N/A"]
Stores     : [inferred or "N/A"]
Key themes : [top 3 themes from the data]
Wiki       : [domain]/[Page_Name].md

Corrections? Or y to proceed.
```

Wait for Warren. Correct and re-display if needed.

---

## ═══ WIKI GATE ═══

*Purpose: Warren decides if this insight is wiki-worthy BEFORE spending tokens on 8-step analysis.*

```
📝 WIKI GATE — Write this insight to wiki?

Wiki     : [domain]/[Page_Name].md
Summary  : [1-line — what this insight says]

Write to wiki? y / n
```

**Rules:**
- This is the ONLY moment Warren can approve a wiki write outside of /ingest. No other command writes to wiki without asking here first.
- If **y** → proceed to Delta Mode + 8-step Analysis → Gate 2 → Gate 3 → Write wiki page.
- If **n** → save raw data + 1-line summary to `_journal/YYYY-MM.md` under `## /insight — not wiki-worthy`. STOP. Do NOT run 8-step analysis. Do NOT write wiki.

Wait for Warren. **y** = continue analysis. **n** = journal-only, STOP immediately.

---

## DELTA MODE (auto after Wiki Gate "y" — no confirm needed)

*Purpose: Temporal comparison. Each insight knows what already exists in wiki.*

1. If Gate 1 identified a `period` → compute previous period (e.g., "April" → "March").
2. search_files(path="wiki/[domain]/", regex="...") for files matching EITHER:
   - Same period keyword in frontmatter or filename
   - Similar theme/keywords in frontmatter `tags:[]` or `name:`
3. If multiple matches → pick latest `last_updated`. If zero → set `DELTA_CONTEXT = null`, skip.
4. If match found → Read its **Summary** and **Key Insights** sections only.
5. Store as `DELTA_CONTEXT`. Do NOT display separately.

Hermes MUST reference DELTA_CONTEXT in analysis when available:
- Step 1 (Steel Man): "vs [existing insight]: [theme] was [X], now [Y]"
- Step 2 (Real Problems): "this is new" or "confirms [prev insight]"
- Step 7 (Commitment): reference previous entry

---

## ANALYZE — 8-STEP CRITICAL THINKING

**PRE-ANALYSIS: ESTIMATE BLIND**
Form independent read from this data only. State raw read explicitly. THEN cross-reference CONTEXT.md + existing wiki.
If divergence → lead with divergence, not confirmation.

Tag every factual claim:
`[HIGH]` = verified in data | `[MOD]` = reasonable inference | `[LOW]` = assumption | `[UNKNOWN]` = insufficient data

---

**Step 1 — Steel Man**
Strongest reading of this raw data. What does it tell us if we read it most favorably? State confidently — uncertainty lives in the tag.

**Step 2 — Real Problems**
What does this data reveal that current operating assumption (in CONTEXT.md or wiki) misses?
- Short-term: [what changes immediately] `[tag]`
- Long-term: [consequence over 3–12 months] `[tag]`
- Dependency: [what must be true for this insight to hold] `[tag]`

**Step 3 — Hardest Question**
The single uncomfortable question this data raises. Must be specific.
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
2. Evidence? (specific data points)
3. Actionable? (can be executed in 30/90 days)
4. Impact-sized? (cost/benefit proportionate)
5. Honest risk? (failure mode named)

If any gate fails → flag which, ask: *"Revise to close failing gates? [y/n]"*
If yes → revise Steps 1–4, re-display. If no → continue.

**Step 6 — Cross-domain Synthesis**
Check same-period or same-theme wiki pages in OTHER domains. Surface combined signals only if data exists.
If no same-period data → skip silently.

**Step 7 — Hermes's Commitment**
Auto-fill from data only (no speculation):
- Insight value: [1-sentence — what makes this worth keeping]
- Actionable implication: [what should Warren DO with this insight]
- Related wiki pages: [existing pages this connects to]
- Next trigger: [what data/event would validate/update this insight]

---

## ═══ GATE 2 — ANALYSIS GATE ═══

*Purpose: Validate quality of thinking before decision.*

```
📊 ANALYSIS GATE — [Page_Name]

[Display Steps 1–7 output]

Analysis solid? y / [correction] / hold
```

Wait for Warren. Revise and re-display if needed. Hold under pushback without new data.

---

## ACTION BLOCK (auto after Gate 2 — mandatory output)

Immediately after Gate 2 approval, output:

```
⚡ TOP 3 ACTIONS (from this insight)
1. [action verb + specific target] — [owner] — [deadline or trigger]
2. [action verb + specific target] — [owner] — [deadline or trigger]
3. [action verb + specific target] — [owner] — [deadline or trigger]
```

Rules:
- Actions must come from Steps 1–5 findings. No generic advice.
- Each action must be executable within 30 days.
- Owner = specific person (Warren, store manager name, CFO), not "team".
- This block is written into the wiki page immediately after Summary.

---

## DEBATE TRIGGER CHECK (auto — decides if debate fires)

Check these 3 conditions from the analysis:

1. Step 2 identifies a **newly surfaced** problem — NOT present in DELTA_CONTEXT. If no delta, treat any `[HIGH]` Real Problem as new.
2. Step 3 Hardest Question challenges a current operating assumption in CONTEXT.md
3. Step 5 has ≥1 gate failure

**If ANY condition is TRUE → fire Debate Panel below.**
**If ALL conditions are FALSE → skip debate.** Output:
```
💤 DEBATE SKIPPED — insight confirmed, no decision point detected.
Proceeding to Gate 3.
```

---

## DEBATE PANEL (fires only when triggered above)

3 roles argue from this insight + same-period wiki ONLY. No speculation.

- **Ops Manager** → SPLH + COL% + headcount only. Never use EBITDA.
- **Finance Manager** → EBITDA% + rent coverage + cash flow only. Never use service metrics.
- **CEO** → Google reviews + brand position + 12-month revenue trend only. Must frame time horizon.

Rules:
- Tension MUST exist. If all 3 agree → debate is invalid, escalate.
- Every argument cites a specific number from this insight or wiki.
- Role borrowing another role's metric → invalid, restart.

**Guest Impact Check (mandatory before conclusion):**
"If we act on this, what happens to guest experience in 30 days?"

```
Option A: [action] → Cost: [X VND/month] | Upside: [+Y%] | Risk: [failure mode]
Option B: [action] → Cost: [X VND/month] | Upside: [+Y%] | Risk: [failure mode]
Guest impact: [Which protects CX better — 1 line]

Your call? A / B / hold
```

Warren's A/B choice feeds into the wiki page. "hold" = pause, no write.

---

## ═══ GATE 3 — ACTION GATE ═══

*Purpose: Final sanity check before permanent write.*

```
⚡ ACTION GATE

Write  : wiki/[domain]/[Page_Name].md
Type   : insight | analysis | reference
Commit : "Insight: [Page_Name] → [domain] | [date]"

Proceed? y / n
```

Wait for Warren. n = discard (no write).

---

## WRITE + COMMIT (automatic after Gate 3 approval)

### Wiki page target
`30_KNOWLEDGE_BASE/wiki/[domain]/[Page_Name].md`

### Page name rules
- Prefix: `Insight_` + descriptive name (e.g., `Insight_LU3_Morning_Peak_Staffing`)
- If name conflict → append `_v2`, flag to Warren
- If title_or_reference provided → use that as base name
- If auto-inferred → use the core subject

### YAML frontmatter
```yaml
---
name: "Insight: [Descriptive Title]"
domain: "[domain]"
type: "insight"
status: "active"
source: "[raw data source — 'conversation' | file path | 'Warren personal']"
last_updated: "YYYY-MM-DD"
tags: ["tag1", "tag2", "insight"]
related: ["Related_File.md"]
stores: ["LU3", "LU5", "LU7"]    # optional — only if store-specific
period: "YYYY-MM"                 # optional — only if time-bound
---
```

### Body template (this order):
1. **Summary** — 2–3 sentences, what this insight says
2. **⚡ Actions** — TOP 3 ACTIONS block (from ACTION BLOCK above)
3. **Raw Input** — the original raw data (for traceability)
4. **Key Insights** — bullet points, each with confidence tag
5. **Δ vs Previous** — delta comparison (omit if DELTA_CONTEXT was null)
6. **Full 8-step Analysis** — Steps 1–7 with confidence tags
7. **Debate** — debate panel output (omit if debate was skipped)
8. **Cross-References** — related wiki pages
9. **Tags for Search** — `#domain #insight #[store] #[theme]`

### Update index
`wiki/WIKI_INDEX.md` → find the domain table → add row (name, period="insight", type="insight", key insights)

### Update log
`wiki/log.md` → append `[date] | /insight [Page_Name] | [domain] | [1-line finding]`

### [[Links]] injection
Check `related:` frontmatter. If present → append `## Related` section:
```
## Related

- [[File_Name_Without_Extension]]
- [[Another_File]]
```

### Git commit (execute_command)
```
execute_command(command="git add 30_KNOWLEDGE_BASE/wiki/[domain]/[Page_Name].md", cwd=VAULT_DIR)
execute_command(command="git add 30_KNOWLEDGE_BASE/wiki/index.md", cwd=VAULT_DIR)
execute_command(command="git add 30_KNOWLEDGE_BASE/wiki/log.md", cwd=VAULT_DIR)
execute_command(command="git commit -m \"Insight: [Page_Name] → [domain] | [date]\"", cwd=VAULT_DIR)
```

---

## FINAL REPORT

```
✅ INSIGHT CAPTURED

📄 Page   : [domain]/[Page_Name].md
🔗 Commit : [hash]
⏱️ Time   : [X]s

📝 Summary: [1-line what this insight says]

⚠️ [Warnings if any]
```

---

## Anti-patterns

- ❌ Skip analysis for obvious insights after Wiki Gate "y" — 8-step is mandatory once wiki-worthy. If Wiki Gate = "n", save to journal and skip 8-step entirely.
- ❌ Write to wiki without Gate 3 approval
- ❌ Speculate beyond the raw data provided — `[UNKNOWN]` is valid
- ❌ Overwrite existing wiki pages — append `_v2` instead
- ❌ Skip stub check
- ❌ Treat conversation insights as less important than file-based ones — all insights follow same pipeline
- ❌ Forget to update WIKI_INDEX + log

---

## Examples

### Example 1: Conversation insight
```
Warren: /insight labour_costs
Warren: LU3 morning peak (7-9am) consistently has only 1 FOH + 1 barista.
        But covers are 80-100 in that window. Compared to LU5 which does
        60-80 covers with 2 FOH + 2 barista. Something is off.

Hermes: [Runs Validate → Gate 1 → Wiki Gate (Warren: y) → Delta → 8-step
        → Gate 2 → Action Block → Gate 3 → Write → Commit]

✅ INSIGHT CAPTURED
📄 Page   : labour_costs/Insight_LU3_Morning_Peak_Staffing.md
🔗 Commit : abc1234
```

### Example 2: File-based insight
```
Warren: /insight menu_cogs Toast_COGS_insight
Warren: Read file 30_KNOWLEDGE_BASE/raw/Food_LTO_LU3_Toast_Tracker.xlsx
        and give insight on toast COGS trend.

Hermes: [Runs Read → Gate 1 → Wiki Gate → ...]
```

### Example 3: No explicit command (auto-trigger)
```
Warren: Remember this: LU7 guest complaints about wait time are increasing
        but revenue is holding steady — possibly silent churn.

Hermes: [Auto-detects as insight request → runs full pipeline → asks Warren
        to confirm domain and wiki-gate before analysis]
```

### Example 4: Wiki Gate = "n" (journal-only)
```
Warren: /insight labour_costs
Warren: this month LU3 COL% increased slightly 0.3%, likely just seasonality

Hermes: [Runs Validate → Read → Gate 1]

📝 WIKI GATE — Write this insight to wiki?
Wiki: labour_costs/Insight_LU3_COL_Slight_Increase.md
Summary: LU3 COL% increased 0.3% — likely seasonal, not structural

Warren: n

Hermes: ✅ Saved to _journal/2026-05.md — not wiki-worthy. STOP.
```

---

**v2.0 | 2026-05-26 | Added WIKI GATE after Gate 1 — Warren must confirm before 8-step analysis runs. No wiki write occurs without explicit "y" here. Removed GATE 0 (Smart Compress).**
**Flow: Validate → Read → Gate 1 → WIKI GATE → (y) Delta Mode → 8-step Analysis → Gate 2 → ACTION BLOCK → Debate (conditional) → Gate 3 → Write**
