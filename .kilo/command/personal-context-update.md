---

description: "Weekly context update for CONTEXT.md Section 5. ORION reads 10 sources from past 7 days, drafts up to 3 themes, waits for Warren's confirm before writing."
updated: 2026-06-02
---

# /ops-CONTEXT-update — Weekly Context Update (L'Usine Ops)
# v1.0 | 2026-05-27
# PURPOSE: Every Monday morning, ORION proactively synthesizes the past week → draft Section 5 → wait for Warren confirm → write CONTEXT.md.
# SCHEDULE: Calendar recurring Mon 7:00 AM GMT+7 → Warren triggers `/ops-CONTEXT-update`

---

## USAGE

```
/ops-CONTEXT-update
```

No arguments. ORION reads 10 sources automatically.

---

## PROTOCOL

### Step 1 — Read 10 sources (silent)

| # | Source | What to read |
|---|--------|-------------|
| 1 | `_journal/YYYY-MM.md` | Entries from last 7 days |
| 2 | `_cases/active/*.md` | All OPEN cases + `follow_up` dates |
| 3 | `10_OPERATION_DATA/morning_briefs/morning_briefs_log.md` | 2-3 most recent briefs |
| 4 | `_kilo/ACTIVITY_LOG.md` | Files created/modified in last 7 days |
| 5 | `10_OPERATION_DATA/*_Log.md` | All pulse logs: Revenue (01), HR (02), COGS (03), LTO (04), Reviews (05), GrabFood (06), COL (07), Incident (08) |
| 6 | `30_KNOWLEDGE_BASE/wiki/**` | Wiki pages created/modified in last 7 days (cross-ref with ACTIVITY_LOG) |
| 7 | `00_CORE_LOGIC/SYSTEM_VIEW.md` | 4-week KPI trends |
| 8 | `_ideas/YYYY-MM.md` | New ideas / competitor intel |
| 9 | `00_CORE_LOGIC/CONTEXT.md` | Current Section 5 (for comparison — what changed?) |
| 10 | `10_OPERATION_DATA/weekly_connections_log.md` | Latest week's cross-domain connections from Sunday — any pattern to elevate? |

**⚠️ Source availability:** If source doesn't exist or is empty → skip, note `⚠️ [source_name]: unavailable` in internal notes. Do not block flow.

### Step 2 — Synthesize up to 3 themes

From the 10 sources, extract the **3 most important themes** Warren should focus on this week.

Selection criteria (in priority order):
1. **Deadline pressure** — case `follow_up` date within next 7 days
2. **Threshold breach** — any KPI exceeding red/yellow threshold in SYSTEM_VIEW or pulse logs
3. **Pattern repetition** — same issue appearing in 2+ independent sources
4. **New decision required** — something surfaced in journal/wiki that needs Warren's call

Each theme maps to one row in the Section 5 table:

| Column | Source |
|--------|--------|
| Concerned question | Distill the theme into one sharp question |
| Currently reading/researching | Link to wiki page, article, or source file |
| Decision needed | Concrete action — what decision is needed this week? |

### Step 3 — Present draft to Warren

```
📝 DRAFT — CONTEXT.md Section 5 (week [YYYY-MM-DD])

I've read 10 sources in the past 7 days. 3 notable themes:

| # | Concerned question | Currently reading/researching | Decision needed |
|---|---|---|---|
| 1 | [question] | [source] | [action] |
| 2 | [question] | [source] | [action] |
| 3 | [question] | [source] | [action] |

📂 Sources scanned: journal (X entries), cases (Y active), briefs (Z),
   pulse logs (8 domains), wiki (N pages), ideas, SYSTEM_VIEW
🔗 Cases needing attention this week: [case names with follow_up dates]

→ Confirmed?
```

**Wait for Warren's response.** Do NOT write anything until confirmed.

### Step 4 — After confirm

Warren says "Ok" or provides edits → write to `00_CORE_LOGIC/CONTEXT.md`:
- Update `last_updated` in frontmatter to today
- Replace Section 5 table with confirmed version
- Update "Last updated" note

### Edge case: Nothing notable

If the week was quiet (no new cases, no threshold breaches, no patterns):
```
📝 DRAFT — CONTEXT.md Section 5 (week [date])

This week is relatively stable. No notable new themes beyond what's already being tracked.

Recommendation: keep current Section 5 as-is. Want to add/remove anything?
```

---

## RULES

1. **Do not auto-write** — always wait for Warren's confirm before touching CONTEXT.md.
2. **Data-driven, not guessing** — each theme must trace back to at least 1 specific source among the 10 sources.
3. **Max 3 themes, min 1** — if the week only has 1-2 themes with [HIGH/MOD] data, don't force a 3rd theme. This is focus, not a laundry list.
4. **Compare old vs new** — if a theme already existed in last week's Section 5 and is still active, note "continues from last week".
5. **Confidence tag** — each theme tagged with [HIGH/MOD/LOW] confidence.
6. **If nothing new** → say so directly, don't fabricate.
