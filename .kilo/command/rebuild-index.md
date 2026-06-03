---
model: deepseek-obsidian/deepseek-v4-flash
description: "Wiki index reconciliation + graph rebuild adapted for ORION+Deepseek toolchain."
updated: 2026-06-02
---

# /rebuild-index â€” WIKI_INDEX Reconciliation + Graph Rebuild
# v2.2 | 2026-06-02
# ORION+Deepseek adaptation â€” Globâ†’list_files, Readâ†’read_file, Writeâ†’write_to_file, pythonâ†’execute_command

---

## Usage

```
/rebuild-index              # incremental â€” only process changed files
/rebuild-index --full       # full scan entire wiki
/rebuild-index --graph      # regenerate WIKI_GRAPH.json
/rebuild-index --frontmatter # build FRONTMATTER_CACHE.json (condition 2)
/rebuild-index --guide      # regenerate USER_GUIDE.md from lusine.md + vault scan
```

---

## PRE-PHASE â€” DETECT MODE

**Incremental (default):**
Run from `vault/` directory via `execute_command()`:
```
cd c:/Users/khoans/Documents/Warren_OS_Local/vault
execute_command(command="git diff --name-only HEAD -- 30_KNOWLEDGE_BASE/wiki/", cwd="vault")
execute_command(command="git ls-files --others --exclude-standard 30_KNOWLEDGE_BASE/wiki/", cwd="vault")
```
Union = `changed_files[]`. If both empty â†’ "Index is current." and stop.

**Full (`--full`):** Skip git, scan all.

---

## PHASE 1 â€” SCAN FILESYSTEM

`list_files(path="30_KNOWLEDGE_BASE/wiki/", recursive=true, file_pattern="*.md")`. Manual exclude filter: `WIKI_INDEX.md`, `index.md`, `log.md`, `DECISION_LOG.md`, `*_Hub*`, `_TEMPLATES`, `archive/`.

Incremental: intersect with `changed_files[]`.

## PHASE 2 â€” SCAN WIKI_INDEX

`read_file(path="30_KNOWLEDGE_BASE/wiki/WIKI_INDEX.md")`, parse table rows (`| [[filename]] | ... |`). Domain from section header. Build `indexed_files[]` = `domain/filename.md`.

## PHASE 3 â€” DIFF

- **MISSING**: on disk, not in index â†’ add
- **ORPHANED**: in index, not on disk â†’ remove
- **STALE**: in both + in `changed_files[]` â†’ flag `âš ` for Warren review

## PHASE 4 â€” REPORT + CONFIRM

Show MISSING/ORPHANED/STALE counts + file list. Ask Warren confirm before fixing.

## PHASE 5 â€” FIX

- MISSING: read frontmatter, append row to correct section. No frontmatter â†’ `## ðŸ†• RECENTLY ADDED`.
- ORPHANED: remove row.
- STALE: append `â†’ upd YYYY-MM-DD` to Period column. Do not rewrite Key Insights.
- Update header: `Last verified: YYYY-MM-DD`
- Commit (run from `vault/` via `execute_command()`): `git commit -m "chore(wiki): rebuild-index reconciliation YYYY-MM-DD"`

---

## --graph mode: Regenerate WIKI_GRAPH.json

1. `list_files(path="30_KNOWLEDGE_BASE/wiki/", recursive=true, file_pattern="*.md")` â€” same excludes as PHASE 1 (manual filter)
2. `read_file()` each file (first 20 lines to parse YAML frontmatter, batch max 10 files at a time)
3. Build nodes:
   - `path`, `domain`, `type`, `status` from frontmatter
   - `stores[]` = tags[] match "LU3"/"LU5"/"LU7"
   - `period_buckets[]` = tags[] pattern: "April-2026"â†’"2026-04", "Q1-2026"â†’"2026-Q1". Fallback: `period:` field. Skip bare years.
4. Build edges:
   - `explicit_link`: related: field â†’ skip folder refs, broken refs, hub refs. Resolve filename-only via unique search.
   - `same_store_cross_domain`: store-specific files Ã— different domain â†’ intersection stores
   - `same_period`: files sharing monthly/quarterly bucket
5. `write_to_file(path="30_KNOWLEDGE_BASE/wiki/WIKI_GRAPH.json", content=json.dumps(graph))` â†’ write WIKI_GRAPH.json
6. `execute_command(command="python scripts/inject_wiki_links.py --apply", cwd="vault")` â†’ inject `## Related` [[wikilinks]]
7. Report: `N nodes, M edges, K warnings | [[links]] injected: X files`

---

## --frontmatter mode: Build FRONTMATTER_CACHE.json (Condition 2)

1. `list_files(path="30_KNOWLEDGE_BASE/wiki/", recursive=true, file_pattern="*.md")` â€” same excludes as PHASE 1 (manual filter)
2. `read_file()` each file (first 20 lines to parse YAML frontmatter, batch max 10 files at a time):
   - Extract: `tags[]`, `period`, `domain`, `status`, `related[]`
   - Build entry: `{ tags, period, domain, status, related, last_updated }`
3. `write_to_file(path="30_KNOWLEDGE_BASE/wiki/FRONTMATTER_CACHE.json", content=json.dumps(cache, indent=2))` â†’ write cache:
4. Report: `N files cached | Build time: X.XXs`

**Rebuild triggers (automatic):**
- Post-commit hook: rebuild cache after /ingest or /rebuild-index --graph
- Hourly cron: `0 * * * * /rebuild-index --frontmatter` (optional, low priority)

---


## --guide mode: Regenerate USER_GUIDE.md

> **Purpose:** Auto-generate `vault/USER_GUIDE.md` from live vault structure + lusine.md.
> Run whenever commands change in lusine.md or vault structure changes.

**Output:** `vault/USER_GUIDE.md` → YAML frontmatter with `auto_regenerated: true`, `source_command: /rebuild-index --guide`

### STEP 1 — Scan vault structure

Read vault root directory via `list_files(path="vault/")`. Extract top-level entries:
- Directories ending in `/` → folder entries
- Notable files: CHANGELOG.md
- Map each directory with a 1-line purpose description

Build folder map table:
```
| Folder / File | What's inside |
|---|---|
| 📁 **00_CORE_LOGIC/** | [purpose from vault architecture description] |
| 📁 **10_OPERATION_DATA/** | [purpose] |
| ... | ... |
| 📄 **CHANGELOG.md** | Feature/session-level change history |
```

### STEP 2 — Parse lusine.md for slash commands

Read `.kilo/agent/lusine.md`. Locate the `## SLASH COMMANDS` section. Extract:
- Each subsection header (### 📥 Data In, ### 📋 Ops & Decisions, etc.) → category group
- Each command line pattern: `` - `/command [args]` → `command.md` — [description] ``
- Map to a 2-column table per category: `| Command | What it does |`

Group structure (from lusine.md):
```
### 📥 Data In
| Command | What it does |
|---|---|
| /command [args] | [description from lusine.md] |
| ... | ... |

### 📋 Ops & Decisions
| Command | What it does |
|---|---|
| ... | ... |

### 🔧 Maintenance
| Command | What it does |
|---|---|
| ... | ... |

### 🎯 Ideas & Creativity
| Command | What it does |
|---|---|
| ... | ... |

### 🎯 Intake & Protocol
| Command | What it does |
|---|---|

### ✅ Review
| Command | What it does |
|---|---|
```

**Note:** For commands listed as `| /command | description |` table format (ideas-review, pnl-check), extract directly. For commands listed as `- /command → command.md — description`, parse and clean up.

### STEP 3 — Extract Quick Rules

Read lusine.md `## HARD CONSTRAINTS` section. Distill into bullet-point rules:
1. Raw data READ-ONLY
2. Newest on top
3. YAML frontmatter required
4. English only
5. File → command → done (don't manually edit inbox)
6. Confidence tags on analysis
7. Cases > 1 day

### STEP 4 — Generate file

Build complete USER_GUIDE.md with this structure:

```
---
description: "L'Usine Operations Vault user guide — folder map, commands, rules"
last_updated: YYYY-MM-DD
auto_regenerated: true
source_command: /rebuild-index --guide
domain: lusine_operations
tags: ["guide", "reference", "index"]
---

# USER_GUIDE — L'Usine Operations Vault

> Quick-start reference. Open this file whenever you forget where things are or what command to use.

---

## 📁 Folder Map

[STEP 1 output]

---

## 📥 Slash Commands

[STEP 2 output — all category tables in order]

---

## ⚡ Quick Rules

[STEP 3 output — numbered list]

---

## 📌 Need help?

- Can't find a command? → /query [keyword]
- Unsure about a file? → Tell ORION the filename
- Something wrong? → /lint [scope] to scan for issues

---

> Auto-generated by /rebuild-index --guide on YYYY-MM-DD. Run again when commands or vault structure changes.
```

### STEP 5 — Write file

Write to `vault/USER_GUIDE.md` via Write tool. Verify content by reading back first 10 lines.

### STEP 6 — Report

Report to Warren:
- "USER_GUIDE.md regenerated — N folders, M commands across C categories, R rules."
- Highlight any discrepancies found between lusine.md and previous USER_GUIDE.md (if pre-existing)

---

## Condition 3 â€” Cache Error Handling + Validation

**Cache validation rules (apply whenever cache is loaded via `read_file()` + `json.parse()`):**

1. **File existence:** If FRONTMATTER_CACHE.json missing or `read_file()` returns error â†’ return `{ cache_status: "missing" }`, trigger fallback
2. **JSON parse:** If `JSON.parse()` fails â†’ return `{ cache_status: "corrupt", error: [parse error] }`, trigger fallback
3. **Schema check:** If parsed JSON missing `_schema` or `data` key â†’ return `{ cache_status: "invalid_schema" }`, trigger fallback
4. **Freshness:** If `_last_built` older than 24 hours AND file modification time exists â†’ log "âš ï¸ Cache stale (24h+) â€” consider rebuild"
5. **Completeness:** If `_total_files` < 10 (sanity check) â†’ log "âš ï¸ Cache appears incomplete (only N files)"

**Fallback behavior (both /explore + /query):**

```
try {
  cache = read_file(path="30_KNOWLEDGE_BASE/wiki/FRONTMATTER_CACHE.json")
  if cache validation fails â†’ throw
  use cache for lookups
} catch {
  log "[explore|query] cache unavailable â€” falling back to [explicit file reads|graph scan]"
  continue with original logic (no halt, no error to Warren)
}
```

**Silent fail protection:**
- Fallback is SILENT â€” Warren sees no error message
- Reason: cache is optimization only, not critical path
- Monitoring: task entry monitors first cache miss (see Condition 4)





