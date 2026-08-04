---
name: personal-context-update
description: "Weekly personal context update for CONTEXT.md Section 9 — scan 11+ vault sources, synthesize up to 3 themes from past 7 days, auto-update CONTEXT.md, log, commit. Cron: Mon 07:00."
version: 2.0
tags: [personal_os, weekly, context, update, cron]
---

# /personal-context-update — Weekly Personal Context Update

## Purpose
Mỗi sáng Thứ Hai lúc 07:00 — quét 11+ nguồn từ 7 ngày trước → tổng hợp tối đa 3 themes → auto-update `00_CORE_LOGIC/CONTEXT.md` Section 9 → log → commit.

**Khác với `/personal-weekly-connections` (cùng scan 11 nguồn, Chủ Nhật):** /personal-context-update là **synthesis downstream** — output 3 themes ngắn gọn cho Section 9, không đi sâu vào cross-domain signal types. /personal-weekly-connections output 5 connections + signal types vào weekly_connections_log.md.

**Trigger:** Cron job Thứ Hai 07:00 (không interactive — auto-write)

## Protocol — Execute sequentially

### Step 1: Scan 11+ sources (past 7 days)

| # | Source | Path | What to read |
|---|--------|------|-------------|
| 1 | Daily_Pulse | `10_PULSE/Daily_Pulse.md` | 5-bullet entries, last 7 days — GG, Health, Money, Mind, People |
| 2 | CONTEXT.md §9 | `00_CORE_LOGIC/CONTEXT.md` | Current Section 9 themes (for comparison — what changed?) |
| 3 | CONTEXT.md §6, §7, §11 | Same file | Financial snapshot, open decisions, thinking patterns |
| 4 | Cases (active) | `_cases/active/*.md` | All OPEN cases, `follow_up` dates, timeline |
| 5 | wiki/log.md | `30_KNOWLEDGE_BASE/wiki/log.md` | Daily cron activity, flags, ingests — last 7 days |
| 6 | Sleep Log | `10_PULSE/051_Sleep_Log.md` | Sleep metrics, weight, BP, fasting trends |
| 7 | Health Log | `10_PULSE/050_Health_Log.md` | Health metrics, lab results |
| 8 | Weekly Connections (latest) | `10_PULSE/weekly_connections_log.md` | **Critical:** read W{prev} entry — the "Feed into /personal-context-update" section is your PRIMARY input |
| 9 | Inbox unprocessed | `_inbox/01_unprocessed/` | Pending items not yet processed |
| 10 | Git log | `git log --oneline --after="7 days ago"` | All vault activity in past week |
| 11 | Candidates Watchlist | `30_KNOWLEDGE_BASE/wiki/03_Investing/VN_Equities/Candidates_Watchlist.md` | Current entry signals, price vs IV |

**⚠️ Source not found / empty:** skip, note `⚠️ [source]: unavailable` internally. Do not block.

### Step 2: Synthesize up to 3 themes

From 11 sources + the weekly_connections_log "Feed into" list, distill **3 most important themes** for Section 9.

Selection criteria (priority order):
1. **🔴 Critical gap** — missing data blocking decisions across domains (e.g. legal outcome unknown paralyzing GG access + child support + burn rate)
2. **Threshold breach** — health metric anomalous (weight drop 2kg in <5 days, BP spike, LDL persisting unaddressed)
3. **Deadline approaching** — case `follow_up` date within next 7 days
4. **Catalyst stacking** — multiple positive signals converging (FTSE upgrade, LDR easing, oil prices)
5. **Pattern continuing from last week** — note "PERSISTS + INTENSIFIES / WORSENS / IMPROVED"

**Use the weekly_connections_log "Feed into" section as primary input.** The connections log already did the heavy scanning. Elevate its top-3 recommendations.

Each theme maps to one row:
| # | Current question | What I'm reading/researching | Decision needed |
|---|---|---|---|
| 🏛️ | **{Sharp question}** | {Evidence + context + trend vs last week} | {Concrete action} |
| 🏥 | **{Health question}** | {Metrics, anomalies, gaps} | {What to do} |
| 🏦 | **{Trading question}** | {Catalysts, watchlist, blockers} | {What conditions must be met} |

Theme order: 🏛️ (legal/family) > 🏥 (health) > 🏦 (trading) > other. **🔴 Critical first.**

### Step 3: Update CONTEXT.md

#### 3a. Update frontmatter
```yaml
last_updated: YYYY-MM-DD
```

#### 3b. Replace Section 9

Replace entire table under `## 9. THIS WEEK`. Update the note line:
```
> **Update:** Every Monday morning. Hermes reads 11 data sources from past 7 days, synthesizes up to 3 themes. **Last updated: YYYY-MM-DD (W{NN}: {date range}).** 7-day scan: {N} git commits, {N} vault files modified, {other notable activity}.
```

Keep the table format intact — 4 columns, 3 rows (one per theme). Use conclusion-first phrasing. Each "What I'm reading/researching" cell must include specific file paths when referencing source data.

### Step 4: Log to wiki/log.md

Prepend a new entry under `## YYYY-MM-DD`:
```markdown
## YYYY-MM-DD
- **UPDATE: CONTEXT.md Section 9** via `/personal-context-update` cron. Synthesized 3 themes: (1) 🏛️ {short}; (2) 🏥 {short}; (3) 🏦 {short}.
```

### Step 5: Log to wiki/log.md (ACTIVITY_LOG deprecated)

Prepend under existing `## YYYY-MM-DD` section in `30_KNOWLEDGE_BASE/wiki/log.md`:
```markdown
|| 07:00 | update | [`00_CORE_LOGIC/CONTEXT.md`](../00_CORE_LOGIC/CONTEXT.md) | /personal-context-update cron: updated Section 9 W{NN} ({dates}) — 3 themes: {short}, {short}, {short}. |
```

### Step 6: Git commit

```bash
git add 00_CORE_LOGIC/CONTEXT.md 30_KNOWLEDGE_BASE/wiki/log.md
git commit -m "feat(context): /personal-context-update W{NN} ({dates}) — 3 themes: {summary}"
```

## Edge cases

### Skill missing / not found
If this skill itself is not found (symptom: cron scheduler logs `skill not found, skipping`):
- Reconstruct from: (1) last successful cron output file in `cron/output/{id}/{date}.md`, (2) the weekly_connections_log "Feed into" section, (3) direct source scan
- Flag in log.md: `⚠️ Skill personal-context-update missing — reconstructed from previous run + W{N} feed`
- Output still gets written — don't skip the cron job just because the skill is missing

### Nothing notable to report (quiet week)
If the week was genuinely quiet (no new cases, no health anomalies, no trading catalysts, weekly connections feed empty):
```
This week is stable. No notable new themes beyond what's already being tracked in Section 9.
Keep current Section 9 as-is.
```

### Weekly connections not yet run
If it's Monday 07:00 and weekly_connections_log shows only W{prev} (no W{current}), run without the feed. Scan sources directly. Flag: `⚠️ Weekly connections W{NN} not yet run — scanning sources directly.`

## Pitfalls / Lessons from 2 runs (W25→W26)

1. **Legal case outcome is #1 priority until resolved** — Phiên tòa 17/6 outcome unknown was the dominant theme across W25→W26→W27+. Track days since last update. Format: "12 NGÀY không update."
2. **Weight deviation ±2kg in <5 days is anomalous** — Warren's stable baseline is 63kg. Weight 61kg from 24/6 flagged as health theme. Cross-reference with fasting hours (18h vs 17h).
3. **Sleep improvement can mask other health degradation** — Paradox pattern: sleep avg 7h35 quality 88.6 improving ≠ overall health improving. LDL/ApoB unaddressed, workout = 0. Flag this paradox when it appears.
4. **FTSE EM upgrade (Sep 21) is persistent catalyst** — This is a confirmed date (~2 tỷ USD passive). Track countdown. Every catalyst-stacking theme should reference it.
5. **0-month emergency fund is structural blocker** — Capital deployment recommendations must reference this constraint. Don't advise entry without flagging "but 0 EF + child support unknown = capital blocked."
6. **CONTEXT.md §9 must compare W{prev}→W{current}** — Each theme should note whether it persists, worsens, improved, or is new. Format: `W25→W26: **PERSISTS + WORSENS** (đã 12 ngày).`
7. **Git diff may show unrelated changes** — Another cron (capture-sleep, process-notes) may have modified files between your scan and commit. Use explicit `git add` (not `git add -A`).

## Relationship with /personal-weekly-connections

| Dimension | /personal-weekly-connections (Sun 01:00) | /personal-context-update (Mon 07:00) |
|-----------|------------------------------------------|--------------------------------------|
| Output | `weekly_connections_log.md` (5 connections) | `CONTEXT.md §9` (3 themes) |
| Depth | Cross-domain signal types (🔴🟡🟢) | Single-row themes with action items |
| Format | Table with evidence, domains, signal, comparison | Table with question, reading, decision |
| Dependency | Independent | Consumes connections "Feed into" section |
| Narrative | Detailed analysis | Conclusion-first executive summary |

## Source files (canonical paths)
- `00_CORE_LOGIC/CONTEXT.md` — target file (Section 9)
- `10_PULSE/weekly_connections_log.md` — primary input (latest entry's "Feed into" section)
- `30_KNOWLEDGE_BASE/wiki/log.md` — activity log target (canonical; `_kilo/ACTIVITY_LOG.md` retired with Kilo Code 2026-07-09)

## Related Skills
- `personal-weekly-connections` — runs Sunday, feeds into this skill Monday morning
- `personal-process-notes` — daily inbox processing (may have processed items before this runs)
- `capture-sleep` — sleep log capture (maintains 051, key health data source)
- `personal-vault-lint` — vault health check (reads same sources for red-flags)

## MANDATORY VERIFY GATE (rule: never trust LLM, verify everything)

After EVERY parser run that reads Excel/CSV/PDF ([DOMAIN: CONTEXT.md update (state, priorities)]), MUST run verify-parser-output gate BEFORE reporting numbers or committing.

1. Independent recompute (fresh script, different method).
2. Cross-assert EVERY number (giá, P&L, room, %Δ, số dư, headcount) vs LLM output.
3. Category-drop scan: count raw rows vs filtered; flag dropped (mã rỗng, dòng tổng, Loc=NaN).
4. Emit VERIFY_RESULT: PASS|FAIL + dropped count. Temp hermes-verify-*.py, clean after.
5. FAIL → LLM wrong until proven. Fix logic, re-run, re-verify.
