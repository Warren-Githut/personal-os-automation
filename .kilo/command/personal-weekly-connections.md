---

description: "Weekly cross-domain connection finder. ORION reads 10 sources from past 7 days, finds correlations/causality/contradictions/amplifications across domains, writes to rolling log. Complement to /ops-CONTEXT-update."
updated: 2026-06-02
---

# /ops-weekly-connections — Weekly Cross-Domain Connections (L'Usine Ops)
# v1.0 | 2026-05-27
# PURPOSE: Every Sunday, ORION scans 10 sources → finds cross-domain patterns (serendipity) → writes rolling log.
# SCHEDULE: Calendar recurring Sun 17:00 GMT+7
# COMPLEMENT: /ops-CONTEXT-update (Mon 7AM) — connections feed into context themes.

---

## USAGE

```
/ops-weekly-connections
```

No arguments. ORION reads 10 sources automatically.

---

## PROTOCOL

### Step 0 -- Source of Truth Pre-flight (Critical gate)

**Goal:** Ensure no conflicting sources exist before running connections analysis. Connecting data from 2 conflicting sources produces false insights.

1. Check known duplication patterns (same list as lint Section H):
   - **Tasks:** LUSINE_TODO_Kanban.md vs _inbox/tasks.md -> Kanban is source
   - **Active cases:** _cases/active/ files vs indexes -> files on disk are source
   - **Store KPIs:** CONTEXT.md vs wiki pages -> wiki is source, CONTEXT is snapshot
   - **Recipe data:** raw/recipes/ CSVs vs Recipe_Index.json -> raw CSVs are source
   - **Command registry:** .kilo/command/*.md vs lusine.md -> commands define one each
2. For each pattern where both files exist AND both have content:
   -> ⚠️ Flag as DUPLICATE source of truth
   -> Suggest which file to keep (and why)
3. If ANY duplicates found:
   ```
   ⚠️ SOURCE OF TRUTH CONFLICT FOUND
   [[file_A]] vs [[file_B]]
   Same: [what overlaps]
   Source of truth: [file_A] -- [reason]
   ```
   -> PAUSE. Show to Warren before Step 1.
   -> Wait for Warren to confirm which source to keep.
   -> Apply fix (delete/redirect duplicate), THEN proceed to Step 1.
4. If no duplicates found -> silent pass, proceed to Step 1.

### Step 1 — Read 9 sources (silent)

Same 10 sources as `/ops-CONTEXT-update`, but read with a **correlation lens**, not urgency lens.

**⚠️ Source availability:** If source does not exist or is empty → skip, note `⚠️ [source_name]: unavailable` in internal notes. Do not block flow.

| # | Source | What to look for |
|---|--------|-----------------|
| 1 | `_journal/YYYY-MM.md` | Recurring frustrations, observations linking 2+ topics |
| 2 | `_cases/active/*.md` | Cases that may explain metric anomalies |
| 3 | `10_OPERATION_DATA/morning_briefs/morning_briefs_log.md` | 2-3 most recent briefs — flags that span multiple stores/domains |
| 4 | `_kilo/ACTIVITY_LOG.md` | Files created/modified — any wiki page + pulse log touched same week? |
| 5 | `10_OPERATION_DATA/*_Log.md` | All 8 pulse logs — look for co-movement between metrics |
| 6 | `30_KNOWLEDGE_BASE/wiki/**` | Wiki pages created/modified — any insight relevant to current pulse? |
| 7 | `00_CORE_LOGIC/SYSTEM_VIEW.md` | 4-week KPI trends — any metric moving opposite to expectation? |
| 8 | `_ideas/YYYY-MM.md` | New ideas that connect to existing cases/metrics |
| 9 | `00_CORE_LOGIC/CONTEXT.md` | Current Section 5 — any theme from last Monday now showing cross-domain effects? |
| 10 | `10_OPERATION_DATA/weekly_connections_log.md` | Previous week's connections — any pattern continuing or escalating? |

### Step 2 — Find connections (4 signal types)

| Signal | What to look for | Priority |
|--------|-----------------|----------|
| **Correlation** | 2 metrics moving together (same or opposite direction) in same week | 🔴 Highest |
| **Causality hint** | 1 case/event appears to explain 1 metric anomaly | 🟡 Medium |
| **Contradiction** | 2 sources say opposite things about same topic | 🟡 Medium |
| **Amplification** | 1 issue appears in 3+ independent sources | 🟢 Lower (but notable) |

### Step 3 — Write to rolling log

Write directly to `10_OPERATION_DATA/weekly_connections_log.md`. Newest on top.

Output format:

```markdown
## YYYY-WXX (DD/MM–DD/MM)

| # | Connection | Domains | Evidence | Signal | Feedback |
|---|---|---|---|---|---|
| 1 | [1-line description] | labour ↔ revenue | [source link], [source link] | 🔴 Correlation |
| 2 | [1-line description] | case ↔ CX | [source link] | 🟡 Causality |

**📊 Stats:** [N] connections | [M] domains involved
**🔗 Most connected domain:** [domain name]
**💡 Feed into Monday's /ops-CONTEXT-update:** [1-2 connections worth elevating to theme]
```

### Edge case: No connections

```markdown
## YYYY-WXX (DD/MM–DD/MM)

No notable cross-domain connections this week.
Domains are operating independently, no cross signals.
```

### Step 4 — Cross-reference with CONTEXT.md

After writing, mention which connections (if any) should be considered for Monday's `/ops-CONTEXT-update`:

```
💡 Suggestions for Monday's /ops-CONTEXT-update:
- Connection #2 (causality) could become a theme if not yet resolved
- Connection #1 (correlation) should be monitored another week before elevating
```

---

## Feedback Mechanism

> **Ref:** [[Feedback_Pair_Pattern]] — every auto-output command must have paired feedback loop.

Each connection in the weekly log supports inline feedback markers:
- `<!-- fb:[ACTED] @YYYY-MM-DD -->` — acted on, skip next week
- `<!-- fb:[NOISE] @YYYY-MM-DD -->` — false positive, skip. 2x [NOISE] = permanent skip
- `<!-- fb:[WATCH] @YYYY-MM-DD -->` — monitor, keep showing

**Weekly checkpoint:** Monday `/ops-context-update` includes "Acknowledge connections from Sunday" with batch-mark option.

**Permanent skip rule:** Same connection marked [NOISE] 2 consecutive weeks → ORION auto-skips permanently.

---

## RULES

1. **Do not invent connections** — if no real pattern, say directly "none".
2. **Minimum 1 meaningful connection** — if week is quiet, write "No significant cross-domain patterns this week." Do not force weak connections.
3. **Trace to source** — each connection must have at least 2 evidence links from 2 different domains.
4. **Do not overlap with /ops-CONTEXT-update** — this is a serendipity engine, not prioritization. Do not output "top 3 themes".
5. **Write directly to log** — no need to wait for Warren to confirm (unlike context-update). This is observation, not decision.
6. **Signal tag mandatory** — each connection must have 🔴🟡🟢 signal type.
7. **Compare to previous week** — if same connection appears 2 consecutive weeks, clearly note "🔄 Week 2 — becoming a pattern".
8. **⚠️ Source availability** — if source does not exist or is empty → skip, note `⚠️ [source_name]: unavailable` in internal notes.
