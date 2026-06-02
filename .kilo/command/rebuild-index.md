---
model: deepseek-obsidian/deepseek-v4-flash
description: "Wiki index reconciliation + graph rebuild adapted for Personal_OS."
updated: 2026-06-02
---

# /rebuild-index — WIKI_INDEX Reconciliation + Graph Rebuild (Personal_OS)
# v2.1 | 2026-06-02
# Personal_OS adaptation — paths updated to personal_vault/

---

## Usage

```
/rebuild-index              # incremental — only process changed files
/rebuild-index --full       # full scan entire wiki
/rebuild-index --graph      # regenerate WIKI_GRAPH.json
/rebuild-index --frontmatter # build FRONTMATTER_CACHE.json (condition 2)
```

---

## PRE-PHASE — DETECT MODE

**Incremental (default):**
Run from `personal_vault/` directory:
```
cd c:/Users/khoans/Documents/Personal_OS/personal_vault
git diff --name-only HEAD -- 30_KNOWLEDGE_BASE/wiki/
git ls-files --others --exclude-standard 30_KNOWLEDGE_BASE/wiki/
```
Union = `changed_files[]`. If both empty → "Index is current." and stop.

**Full (`--full`):** Skip git, scan all.

---

## PHASE 1 — SCAN FILESYSTEM

`list_files(path="personal_vault/30_KNOWLEDGE_BASE/wiki/", recursive=true, file_pattern="*.md")`. Manual exclude filter: `WIKI_INDEX.md`, `index.md`, `log.md`, `DECISION_LOG.md`, `*_Hub*`, `_TEMPLATES`, `archive/`.

Incremental: intersect with `changed_files[]`.

## PHASE 2 — SCAN WIKI_INDEX

`read_file(path="personal_vault/30_KNOWLEDGE_BASE/wiki/WIKI_INDEX.md")`, parse table rows (`| [[filename]] | ... |`). Domain from section header. Build `indexed_files[]` = `domain/filename.md`.

## PHASE 3 — DIFF

- **MISSING**: on disk, not in index → add
- **ORPHANED**: in index, not on disk → remove
- **STALE**: in both + in `changed_files[]` → flag `⚠` for Warren review

## PHASE 4 — REPORT + CONFIRM

Show MISSING/ORPHANED/STALE counts + file list. Ask Warren confirm before fixing.

## PHASE 5 — FIX

- MISSING: read frontmatter, append row to correct section. No frontmatter → `## 🆕 RECENTLY ADDED`.
- ORPHANED: remove row.
- STALE: append `→ upd YYYY-MM-DD` to Period column. Do not rewrite Key Insights.
- Update header: `Last verified: YYYY-MM-DD`
- Commit (run from `personal_vault/`): `git commit -m "chore(wiki): rebuild-index reconciliation YYYY-MM-DD"`

---

## --graph mode: Regenerate WIKI_GRAPH.json

1. `list_files(path="personal_vault/30_KNOWLEDGE_BASE/wiki/", recursive=true, file_pattern="*.md")` — same excludes as PHASE 1 (manual filter)
2. `read_file()` each file (first 20 lines to parse YAML frontmatter, batch max 10 files at a time)
3. Build nodes:
   - `path`, `domain`, `type`, `status` from frontmatter
   - `period_buckets[]` = tags[] pattern: "April-2026"→"2026-04", "Q1-2026"→"2026-Q1". Fallback: `period:` field. Skip bare years.
4. Build edges:
   - `explicit_link`: related: field → skip folder refs, broken refs, hub refs. Resolve filename-only via unique search.
   - `same_period`: files sharing monthly/quarterly bucket
5. `write_to_file(path="personal_vault/30_KNOWLEDGE_BASE/wiki/WIKI_GRAPH.json", content=json.dumps(graph))` → write WIKI_GRAPH.json
6. Report: `N nodes, M edges, K warnings | [[links]] injected: X files`

---

## --frontmatter mode: Build FRONTMATTER_CACHE.json (Condition 2)

1. `list_files(path="personal_vault/30_KNOWLEDGE_BASE/wiki/", recursive=true, file_pattern="*.md")` — same excludes as PHASE 1 (manual filter)
2. `read_file()` each file (first 20 lines to parse YAML frontmatter, batch max 10 files at a time):
   - Extract: `tags[]`, `period`, `domain`, `status`, `related[]`
   - Build entry: `{ tags, period, domain, status, related, last_updated }`
3. `write_to_file(path="personal_vault/30_KNOWLEDGE_BASE/wiki/FRONTMATTER_CACHE.json", content=json.dumps(cache, indent=2))` → write cache:
4. Report: `N files cached | Build time: X.XXs`

**Rebuild triggers (automatic):**
- Post-commit hook: rebuild cache after /ingest or /rebuild-index --graph
- Hourly cron: `0 * * * * /rebuild-index --frontmatter` (optional, low priority)

---

## Condition 3 — Cache Error Handling + Validation

**Cache validation rules (apply whenever cache is loaded via `read_file()` + `json.parse()`):**

1. **File existence:** If FRONTMATTER_CACHE.json missing or `read_file()` returns error → return `{ cache_status: "missing" }`, trigger fallback
2. **JSON parse:** If `JSON.parse()` fails → return `{ cache_status: "corrupt", error: [parse error] }`, trigger fallback
3. **Schema check:** If parsed JSON missing `_schema` or `data` key → return `{ cache_status: "invalid_schema" }`, trigger fallback
4. **Freshness:** If `_last_built` older than 24 hours AND file modification time exists → log "⚠️ Cache stale (24h+) — consider rebuild"
5. **Completeness:** If `_total_files` < 10 (sanity check) → log "⚠️ Cache appears incomplete (only N files)"

**Fallback behavior:**

```
try {
  cache = read_file(path="personal_vault/30_KNOWLEDGE_BASE/wiki/FRONTMATTER_CACHE.json")
  if cache validation fails → throw
  use cache for lookups
} catch {
  log "[explore|query] cache unavailable — falling back to [explicit file reads|graph scan]"
  continue with original logic (no halt, no error to Warren)
}
```

**Silent fail protection:**
- Fallback is SILENT — Warren sees no error message
- Reason: cache is optimization only, not critical path
