---

description: "Vault linting protocol (hybrid: script + LLM) adapted for ORION+Deepseek toolchain."
updated: 2026-06-02
---

# Lint Protocol — Slash Command
# v4.0 | 2026-05-31
# ORION+Deepseek adaptation — Read→read_file, Write→write_to_file, Grep→search_files, python→execute_command, agent name update

## Purpose
Scan Warren OS vault for data quality issues: stale pages, orphaned files, contradictions, missing cross-references, frontmatter gaps. Categorized by severity so Warren knows what needs immediate attention vs. what's low priority.

**Optimization:** v3.0 uses Script + LLM hybrid architecture. Python scripts handle all mechanical checks (B/C/D/E) by reading `FRONTMATTER_CACHE.json`. LLM only handles judgment calls (A, F, G1/G2/G3). This reduces tool calls from ~88 individual file reads to 1 cache read + 2 script invocations.

## Usage
```
/lint [scope] [--quick]
```

**Examples:**
```
/lint all
/lint all --quick
/lint labour_costs
/lint lusine_operations
```

## Parameters
- **[scope]** = `all` (entire wiki) | domain name (lusine_operations, labour_costs, menu_cogs, marketing_growth, lto_tracker, P&L_Budget, customer_experience, SOP_POLICY_LUSINE)
- **[--quick]** = skip slower checks (B1 phantom index, B3 stale active git, D orphan detection). Runs C + E only.

## Prerequisites

Before running `/lint`, ensure `FRONTMATTER_CACHE.json` is populated:
```
execute_command(command="python scripts/build_frontmatter_cache.py", cwd="vault")
```
If cache is empty, Step 1 will detect this and prompt you to rebuild first.

---

## Steps ORION Will Execute

### 1. READ CACHE + RUN SCRIPTS
- `read_file(path="30_KNOWLEDGE_BASE/wiki/FRONTMATTER_CACHE.json")` (1 tool call — replaces ~88 individual file reads)
- If cache is empty (`_total_files: 0`): `execute_command(command="python scripts/build_frontmatter_cache.py", cwd="vault")` first
- If cache older than 3 days: `execute_command(command="python scripts/build_frontmatter_cache.py", cwd="vault")` to refresh stale cache
- Run mechanical checks: `execute_command(command="python scripts/lint_mechanical.py [--quick] [--domain=SCOPE]", cwd="vault")`
- Parse script output (JSON) for B/C/D/E findings
- LLM fallback: if script fails or Python unavailable, fall back to original manual Step 1 SCAN (read files individually)

---

### 2. DETECT ISSUES (Hybrid: Script + LLM)

**Severity levels:**
- 🔴 **Critical** — data integrity or navigation broken. Requires Warren decision before next ingest.
- 🟡 **Warning** — quality degradation. Should fix within current sprint.
- 🔵 **Info** — improvement opportunities. Fix when convenient.

---

#### Script-handled checks (run automatically via `lint_mechanical.py`):

**B. 🔴 Status Inconsistencies** (Critical) — Script
- B1: Pages listed in `WIKI_INDEX.md` that don't exist on disk (phantom index entries)
- B2: `status=archived` BUT page still listed in `WIKI_INDEX.md`
- B3: `status=active` BUT `last_updated` > 60 days old AND no recent Git commits
- Report: Page name, inconsistency type, suggested fix

**C. 🟡 Stale Data** (Warning) — Script
- Compare `last_updated` from cache to today's date
- Flag if: today − last_updated > 30 days AND status != "archived"
- Exception: `type: reference` → threshold is 90 days
- Report: Page name, last update date, days stale

**D. 🟡 Orphaned Pages** (Warning) — Script
- Scan all wiki `.md` files for `[[wikilinks]]`
- Build inbound link matrix; flag pages with zero inbound links
- Excludes: archived, hubs, index pages
- Report: Page name, domain, git_created date, likely cause

**E. 🟡 Frontmatter Gaps** (Warning) — Script
- Required fields: `name`, `domain`, `type`, `status`, `last_updated`, `source`, `tags`, `related`
- Flag if: any required field is missing from cache entry
- Note: `source` field only → lower priority (pre-v2.0 pages)
- Report: Page name, missing fields

---

#### LLM-handled checks (judgment calls — continue to read files directly):

**A. 🔴 Contradiction Flags** (Critical) — LLM
- Search for explicit `flagged-contradiction` tag in any page body
- Flag if: found
- Report: Page name, quoted contradiction note
- *Do NOT infer contradictions — explicit tag only*

**F. 🔵 Missing Cross-References** (Info) — LLM
- Scan page body for domain-specific terms without corresponding `[[link]]`
- Only flag high-confidence: 3+ domain keywords without link
- Report: Page name, suggested link + keyword match reason

**G. ⚠️ Ingest Candidates** (Info — 3 sources) — LLM

*G1 — raw/ files not yet ingested:*
- `list_files(path="30_KNOWLEDGE_BASE/raw/")` — list files in raw/
- `search_files(path="30_KNOWLEDGE_BASE/wiki/", regex="source: \"[filename]\"")` — search for source references
- Flag if: no match found → file not ingested
- Self-assess: ✅ INGEST (metrics, terms, benchmarks) vs ❌ SKIP (scripts, covered data)
- Report: `[filename] | Signal: [1-line reason] | Suggested domain: [domain]`

*G2 — Closed cases with insight not yet ingested:*
- `list_files(path="_cases/closed/", recursive=true, file_pattern="*.md")` — scan closed cases
- `read_file()` — read Closing Record from each case
- Flag if: Lessons Learned ≠ "—" AND Decision Made non-empty AND no wiki `source:` pointing to this case
- Self-assess: INGEST (reusable benchmark/policy) vs SKIP (one-off outcome)
- Report: `[case slug] | Closed: [date] | Decision: [60 chars] | Suggested domain: [domain]`

*G3 — Op log patterns:*
- `read_file(path="10_OPERATION_DATA/[log_file]", limit=50)` — read last entries of each operation log file
- Flag if: same metric deviates >10% from 4-entry average in ≥3 consecutive entries
- Strategic pattern → ingest as wiki analysis page
- Report: `[log file] | Metric: [name] | Pattern: [direction + magnitude] | Domain: [domain]`

*H. ⚠️ Source of Truth Conflicts (Critical -- LLM):*
- Check for known duplication patterns where the same data lives in 2+ places:
  - **Tasks:** LUSINE_TODO_Kanban.md vs _inbox/tasks.md (if found) -> Kanban is single source (tasks.md was deleted in prior migration; redirect to Kanban if recreated)
  - **Active cases:** _cases/active/ files vs ACTIVE_CASES_INDEX.md -> disk files are source, index is derived
  - **Store KPIs:** CONTEXT.md section 2 vs dedicated wiki pages -> wiki page is source, CONTEXT.md is snapshot
  - **Recipe data:** raw/recipes/ CSVs vs Recipe_Index.json -> raw CSVs are source, JSON is cache
  - **Command registry:** .kilo/command/*.md vs .kilo/agent/lusine.md SLASH COMMANDS -> lusine.md lists all, commands define one each
- For each suspected pair: check if both files exist AND have overlapping content
- Flag if: 2+ sources found for the same data category
- Report format:
  `- [[file_A]] vs [[file_B]] | Same: [what overlaps] | Source of truth: [file_A] | Reason: [why file_A is authoritative] | Action: [delete/redirect file_B or update to point to file_A]`
- Self-assessment per pattern: ⚠️ KEEP (verified single source) vs ⚠️ DUPLICATE (needs resolution)
- Do NOT auto-fix -- flag for Warren to decide which source to keep


---

### 3. COMPILE REPORT

Output format:
```
# Lint Report — [SCOPE]
Date: YYYY-MM-DD | Domain(s): [scope] | Pages scanned: [N] | Mode: hybrid (script + LLM)

## Summary
🔴 Critical:  [N] issues (action required)
🟡 Warning:   [N] issues (fix this sprint)
🔵 Info:      [N] issues (optional)

## 🔴 A. Contradiction Flags
- [[domain/Page_Name]] | Tag: flagged-contradiction | Note: "[quoted snippet]"

## 🔴 B. Status Inconsistencies
- [[domain/Page_Name]] | Issue: [description] | Suggested fix: [action]

## 🟡 C. Stale Data (>30 days active)
- [[domain/Page_Name]] | Last updated: YYYY-MM-DD (XX days ago)

## 🟡 D. Orphaned Pages
- [[domain/Page_Name]] | Domain: [domain] | Age: [days] | Likely cause: [new/forgotten]

## 🟡 E. Frontmatter Gaps
- [[domain/Page_Name]] | Missing: [field1, field2]

## 🔵 F. Missing Cross-References
- [[domain/Page_Name]] | Suggested: [[related_domain/Related_Page]] (reason: [keywords])

## ⚠️ G. Ingest Candidates
**G1 — raw/ not yet ingested:**
- [filename] | Signal: [reason] | Domain: [domain]

**G2 — Closed cases with insight:**
- [case-slug] | Closed: [date] | Decision: [60 chars] | Domain: [domain]

**G3 — Op log patterns (≥3 consecutive weeks):**
- [log file] | Metric: [name] | Pattern: [direction + magnitude] | Domain: [domain]

## Actions
🔴 REQUIRED before next ingest:
- [ ] [specific action per Critical issue]

🟡 Fix this sprint:
- [ ] [specific action per Warning issue]

🔵 Optional improvements:
- [ ] [specific action per Info issue]
```

---

### 4. SHOW WARREN + OFFER AUTO-FIX

Display full lint report, then ask:

```
Lint complete: [N] Critical, [N] Warning, [N] Info issues found.

ORION's recommended actions (in priority order):
1. [Most urgent Critical issue] → suggested fix: [specific action]
2. [Next Critical or Warning] → suggested fix: [specific action]
3. [...continue for all Critical + Warning items]

I can automatically fix these mechanical issues right now:
  - Add missing frontmatter fields (with placeholder values for you to fill)
  - Remove archived pages from index.md

I cannot auto-fix (need your judgment):
  - Contradictions — requires decision on which version is correct
  - Stale content — requires you to confirm whether to refresh or archive
  - Orphaned pages — requires you to confirm intent (keep / archive / link)

Options:
  y        → approve all auto-fixes ORION listed above
  [list]   → specify which auto-fixes to apply (e.g., "fix frontmatter only")
  n        → no auto-fixes, log findings only
```

**PAUSE — wait for Warren's response before making any changes.**

---

### 5. EXECUTE APPROVED FIXES (if any)

For each approved fix:
- Make the change in the relevant file
- Note what was changed in the fix log below

Fix log template (append to report):
```
## Fixes Applied
- [Page_Name] | [field added / line removed] | [timestamp]
```

---



### 6. SAVE REPORT FILE (Rolling)

**Output location:** `_kilo/lint/lint_[YYYY].md` (1 file/year, append newest entry on top)

No longer create separate daily files. Append new entry to top of rolling file, with header:

```
---
## YYYY-MM-DD

**Scope:** [scope] | **Pages scanned:** [N]

### Summary
🔴 Critical:  [N]
🟡 Warning:   [N]
🔵 Info:      [N]

...
```

If file does not exist, create new with frontmatter:
```
---
type: lint_rolling
scope: [scope]
year: YYYY
last_updated: YYYY-MM-DD
---
```

---

### 6B. UPDATE LOG
- `read_file(path="30_KNOWLEDGE_BASE/wiki/log.md")` → `write_to_file()` to append entry:
  ```
  | YYYY-MM-DD | /lint [scope] | [N] Critical, [N] Warning, [N] Info | Fixes applied: [N] | [approved/pending] |
  ```

---

### 7. COMMIT
Run from `vault/` directory via `execute_command()`:
```
cd c:/Users/khoans/Documents/Warren_OS_Local/vault
git add _kilo/lint/lint_[YYYY].md
git add wiki/log.md
git add wiki/index.md          # if index was modified
git add wiki/[any fixed files] # all files touched by auto-fixes
git add scripts/lint_constants.py scripts/build_frontmatter_cache.py scripts/lint_mechanical.py
git add 30_KNOWLEDGE_BASE/wiki/FRONTMATTER_CACHE.json
git commit -m "Lint: [scope] | [N]C [N]W [N]I | [N] fixes applied | v4.0 rolling file | [date]"
git log --oneline -1
```
Paste commit hash as confirmation.

---

## Cross-reference

Sections 5B and 5C have been spun out into separate commands for single responsibility:
- /ideas-review — Monthly ideas review (first Sunday)
- /pnl-check — Monthly P&L cross-check (day 10-16)

## Rules

- **Never delete pages** — only flag for archival. Warren decides.
- **Never auto-fix content** — only mechanical gaps (missing fields, index cleanup).
- **Stale threshold:** 30 days for analysis/tracking pages; 90 days for reference pages.
- **Contradiction flag = explicit tag only.** Do not infer contradictions from content.
- **Cross-reference suggestions = high-confidence only** (3+ domain keywords without link).
- Run monthly (W3 cadence per CLAUDE.md) or on-demand after major ingests.
- 🔴 Critical issues block next ingest until resolved. State this explicitly in report.
- **Cache first:** If `FRONTMATTER_CACHE.json` is stale or empty, rebuild before linting.
- **LLM fallback:** If Python scripts fail, fall back to manual Step 1 SCAN (read files individually).

---

**v2.1 | 2026-05-05 | Added: ORION-proposes priority order at Step 4 with y/list/n options. Explicit separation of auto-fixable vs judgment-required issues.**
**v3.0 | 2026-05-25 | Script + LLM hybrid: mechanical checks (B/C/D/E) via lint_mechanical.py reading FRONTMATTER_CACHE.json. LLM only handles A/F/G. --quick flag for fast scans.**
**v3.1 | 2026-05-25 | ORION+Deepseek adaptation — Read→read_file, Write→write_to_file, Grep→search_files, python→execute_command, agent name update**
