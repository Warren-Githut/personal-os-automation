---
model: deepseek-obsidian/deepseek-v4-pro
description: "Vault search protocol (wiki graph + cases + tasks + pulse logs) adapted for ORION+Deepseek toolchain."
updated: 2026-06-02
---

# /query — Vault Search: Wiki + Cases + Tasks + Pulse Logs
# v1.6 | 2026-05-25
# PURPOSE: Find related files by concept/keyword from 4 sources: wiki graph, cases (indexed), tasks, pulse logs.
# Value: find hidden connections between files + search 4 sources simultaneously — not token saving.
# OPTIMIZATION: ACTIVE_CASES_INDEX (Condition 1) + FRONTMATTER_CACHE for YAML lookups (Condition 2).

---

## Usage

```
/query [keyword or concept]
```

**Examples:**
```
/query GG family access
/query net worth finance
/query health exercise
/query trading VN stocks
```

---

## Protocol

### STEP 0 — CHECK GRAPH EXISTS & VALID

Use `read_file(path="30_KNOWLEDGE_BASE/wiki/WIKI_GRAPH.json")`:
- If file MISSING -> notify "WIKI_GRAPH.json not found — rebuilding..." -> trigger `/rebuild-index --graph` -> continue.
- If file exists but `JSON.parse()` FAIL (corrupt) -> notify "WIKI_GRAPH.json corrupted — rebuilding..." -> trigger `/rebuild-index --graph` -> continue.

---

### STEP 1 — PARSE QUERY

Extract from query:
- **Store tokens**: removed for Personal_OS (no store concept)
- **Domain tokens** — map to domain string in graph:

  | Query keyword | Domain string |
  |---|---|
  | "trading", "stock", "equity", "portfolio", "vn-index", "btc" | `trading` |
  | "health", "weight", "bmi", "exercise", "sleep", "blood", "workout" | `health` |
  | "family", "gg", "gia-gia", "son", "parent", "mother", "father" | `family_gg` |
  | "finance", "budget", "net-worth", "debt", "saving", "burn", "expense" | `finance` |
  | "growth", "learn", "book", "insight", "skill", "course" | `growth` |
  | "relationship", "friend", "social", "connection", "network" | `relationship` |
  | "decision", "plan", "goal", "strategy", "commitment" | `decision_log` |
  | "case", "dispute", "legal", "issue", "problem" | `cases` |

- **Period tokens**: year/month patterns ("april", "Q1", "2026", "march", "Q2", etc.)
- **Keyword tokens**: remaining words (used for path matching)

---

### STEP 2 — CACHE LOOKUP + SCORE NODES

**2A — Check FRONTMATTER_CACHE (Condition 2 optimization + Condition 3 error handling):**

```
try {
  cache = JSON.parse(read_file(path="30_KNOWLEDGE_BASE/wiki/FRONTMATTER_CACHE.json"))
  validate: cache._schema exists AND cache.data exists
  validate: cache._total_files >= 10 (sanity check)
  if cache older than 24h AND disk file exists -> log "⚠️ Cache stale" (continue anyway)
  use cache for tags[], period, domain, status lookups (skip YAML frontmatter parsing)
} catch (error) {
  log "⚠️ cache error: [error type]" (SILENT to Warren)
  fallback to WIKI_GRAPH.json below (no halt)
}
```

- If file exists + valid JSON -> use cache to lookup `tags[]`, `period`, `domain`, `status` (skip file reads)
- If missing, corrupt, or invalid schema -> fallback to WIKI_GRAPH.json scoring (silent fallback, no error to Warren)

**2B — Load WIKI_GRAPH.json via `read_file()` (if cache unavailable):**

Score each node by:

| Signal | Points |
|---|---|
| Node path contains keyword (case-insensitive) | +3 per keyword |
| Node domain matches query domain token | +2 |
| Node period_buckets[] matches query period | +2 |
| Node type = "analysis", "tracking", or "tracker" | +1 |
| Node status = "archived" | -2 |
| Node data_status = "stub" | -3 |

Sort descending by score. **Tiebreaker:** node with newer `last_updated` -> higher rank. Take top 5.

---

### STEP 3 — EXPAND VIA EDGES

For each top-5 node, traverse 1 hop edges:
- `explicit_link` -> mark as "directly linked"
- `same_domain_cross_reference` -> add if not present, mark edge type + domain
- `same_period` -> add if cross-domain and not present

Total results: max 8 files (5 direct + 3 connected). Priority: explicit_link > same_domain_cross_reference > same_period.

---

### STEP 3B — SEARCH ACTIVE CASES (via ACTIVE_CASES_INDEX)

`read_file(path="_cases/ACTIVE_CASES_INDEX.md")` (table format, replaces glob logic):
- Match if: Slug, Domain, Summary columns contain keyword (case-insensitive)
- Extract: Slug, Priority, Domain, Summary, Follow-up from table row
- Sort: HIGH priority first -> nearest follow_up (non-null) first -> null follow_up at bottom
- **Optimization (Condition 1):** Read 1 index file instead of list_files + read_file 10+ active case files (~90% fewer file reads)
- Fallback: If ACTIVE_CASES_INDEX.md missing or parse fail -> `list_files(path="_cases/active/", file_pattern="*.md")` manually (graceful degradation)

---

### STEP 3C — SEARCH OPEN TASKS

`read_file(path="_inbox/tasks.md")`. For each line starting with `- [ ]`:
- **Only match on main line** (`- [ ]` line) — do not scan sub-bullets (Trigger/Expected/Silent fail check)
- If keyword appears in sub-bullet -> no match (avoid false positives from context)
- Separate 2 types: action tasks (no `[monitor]`) and monitor tasks (has `[monitor]`)
- Truncate at 120 characters if line longer
- Show action tasks first, monitor tasks after with separate label

---

### STEP 3D — SEARCH PULSE LOGS

`list_files(path="10_PULSE/", file_pattern="*.md")`.
For each file:
- Match if: filename contains keyword (case-insensitive)
- Extract: `name`, `last_updated` from frontmatter
- Show: filename + last_updated date
- No need to traverse entries — just know this pulse log exists and is relevant

Example: query "trading" -> match `020_VNStock_Weekly_Outlook.md` ✓
Example: query "health" -> match `050_Health_Log.md` ✓
Example: query "GG" -> no filename matches -> section hidden ✓

---

### STEP 3E — SEARCH CLOSED CASES INDEX

`read_file(path="_cases/closed/CLOSED_CASES_INDEX.md")`. For each table row:
- Match if: slug, type, domain, or summary contains keyword (case-insensitive)
- Extract: closed date, type, slug, domain, summary, file link
- Show max 5 rows — prioritize nearest match (newest on top already ensured)
- Hide section if no match or file doesn't exist

---

### STEP 4 — OUTPUT

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
/query: "[query text]"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WIKI RESULTS:
  [domain/filename.md] — [domain] | [type] | tags: [tag1,tag2]
  [domain/filename.md] — via explicit_link from [source_file]
  (If 0 results: "No wiki files found — files in same domain: [list]")

ACTIVE CASES:
  [slug] — [priority] | domain: [...] | follow_up: YYYY-MM-DD (or "no deadline" if null)
  (Hide this section if no match)

PULSE LOGS:
  [filename] — last updated: YYYY-MM-DD
  (Hide this section if no match)

OPEN TASKS:
  - [ ] [task headline, max 120 chars]
  👁 MONITOR: [monitor task headline]
  (Hide this section if no match)

CLOSED CASES:
  [{slug}] {1-sentence summary} — {type} | domain: {domain} | closed: {date}
  (Hide this section if no match)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Rules:** Any section with no match -> hide entirely, do not show empty header.

---

## Anti-patterns

- ❌ Do not read file content to answer /query — only traverse graph + frontmatter + task headlines
- ❌ Do not return > 8 wiki files — if more, prioritize explicit_link > same_domain > same_period
- ❌ Do not include stub files in top wiki results unless no other options exist
- ❌ Do not crash if WIKI_GRAPH.json missing or corrupt — auto-trigger rebuild
- ❌ Do not scan sub-bullets of tasks — only main `- [ ]` line
- ❌ Do not scan entire _cases/closed/ folder — only read CLOSED_CASES_INDEX.md
- ❌ Do not read entries inside pulse log files — only match filename, show last_updated
- ❌ Do not mix action tasks with monitor tasks — show separately, label clearly
