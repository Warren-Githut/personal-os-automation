# 2026-07-01: vault-index-sync Deprecation + vault-structure-audit/ops-lint Overlap Detection

## vault-index-sync Deprecation

**Context:** `scripts/ops_index_lint_sync.py` had already merged ops-lint + ops-index-sync on 2026-06-22 (see `2026-06-22-ops-lint-merge-case-study.md`). However, the `devops/vault-index-sync` skill under warren-profile was never updated — it still referenced standalone scripts (`ops_index_watchdog.py`), `.kilo/` dead paths, and claimed to be the execution layer.

**Action taken:**
- SKILL.md frontmatter: added `[DEPRECIATED — merged into scripts/ops_index_lint_sync.py]`
- Title: added ⚠️ DEPRECIATED
- Added deprecation banner blockquote
- Updated Watchdog Pattern to reference the merged script
- Updated Schema Mismatch section to reference merged script
- Related section: removed 3 `.kilo/` dead refs, added merged script + HERMES_COMMANDS.md refs
- HERMES_COMMANDS.md §5: marked Weekly Index Sync row as strikethrough + merge note

**Lesson:** After any code merge/consolidation, the corresponding skill documentation must be audited for stale references. The code merge is not complete until the skill catches up.

## vault-structure-audit ↔ ops-lint Overlap

**Finding:** `/vault-structure-audit` (skill) shares partial overlap with `/ops-lint` (script):

| vault-structure-audit phase | ops-lint equivalent | Overlap type |
|---|---|---|
| Phase 1F — Index Integrity | OPERATION_INDEX duplicate check in `ops_index_lint_sync.py` | Same check, different depth |
| Phase 3D — Rebuild All Indices | ops-lint rebuilds FRONTMATTER_CACHE + indexes | Same action |

**Verdict:** vault-structure-audit is a **strategic consumer** of ops-lint output. It should reference ops-lint results rather than re-implementing the checks. Not a merge candidate — 2 different levels.

**Key differentiators:**
| Dimension | ops-lint | vault-structure-audit |
|-----------|----------|----------------------|
| Depth | File-level: frontmatter, dates, schema | Architecture-level: MOC, graph, profile drift, cross-vault |
| Script | `ops_index_lint_sync.py` (automated) | LLM-driven skill (no script) |
| Scope | Single vault data quality | Multi-profile, multi-vault strategic health |

## Methodology for Detecting Overlaps

Used in this session to compare 4 items (ops-lint, ops-index-sync, ops-weekly-report, vault-structure-audit):

1. **Search vault** for each name → `search_files(pattern, path=vault/)` → find documentation, command references
2. **Search skills** for each name → `skill_view(name)` on each candidate
3. **Read scripts** → check actual implementation (what it really does vs what it claims)
4. **Check cron jobs** → `cronjob action=list` → identify active vs dead documentation
5. **Cross-reference matrix** → build comparison table of actual actions
6. **Verdict** → KEEP / MERGE / DELETE / DEPRECIATE per Ruthless protocol
