---
name: explore
description: Ops-feasibility validation — evaluate operational ideas by auditing referenced data sources for existence, recency, and gating factors. Produces a scope assessment with execution order recommendation. Use when Warren asks "check this idea" or you need to validate an ops initiative before planning.
category: ops
tags: ['feasibility', 'validation', 'ops', 'idea']
version: 2.0.0
trigger: Warren says "check", "validate", "review this idea", or asks you to evaluate an operational concept
related_skills: [idea-refine]
---

# /explore — Ops-Feasibility Validation

> Evaluate raw operational ideas by checking what data actually exists.

Unlike `idea-refine` (creative ideation), this skill is about **feasibility validation** — mapping an operational concept to real data sources, identifying gaps, and producing a realistic execution order.

## Process

### Phase 1: Load + Parse

1. **Read the idea file** (usually in `_ideas/` or inline in conversation)
2. **Extract all referenced data sources** — files, sheets, wiki pages
3. **Batch-read every referenced source** in parallel — check:
   - Does the file exist?
   - Is there actual data, or just a template/header?
   - What's the last_updated date?
   - What format is the data in? (per-SKU table? weekly summary? raw log?)
   - Are there existing parsers for this data?

### Phase 2: Assess Each Mảng (Workstream)

For each workstream in the idea, build a table:

| Dimension | What to check |
|-----------|---------------|
| **Existence** | Does the data source file exist? |
| **Recency** | When was it last updated? How many months stale? |
| **Completeness** | Has actual data rows, or just empty template? |
| **Format precedent** | Has a similar analysis been done before (template exists)? |
| **Format gap** | Does source data need transformation before use? |
| **Parser exists?** | Is there a .py parser in `parsers/` for this data? |
| **Gating factor** | What blocks this workstream from being built RIGHT NOW? |

### Phase 3: Gating Factor Analysis

For each workstream, identify:

1. **Data ready now** — can start immediately
2. **Data exists but stale** — needs parser re-run or manual update
3. **Data gated by external party** — e.g., "waiting for CFO P&L mid-month"
4. **Data doesn't exist** — needs manual collection or new pipeline

### Phase 4: Execution Order Recommendation

Rank workstreams by:

1. **Ease** (data ready now vs gated)
2. **Impact** (which unblocks decisions fastest)
3. **Dependency** (does workstream A depend on B?)

Propose 1-mảng/turn execution with rationale.

## Output Format

```
## ✅ Summary

| Mảng | Exists? | Recency | Format | Gating factor | Priority |
|------|---------|---------|--------|---------------|----------|
| ... | ✅/⏳/❌ | date | table/summary/raw | blocker | order |

## Gating Factors

1. [Workstream] — [gating detail + what to unblock]

## Recommended Order

1. → [fastest to ship]
2. → [second]
3. → [most gated]
```

## Example

See session 2026-07-03: Warren said "check vault/_ideas/next_session_complete_visibility.md". Hermes batch-read all 6+ referenced files, found:
- Menu GP% → April data exists but 2 months stale. Format precedent (April 2026 analysis). ✅ Ready but needs update.
- COGS Food/Bar → Supplier swings tracked (T5+T6), but actual COGS% needs P&L from CFO mid-month. ⏳ Gated.
- Channel Economics → GrabFood weekly data complete. Walk-in revenue needs manual split. ✅ Menu first, channel second, COGS last.

## Pitfalls

- **Don't assume files exist just because an idea references them.** Verify by reading the first 5-10 lines.
- **Check not just existence but data recency.** An April analysis in July = stale.
- **Look for existing parsers** — if a parser already pulls this data, don't plan manual work.
- **Check for format precedent** — if a similar analysis was done before (e.g., April 2026 Food COGS), use its format as template. Don't design from scratch.
- **Don't merge dependent workstreams.** If one needs external data (CFO P&L), flag it and start the independent one first.
- **Batch independent reads** — read all referenced files in parallel, not sequentially.
- **Verify EXTERNAL/legal sources LIVE before building on them.** When the user pastes "authoritative" legal/policy quotes (Google ToS, law articles, gov decrees), they are OFTEN hallucinated or point to archived/revoked pages. `mcp_smart_fetch` the actual URL, read the live text, quote the REAL line. Don't build a defense on an unverified paste. (Worked example: a Google GenAI ToS paste claiming "commercial-safe, immune to VCPMC" was actually ARCHIVED 2023; the live Google ToS 22/05/2024 only says "Google won't claim ownership over that content" — no VCPMC immunity. See `ops-legal-compliance` skill.)
