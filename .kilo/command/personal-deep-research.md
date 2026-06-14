---

description: "Deep-dive research assistant. Hermes reads all relevant vault knowledge (wiki, pulse logs, cases, journal, raw) to answer a specific question with structured memo — What We Know, Suspect, Don't Know. Inline output, no auto-wiki."
updated: 2026-06-02
---

# /ops-deep-research — Deep Research (L'Usine Ops)
# v1.0 | 2026-05-27
# PURPOSE: Warren asks a deep question → Hermes reads all relevant vault knowledge → structured research memo. On-demand, no schedule.
# NOT: /ops-pulse (snapshot), /ops-context-update (weekly synthesis), /review-plan (evaluate plan), /ops-weekly-connections (cross-domain patterns)

---

## USAGE

```
/ops-deep-research [question]
```

**Examples:**
```
/ops-deep-research LU5 labour cost trend Q1 2026
/ops-deep-research GrabFood ROI per store from launch to now
/ops-deep-research cold brew revenue LU3 vs LU7
/ops-deep-research competitor landscape — who's opening near LU3?
/ops-deep-research beverage COGS trend LU5 vs LU7 last 3 months
```

---

## GATE 0 — NARROW-DOWN (mandatory, before reading)

Before reading anything, evaluate the question:

| Check | Action if FAIL |
|-------|---------------|
| **Topic scope** — covers ≤2 domains? | Ask Warren: "This question spans [N] domains. Which domain do you want to focus on most?" |
| **Time scope** — has time boundary? | If vague ("since the beginning"), suggest: "I suggest focusing on [last 3 months / Q1 2026 / since launch]. OK?" |
| **Store scope** — specifies stores? | If "all L'Usine", narrow: "Do you want to compare all 3 stores or focus on 1?" |

If question is narrow enough (≤2 domains, time boundary clear, stores specified) → proceed to Step 1 immediately. Do not ask for the sake of asking — only narrow when genuinely too broad.

---

## PROTOCOL

### Step 1 — Parse question (silent)

Extract:

```
TOPIC      : [1-line summary]
DOMAINS    : [labour_costs | menu_cogs | marketing_growth | lto_tracker | P&L_Budget | customer_experience | lusine_operations | SOP_POLICY_LUSINE]
STORES     : [LU3] [LU5] [LU7] [ALL]
TIME RANGE : [YYYY-MM to YYYY-MM | "since launch" | "last N months"]
QUESTION   : [sharpened version — what exactly is Warren asking?]
```

### Step 2 — Read relevant sources (silent)

Based on DOMAINS + TIME RANGE + STORES parsed in Step 1. Read selectively — not all 7 sources every time:

| # | Source | When to read | What to look for |
|---|--------|-------------|-----------------|
| 1 | `30_KNOWLEDGE_BASE/wiki/[domain]/**` | Always | All wiki pages in matching domain(s). Cross-ref WIKI_INDEX.md first. |
| 2 | `10_OPERATION_DATA/*_Log.md` | If TIME RANGE matches log dates | Revenue (01), HR (02), COGS (03), LTO (04), Reviews (05), GrabFood (06), COL (07), Incident (08) |
| 3 | `_cases/active/*.md` + `_cases/closed/**` | If topic touches case subject | Cases matching topic keywords |
| 4 | `_journal/YYYY-MM.md` | If TIME RANGE covered | Journal entries mentioning stores/topics |
| 5 | `30_KNOWLEDGE_BASE/raw/*` | If quantitative question | Raw CSVs matching domain (e.g. payroll CSV for labour, COGS CSV for menu) |
| 6 | `00_CORE_LOGIC/CONTEXT.md` | Always (light read) | Current Section 5 — any related decisions? |
| 7 | `00_CORE_LOGIC/SYSTEM_VIEW.md` | If time-sensitive | Current KPI trends — relevant context |

**⚠️ Source availability:** If source doesn't exist or is empty → skip, note `⚠️ [source_name]: unavailable` in internal notes. Do not block flow.

### Step 3 — Synthesize research memo

4 mandatory sections:

```
# 🧠 Deep Research: [original question]

**Research date:** YYYY-MM-DD
**Domains:** [list]
**Stores:** [list]
**Time range:** [range]

---

## 📊 What We KNOW [HIGH]
*(Findings backed by ≥2 independent sources or hard data)*

- [finding 1] → source: [wiki link], [pulse log link]
- [finding 2] → source: [case link], [raw CSV]

*(If none → "Not enough data for any HIGH-confidence finding.")*

---

## 🔍 What We SUSPECT [MOD/LOW]
*(Patterns visible but insufficient data / single source / contradictory)*

- [pattern 1] [MOD] — [why not HIGH] → source: [source]
- [pattern 2] [LOW] — [why low confidence]

*(If none → "No suspect patterns worth noting.")*

---

## ❓ What We DON'T Know (Gaps)
*(Missing data, unanswered questions — equally important as findings)*

- [gap 1] — missing data [specific: which file, which metric]
- [gap 2] — no wiki page yet for [topic]
- [gap 3] — follow-up question: [sharp question]

*(Mandatory — never leave empty)*

---

## 📋 Related Active Decisions

| Case / Decision | Store | Follow-up | Relevance |
|---|---|---|---|
| [case name] | [LU3/LU5/LU7] | YYYY-MM-DD | [1-line why related] |

*(If none → "No active cases directly related.")*

---

## 📎 Sources Read

- [list all files read, with confidence tag if source has caveat]
```

### Step 4 — Save gate

After output, ask exactly once:

```
Save this research to wiki?

If yes → I'll create a wiki page in `30_KNOWLEDGE_BASE/wiki/[domain]/` with standard frontmatter.
If no → this research exists only in chat. Nothing saved.
```

**If Warren says yes:**
- Create file: `30_KNOWLEDGE_BASE/wiki/[domain]/DeepResearch_[topic_slug]_YYYY-MM-DD.md`
- Frontmatter:
  ```yaml
  ---
  domain: [domain]
  tags: ["deep-research", "LU3", "LU5", "LU7", "YYYY-MM"]
  related: ["[wiki file 1]", "[wiki file 2]"]
  created: YYYY-MM-DD
  status: active
  ---
  ```
- Content: full research memo from output

**If Warren says no:** Do not create file. End.

---

## RULES

1. **Data-driven, don't fabricate** — each finding must trace back to ≥1 specific source.
2. **Confidence tag mandatory** — [HIGH/MOD/LOW] on every claim.
3. **Gaps section is mandatory** — equally important as findings. "Don't know" is also insight.
4. **Clearly separate KNOW vs SUSPECT** — HIGH = ≥2 independent sources or hard data. MOD/LOW = single source, unconfirmed pattern, contradiction.
5. **Do not auto-create wiki** — output inline. Only create wiki when Warren confirms "save" at Step 4.
6. **Narrow-down before research** — GATE 0 mandatory. Do not read 50 files for an overly broad question.
7. **Use deepseek-reasoner** — this command requires deep reasoning.
8. **Source availability** — if source doesn't exist/is empty → skip + note `⚠️ [source_name]: unavailable`.
9. **Raw data READ ONLY** — reading raw/ is allowed, writing is not.

---

## Anti-patterns

- ❌ Reading all 7 sources when only 2-3 are needed → check relevance first
- ❌ SUSPECT mixed into KNOW → wrong confidence tag leads Warren to wrong decisions
- ❌ Gaps left empty or written as "none" → there are always gaps
- ❌ Auto-creating wiki file without asking → must go through Step 4 save gate
- ❌ Overly aggressive narrow-down → only narrow when genuinely too broad (≥3 domains, no time boundary)
