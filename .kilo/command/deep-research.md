---
model: deepseek-obsidian/deepseek-v4-pro
description: "Deep-dive research assistant. ORION reads all relevant vault knowledge (wiki, pulse logs, cases, journal, raw) to answer a specific question with structured memo — What We Know, Suspect, Don't Know. Inline output, no auto-wiki."
updated: 2026-06-02
---

# /deep-research — Deep Research (Personal_OS)
# v1.0 | 2026-06-02
# Personal_OS adaptation of /ops-deep-research v1.0
# PURPOSE: Warren asks a deep question → ORION reads all relevant vault knowledge → structured research memo. On-demand, no schedule.

---

## USAGE

```
/deep-research [question]
```

**Examples:**
```
/deep-research sleep quality trend Q1 2026
/deep-research VNStock portfolio performance from launch to now
/deep-research health metrics correlation with trading performance
/deep-research family spending trend last 3 months
/deep-research learning log — which skills am I investing in vs using?
```

---

## GATE 0 — NARROW-DOWN (mandatory, before reading)

Before reading anything, evaluate the question:

| Check | Action if FAIL |
|-------|---------------|
| **Topic scope** — covers ≤2 domains? | Ask Warren: "This question spans [N] domains. Which domain do you want to focus on most?" |
| **Time scope** — has time boundary? | If vague ("since the beginning"), suggest: "I suggest focusing on [last 3 months / Q1 2026 / since launch]. OK?" |
| **Domain scope** — specifies domain? | If too broad, narrow: "Do you want to focus on trading, health, family, or finance?" |

If question is narrow enough (≤2 domains, time boundary clear) → proceed to Step 1 immediately. Do not ask for the sake of asking — only narrow when genuinely too broad.

---

## PROTOCOL

### Step 1 — Parse question (silent)

Extract:

```
TOPIC      : [1-line summary]
DOMAINS    : [trading | health | family_gg | finance]
TIME RANGE : [YYYY-MM to YYYY-MM | "since launch" | "last N months"]
QUESTION   : [sharpened version — what exactly is Warren asking?]
```

### Step 2 — Read relevant sources (silent)

Based on DOMAINS + TIME RANGE parsed in Step 1. Read selectively — not all sources every time:

| # | Source | When to read | What to look for |
|---|--------|-------------|-----------------|
| 1 | `personal_vault/30_KNOWLEDGE_BASE/wiki/[domain]/**` | Always | All wiki pages in matching domain(s). Cross-ref WIKI_INDEX.md first. |
| 2 | `personal_vault/10_OPERATION_DATA/` | If TIME RANGE matches log dates | Daily_Pulse log, Health_Log, weekly_connections_log |
| 3 | `personal_vault/_cases/active/*.md` + `_cases/closed/**` | If topic touches case subject | Cases matching topic keywords |
| 4 | `personal_vault/_journal/YYYY-MM.md` | If TIME RANGE covered | Journal entries mentioning topics |
| 5 | `personal_vault/30_KNOWLEDGE_BASE/raw/*` | If quantitative question | Raw CSVs matching domain (e.g., VNStock_Weekly_Outlook for trading, health trackers for health) |
| 6 | `personal_vault/00_CORE_LOGIC/CONTEXT.md` | Always (light read) | Current context — any related decisions? |

**⚠️ Source availability:** If source doesn't exist or is empty → skip, note `⚠️ [source_name]: unavailable` in internal notes. Do not block flow.

### Step 3 — Synthesize research memo

4 mandatory sections:

```
# 🧠 Deep Research: [original question]

**Research date:** YYYY-MM-DD
**Domains:** [list]
**Time range:** [range]

---

## 📊 What We KNOW [HIGH]
*(Findings backed by ≥2 independent sources or hard data)*

- [finding 1] → source: [wiki link], [log link]
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

| Case / Decision | Domain | Follow-up | Relevance |
|---|---|---|---|
| [case name] | [domain] | YYYY-MM-DD | [1-line why related] |

*(If none → "No active cases directly related.")*

---

## 📎 Sources Read

- [list all files read, with confidence tag if source has caveat]
```

### Step 4 — Save gate

After output, ask exactly once:

```
Save this research to wiki?

If yes → I'll create a wiki page in `personal_vault/30_KNOWLEDGE_BASE/wiki/[domain]/` with standard frontmatter.
If no → this research exists only in chat. Nothing saved.
```

**If Warren says yes:**
- Create file: `personal_vault/30_KNOWLEDGE_BASE/wiki/[domain]/DeepResearch_[topic_slug]_YYYY-MM-DD.md`
- Frontmatter:
  ```yaml
  ---
  domain: [domain]
  tags: ["deep-research", "YYYY-MM"]
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
7. **Source availability** — if source doesn't exist/is empty → skip + note `⚠️ [source_name]: unavailable`.
8. **Raw data READ ONLY** — reading raw/ is allowed, writing is not.

---

## Anti-patterns

- ❌ Reading all sources when only 2-3 are needed → check relevance first
- ❌ SUSPECT mixed into KNOW → wrong confidence tag leads Warren to wrong decisions
- ❌ Gaps left empty or written as "none" → there are always gaps
- ❌ Auto-creating wiki file without asking → must go through Step 4 save gate
- ❌ Overly aggressive narrow-down → only narrow when genuinely too broad (≥3 domains, no time boundary)
