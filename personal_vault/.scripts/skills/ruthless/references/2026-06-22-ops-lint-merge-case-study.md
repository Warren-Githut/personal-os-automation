# Case Study: ops-lint → ops-index-sync Merge (2026-06-22)

## Target
`ops-lint` skill — vault linting + frontmatter cache rebuild.

## Trigger
Warren asked: "lệnh lint này có nội dung gì trong đó. hãy nói thật lòng và thẳng thắn, nó có thật sự cần thiết hoặc merge với lệnh nào hiện có được ko"

## Analysis

### SKILL.md claimed (15+ checks):
- BOM detection, YAML parse errors, markdown syntax, duplicate last_updated, stale >30d, table alignment, cross-reference validation, wiki graph connectivity, case completeness, WIKI_INDEX freshness, ORERATION_INDEX duplicates

### Actually shipped (~9 checks, confirmed via runner script):
- BOM, YAML parse errors, no frontmatter, stale >30d, required fields, duplicate frontmatter blocks, case gaps, OPERATION_INDEX duplicates, WIKI_INDEX freshness, briefs freshness
- **Not implemented:** markdown syntax, table alignment, cross-reference validation, wiki graph connectivity

### Overlap Analysis
| Check | ops-lint | ops-index-sync | vault-structure-audit | vault-metadata-normalization |
|---|---|---|---|---|
| No frontmatter | ✅ | ✅ | ✅ (Phase 1F) | ✅ (SCHEMA_MAP) |
| Stale last_updated | ✅ | ✅ | ✅ | ❌ |
| Index duplicates | ✅ | (rebuild prevents) | ❌ | ❌ |
| Case schema gaps | ✅ | ❌ | ✅ | ✅ |
| BOM detection | ✅ | ❌ | ✅ (Phase 1G) | ❌ |
| YAML parse errors | ✅ | ❌ | ❌ | ❌ |

**Unique check:** YAML parse error detection — 1 line: `try: yaml.safe_load(fm)`

### Verdict: MERGE into ops-index-sync
- Every check overlapped with at least one other skill
- Only unique value: 1-line YAML parse error check
- Two scripts existed doing similar things: `_ops_lint_runner.py` (vault) + `ops-lint-runner.py` (skill dir)
- Cron redundancy: ops-index-sync ran Sunday 18:00, ops-lint ran Monday 09:00 (lint detecting nothing new)

### Execution
1. Created `vault/scripts/ops_index_lint_sync.py` — unified script with --check-only / --sync-only flags
2. Updated `ops-index-sync` SKILL.md — added lint docs, --check-only flag
3. Deprecated `ops-lint` SKILL.md — redirect notice
4. Updated cron `5e51a9a2fd7a` (Mon 09:00) → ops-index-sync --check-only
5. Created cron `14afd61e57b9` (Mon 14:00) → reminder with description
6. Updated memory reference

### Result
- 2 cron jobs → 1 (other repurposed as reminder)
- 2 SKILL.md files → 1 active + 1 redirect
- 2 runner scripts → 1 unified script
- Async checks eliminated