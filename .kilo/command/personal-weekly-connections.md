---
model: deepseek-obsidian/deepseek-v4-pro
description: "Weekly cross-domain connections for Personal OS. ORION reads 10 personal sources, finds correlations across trading/health/family/finance, writes to rolling log."
updated: 2026-06-02
---

# /personal-weekly-connections — Weekly Cross-Domain Connections (Personal OS)
# v1.0 | 2026-05-31
# PURPOSE: Every Sunday, ORION scans 10 personal sources -> find cross-domain patterns -> write rolling log.
# SCHEDULE: Calendar recurring Sun 17:00 GMT+7
# COMPLEMENT: /personal-context-update (Mon 7AM) — connections feed into context themes.

---

## USAGE

```
/personal-weekly-connections
```

No arguments. ORION reads 10 sources automatically.

---

## PROTOCOL

### Step 1 — Read 10 sources (silent)

Read with a correlation lens, not urgency lens.

Source availability: if source doesn't exist or is empty -> skip, note in internal notes.

| # | Source | What to look for |
|---|--------|-----------------|
| 1 | _growth/_INDEX.md | Knowledge captured this week — any insight linking 2+ personal domains |
| 2 | _cases/active/*.md | Cases that may explain life metric changes |
| 3 | 10_PULSE/Daily_Pulse.md | Most recent entries — flags spanning multiple personal domains |
| 4 | _kilo/ACTIVITY_LOG.md | Files created/modified this week |
| 5 | 10_PULSE/* | All pulse logs — co-movement between trading/health/finance |
| 6 | 30_KNOWLEDGE_BASE/wiki/** | Wiki pages created/modified — insight relevant to current pulse |
| 7 | 00_CORE_LOGIC/SYSTEM_VIEW.md | KPI trends — any metric moving opposite to expectation |
| 8 | _ideas/ | New ideas connecting to existing cases/metrics |
| 9 | 00_CORE_LOGIC/CONTEXT.md | Section 9 — themes showing cross-domain effects |
| 10 | 10_PULSE/weekly_connections_log.md | Previous week's connections — continuing pattern? |

### Step 2 — Find connections (4 signal types)

| Signal | What to look for | Priority |
|--------|-----------------|----------|
| Correlation | 2 metrics moving together (same/opposite) same week | RED Highest |
| Causality hint | 1 case/event appears to explain 1 metric anomaly | YELLOW Medium |
| Contradiction | 2 sources say opposite things about same topic | YELLOW Medium |
| Amplification | 1 issue appears in 3+ independent sources | GREEN Lower |

### Step 3 — Write to rolling log

Write directly to 10_PULSE/weekly_connections_log.md. Newest on top.

Format:
```
## YYYY-WXX (DD/MM-DD/MM)

| # | Connection | Domains | Evidence | Signal |
|---|---|---|---|---|
| 1 | [1-line desc] | trading <-> health | [source], [source] | RED Correlation |

**Stats:** [N] connections | [M] domains
**Most connected domain:** [domain]
**Feed into /personal-context-update Monday:** [1-2 connections to elevate]
```

### Edge case: No connections
```
## YYYY-WXX (DD/MM-DD/MM)

No significant cross-domain patterns this week.
```

### Step 4 — Cross-reference with CONTEXT.md
Mention which connections should be considered for Monday's /personal-context-update.

---

## RULES

1. Don't fabricate connections — if no real pattern, say "none found".
2. Minimum 1 meaningful connection — don't force weak connections.
3. Trace to source — each connection needs 2 evidence links from 2 different domains.
4. Don't duplicate /personal-context-update — this is serendipity engine, not prioritization.
5. Write directly to log — no need to wait for Warren confirm.
6. Signal tag required — every connection must have RED/YELLOW/GREEN type.
7. Compare with last week — if same connection appears 2 weeks running, note "Week 2 — becoming a pattern".
8. Source availability — if source missing/empty, skip and note.

---

**v1.0 | 2026-05-31 | Personal_OS adaptation. Domains: trading, health, family_gg, finance, relationship, growth. Sources aligned with Personal_OS vault structure.**