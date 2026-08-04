---
name: personal-weekly-connections
description: "Weekly cross-domain connections synthesis for Personal_OS vault — scan 11+ sources, identify connections across domains (legal, family_gg, finance, health, trading, meta), assign signal types, write to weekly_connections_log.md, update metadata, log activity, commit."
version: 1.0
tags: [personal_os, weekly, cross-domain, synthesis, connections]
---

# /personal-weekly-connections — Weekly Cross-Domain Connections

## Purpose
Quét toàn bộ vault mỗi Chủ Nhật → phát hiện cross-domain connections (kết nối giữa các lĩnh vực tưởng chừng riêng biệt) → viết vào `10_PULSE/weekly_connections_log.md` → feed insights vào `/personal-context-update` sáng Thứ 2.

**Trigger:** Cron job Chủ Nhật 01:00 (hoặc on-demand bằng `/personal-weekly-connections`)

## Protocol — 3-phase execution

### Phase 1: Scan (quét 11+ nguồn)

| # | Source | Path | What to look for |
|---|--------|------|------------------|
| 1 | Daily_Pulse | `10_PULSE/Daily_Pulse.md` | 5 bullets (GG, Health, Money, Mind, People) — last 7 days |
| 2 | CONTEXT.md | `00_CORE_LOGIC/CONTEXT.md` | Current snapshot, open decisions, health baseline |
| 3 | _inbox/01_unprocessed/ | `_inbox/01_unprocessed/` | Pending items not yet processed |
| 4 | _cases/active/ | `_cases/active/` | Open case threads, follow_up dates, timeline |
| 5 | log.md | `30_KNOWLEDGE_BASE/wiki/log.md` | Daily cron activity, flags, recent ingests |
| 6 | Sleep Log | `10_PULSE/051_Sleep_Log.md` | Sleep metrics, weight, BP, fasting trends |
| 7 | Health Log | `10_PULSE/050_Health_Log.md` | Health metrics, lab results, doctor notes |
| 8 | VNStock Weekly | `10_PULSE/020_VNStock_Weekly_Outlook.md` | VN-Index, sector flow, watchlist |
| 9 | VNStock Macro | `10_PULSE/021_VNStock_Macro.md` | Macro news, policy changes, global events |
| 10 | Candidates Watchlist | `30_KNOWLEDGE_BASE/wiki/03_Investing/VN_Equities/Candidates_Watchlist.md` | Current tickers, entry signals, catalysts |
| 11 | Weekly Synthesis | `10_PULSE/Weekly_Synthesis.md` | Prior week's permanent knowledge extraction |

### Phase 2: Analyze — Identify connections

Look for these 4 signal types:

| Signal | Color | Meaning | Example |
|--------|-------|---------|---------|
| **Critical gap** | 🔴 | Missing data that blocks decision-making across domains | Legal outcome unknown → blocks GG access + child support + burn rate |
| **Correlation** | 🟡 | Two domains moving together without clear causality | Sleep quality drops same week as market selloff |
| **Contradiction** | 🟡 | Tension between domains pulling in opposite directions | Catalysts stacking but capital blocked by 0-month EF |
| **Amplification** | 🟢 | Signal in one domain reinforces opportunity in another | PVD catalysts stacking (oil + Sư Tử Trắng + FTSE) |

**Domains:** legal, family_gg, finance, health, trading, meta, relationship

Each connection MUST have:
- A clear title (conclusion-first)
- Specific evidence with file paths (Obsidian wikilinks)
- Domains involved (use `↔` separator)
- Signal type with W25→W26 comparison

### Phase 3: Write

#### 3a. Prepend to `weekly_connections_log.md`

Entry format (exact — copy from W26 entry):
```markdown
## 2026-W26 (22/06–28/06)

| # | Connection | Domains | Evidence | Signal |
|---|---|---|---|---|
| 1 | **{Title}** — {1-2 sentence conclusion-first description}. Evidence bullets separated by `—`. | domain1 ↔ domain2 | [`path/file.md`](../path/file.md) (key facts); [other source]() | 🔴 Signal — W25→W26: **STATUS** |
| ... | ... | ... | ... | ... |

**📊 Stats:** N connections | N domains involved (domain1, domain2, ...)

**🔗 Most connected domain:** domainX (appears in N of N connections)

**🔄 Previous week comparison:**
| Connection | W{N} status | W{N+1} change |
|---|---|---|
| #1 ({short name}) | 🟡 Status | **CHANGE** — description |

**💡 Feed into /personal-context-update (Monday):**
1. **[HIGH/MOD] {Title}** — 1-sentence action item.
```

#### 3b. Update frontmatter metadata
- `last_updated: <today>` (YYYY-MM-DD)
- `entries: <count>` (total sections, increment by 1)

#### 3c. Update `30_KNOWLEDGE_BASE/wiki/log.md` (ACTIVITY_LOG deprecated)
Prepend new date section under `## YYYY-MM-DD`:
```
|| Time | Action | File | Summary |
||------|--------|------|---------|
|| 01:00 | update | [`10_PULSE/weekly_connections_log.md`](../10_PULSE/weekly_connections_log.md) | /personal-weekly-connections cron: added W{NN} ({date range}) — N connections, N domains. Key: {top 5 findings in 1 line each}. |
```
#### 3d. Git commit
```bash
git add 10_PULSE/weekly_connections_log.md
git commit -m "feat(meta): /personal-weekly-connections W{NN} ({dates}) — N cross-domain connections"
```

## Source files (canonical paths)
- `10_PULSE/weekly_connections_log.md` — target file (growing, newest on top)
- `30_KNOWLEDGE_BASE/wiki/log.md` — activity log (canonical; `_kilo/ACTIVITY_LOG.md` retired with Kilo Code 2026-07-09)
- `_cases/active/legal_divorce_court_GG_access.md` — legal case (common connection source)

## Pitfalls / Lessons from 5 runs (W22→W26)

1. **Daily_Pulse gap common** — Warren often stops Daily_Pulse during stressful periods (legal, family). Sleep log (051) may still be active. Cross-reference both; don't assume Daily_Pulse gap = no health data.
2. **Legal outcome is highest-priority data gap** — When court case is OPEN, the outcome overrides everything. Flag it as #1 connection until resolved.
3. **Weight tracking** — Warren's weight stable 63kg, any deviation ±2kg in <5 days is anomalous and warrants a connection. Cross-reference with fasting hours (18h vs 17h).
4. **MSCI/FTSE upgrade narrative** — These are recurring macro catalysts. Track phase (Frontier→EM timeline, FTSE Sep 21 upgrade, 4-drawdown schedule).
5. **0-month EF is structural blocker** — Every capital deployment connection must reference this constraint. Don't recommend entry without flagging it.
6. **Inbox may be empty** — If auto-process cron (process-notes) ran first, inbox items are cleared. Check log.md for what was processed.
7. **Git diff shows unrelated changes** — 051_Sleep_Log.md may appear modified (by capture-sleep cron). Only stage `weekly_connections_log.md` for the commit.

## Related Skills
- `personal-process-notes` — daily inbox processing (runs before this weekly cron)
- `personal-vault-lint` — vault health check (reads same sources for red-flags)
- `capture-sleep` — sleep log capture (maintains 051, key health data source)
- `stock-capture` — stock analysis capture (maintains trading pulse files)

## Support files
- `references/source-list.md` — canonical source list with paths and scan priorities

## MANDATORY VERIFY GATE (rule: never trust LLM, verify everything)

After EVERY parser run that reads Excel/CSV/PDF ([DOMAIN: weekly synthesis (cross-domain)]), MUST run verify-parser-output gate BEFORE reporting numbers or committing.

1. Independent recompute (fresh script, different method).
2. Cross-assert EVERY number (giá, P&L, room, %Δ, số dư, headcount) vs LLM output.
3. Category-drop scan: count raw rows vs filtered; flag dropped (mã rỗng, dòng tổng, Loc=NaN).
4. Emit VERIFY_RESULT: PASS|FAIL + dropped count. Temp hermes-verify-*.py, clean after.
5. FAIL → LLM wrong until proven. Fix logic, re-run, re-verify.
