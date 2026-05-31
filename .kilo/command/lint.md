---
model: deepseek-obsidian/deepseek-v4-pro
description: "Personal vault linting protocol — scan Personal_OS wiki for stale pages, orphans, frontmatter gaps, contradictions. Adapted for personal domains: family, trading, health, finance."
---

# Lint Protocol — Slash Command (Personal OS)
# v1.0 | 2026-05-31
# Adapted from L'Usine lint v4.0 for Personal_OS vault structure

## Purpose
Scan Personal_OS vault for data quality issues: stale pages, orphaned files, contradictions, missing cross-references, frontmatter gaps.

## Usage
```
/lint [scope] [--quick]
```

**Examples:**
```
/lint all
/lint all --quick
/lint trading
/lint family_gg
```

## Parameters
- **[scope]** = all (entire wiki) | domain (trading, family_gg, health, finance, relationship, growth)
- **[--quick]** = skip slower checks (B1 phantom index, D orphan detection). Runs C + E only.

## Prerequisites

Before running /lint, ensure FRONTMATTER_CACHE.json is populated:
```
python scripts/build_frontmatter_cache.py
```
(pwd: personal_vault/)

If cache is empty or scripts don't exist, ORION falls back to LLM manual lint mode (read cache directly, no scripts).

---

## Steps ORION Will Execute

### 1. READ CACHE + RUN SCRIPTS (if available)
- Read 30_KNOWLEDGE_BASE/wiki/FRONTMATTER_CACHE.json
- If cache empty or >3 days old: rebuild via build_frontmatter_cache.py (if exists)
- Run mechanical checks via lint_mechanical.py (if exists)
- **LLM fallback:** if scripts missing/fail, do manual analysis from cache file

---

### 2. DETECT ISSUES (Hybrid)

**Severity levels:**
- RED Critical — data integrity broken. Blocks next ingest.
- YELLOW Warning — quality degradation. Fix this sprint.
- BLUE Info — improvement opportunities.

**Script-handled checks (B/C/D/E):**
- B: Status Inconsistencies — phantom index entries, archived pages still listed, stale active
- C: Stale Data — last_updated >30d (analysis/tracking) or >90d (reference)
- D: Orphaned Pages — zero inbound [[wikilinks]] (excl. hubs/index/archived)
- E: Frontmatter Gaps — missing domain/type/status/last_updated

**LLM-handled checks (A/F/G):**
- A: Contradiction Flags — explicit flagged-contradiction tag only
- F: Missing Cross-References — 3+ domain keywords without link
- G: Ingest Candidates — raw/ files, closed cases, pulse patterns

---

### 3. COMPILE REPORT

Format:
```
# Lint Report — Personal OS
Date: YYYY-MM-DD | Domain(s): [scope] | Pages scanned: [N]
Summary: RED [N] | YELLOW [N] | BLUE [N]
```

Follow sections: A (Contradictions), B (Status Inconsistencies), C (Stale Data), D (Orphans), E (Frontmatter Gaps), F (Cross-References), G (Ingest Candidates).

---

### 4. SHOW WARREN + OFFER AUTO-FIX

Show report, then:
- y = approve all auto-fixes (frontmatter gaps, index cleanup)
- [list] = specify which
- n = log only

### 5. EXECUTE APPROVED FIXES

### 6. SAVE REPORT
Output: _kilo/lint/lint_[YYYY].md (rolling, newest on top)

### 6B. UPDATE LOG
Append entry to 30_KNOWLEDGE_BASE/wiki/log.md

### 7. COMMIT
From personal_vault/ directory.

---

## Rules
- Never delete pages — only flag for archival
- Never auto-fix content — only mechanical gaps
- Stale threshold: 30d analysis/tracking, 90d reference
- Contradiction = explicit tag only
- Cache first, LLM fallback
- RED issues block next ingest

---

**v1.0 | 2026-05-31 | Personal_OS adaptation. Domains: trading, family_gg, health, finance, relationship, growth. Script-optional mode.**