---
name: vault-index-sync
description: [DEPRECIATED — merged into scripts/ops_index_lint_sync.py] Keep vault index files synchronized with source data and enforce single-source-of-truth references in commands. Use when working with OPERATION_INDEX, WIKI_INDEX, or any derived index that must mirror frontmatter/file state. Also use when hardening commands against hardcoded file lists.
---

# Vault Index Sync ⚠️ DEPRECIATED

Maintain vault indexes as derived caches from source files, not the other way around. Apply this whenever adding/removing log files, updating frontmatter, or editing command Step 1 sources.

> **⚠️ SKILL NÀY ĐÃ DEPRECIATED — merged vào `scripts/ops_index_lint_sync.py` (06/2026)**
> Execution layer là `scripts/ops_index_lint_sync.py` (vault/scripts/). Skill này giữ lại làm **reference documentation** cho:
> - Canonical index format (cross-profile)
> - Schema mismatch resolution (ops-lint vs index format)
> - Core principles (index = derived, source = truth)
>
> **Không còn standalone execution.** Chạy sync qua:
> ```
> python scripts/ops_index_lint_sync.py       # sync + lint
> python scripts/ops_index_lint_sync.py --sync-only  # index sync only
> ```

## Core Rules

1. **Index = derived. Source = truth.**
   - `OPERATION_INDEX.md` derives `last_updated` from each log file's YAML frontmatter.
   - `WIKI_INDEX.md` derives from actual `30_KNOWLEDGE_BASE/wiki/` contents.
   - If either drifts, the index is wrong, not the source.

2. **Frontmatter is the contract.**
   - Every log/wiki file that can be appended MUST have `last_updated: YYYY-MM-DD` in YAML frontmatter.
   - When a parser or command appends to a file, it MUST also update that file's frontmatter.
   - Missing/ stale frontmatter is a bug, not a warning to ignore.

3. **Commands reference index, not hardcoded lists.**
   - Any command that enumerates op-data files must point to `OPERATION_INDEX.md §Operational Logs` as the source list.
   - Add a lightweight consistency check at session start: count index rows vs command Step 1 sources; mismatch → flag.

4. **New file auto-detection.**
   - At session start, scan the target directory for files not yet in the index table and add them automatically with their frontmatter date.
   - This prevents manual-maintenance drift (e.g. 9→12 files).

5. **Stale guard (30-day rule).**
   - If `last_updated` in frontmatter is >30 days behind the file's `mtime` on disk, flag it explicitly.
   - Do not silently accept obviously stale frontmatter.

6. **Parser contract: atomic 1-pass update on every append/overwrite.**
   - Source of truth is the log file frontmatter `last_updated: YYYY-MM-DD`.
   - `OPERATION_INDEX.md` is a derived cache, not a manual list.
   - On append or overwrite, the parser/command must update **all three** atomically:
     1. the log file body + `last_updated` frontmatter,
     2. `OPERATION_INDEX.md §Operational Logs` matching row,
     3. `OPERATION_INDEX.md` own `last_updated` frontmatter.
   - Missing/failed step 2 or 3 is a bug in the parser, not a warning to ignore.
   - If a log file mtime is >30 days newer than `OPERATION_INDEX.md` last_updated, treat `MISSING_FRONTMATTER` as a fault and auto-repair it.

## Watchdog Pattern ⚠️ DEPRECIATED

> **Execution đã chuyển sang `scripts/ops_index_lint_sync.py`.** Phần này giữ lại làm reference cho logic index sync.

Use a dedicated script (`vault/scripts/ops_index_lint_sync.py` — merged) to enforce the above:

- Read index table.
- Scan directory for eligible files.
- Parse frontmatter `last_updated`.
- Compare with existing index row; update if newer.
- Add missing files at the bottom with a new header.
- Report stale-frontmatter flags.

Trigger points:
- After any `/ops-process-logs` run (post-parse).
- Session start (auto-hook if available).
- Manual: `python scripts/ops_index_lint_sync.py` (sync-only or sync+lint mode).

## Canonical Index Format (cross-vault, warren + personal profiles)

Every index file MUST follow this structure:

1. YAML frontmatter **Properties block**:
   - Required fields: `name`, `type`, `status`, `domain`, `last_updated`, `total_files`, `index_first_rule`, `auto_update`, `stale_check`, `refresh_cadence`, `maintained_by`
   - Optional but recommended: `owner`, `scope`, `related_paths`

2. Inventory table:
   - Use normalized columns: `file`/`name`, `period`/`context`, `type`, `key_insights`/`description`, `last_updated`
   - Do not invent custom schemas per index without a corresponding `related_paths`/scope note explaining the custom columns

3. Update Protocol section at the bottom:
   - Restate how entries are added/removed/updated
   - State whether index is derived (read from source) or canonical (source of truth)

### Workspace authority rules (NON-NEGOTIABLE)

- `99_HERMES_AGENT_WORKSPACE/` (or equivalents under other profiles) = **ALL** Hermes artifacts: SOPs, rules, indexes, scratch, tracking, WIP
- `30_KNOWLEDGE_BASE/wiki/` = human-facing knowledge base (Warren/docs). **Hermes NEVER auto-writes here.** Write/update requires explicit user approval.
- Any file with `hermes_` prefix inside the agent workspace is canonical for that workspace; do not rely on same-named files elsewhere.
- When the user says "rollback" after a bulk plan: revert everything, then apply ONLY the single explicitly approved file move. Do NOT batch-move additional files unless the user explicitly names each one.

## Cross-Profile Index Format Application

When applying a new index format across profiles (warren-profile + personal-profile):
1. Preserve domain-specific sections (e.g. `_growth/_INDEX.md` knowledge-capture template, `PULSE_INDEX.md` cadence legend)
2. Do NOT overwrite identity files with generic content from a different directory
3. If a file's identity is unclear, read its current content before templating it
4. Always backup before bulk rewrite; backup path: `<vault>/.archive/index_backup_YYYY-MM-DD/`

## Schema Mismatch: ops-lint vs canonical index format

The current ops-lint linter (`scripts/ops_index_lint_sync.py` — merged) enforces a **different universal schema** than the canonical index format:

| Field | ops-lint expects | canonical format expects |
|-------|-----------------|--------------------------|
| Identity | `name`, `type`, `status`, `owner`, `cadence`, `data_quality`, `last_updated` | `name`, `type`, `status`, `domain`, `last_updated`, `total_files`, `index_first_rule`, `auto_update`, `stale_check`, `refresh_cadence`, `maintained_by` |
| Static bonus | `last_reviewed` | `owner` (optional), `scope`, `related_paths` |

**Resolution priority:**
- For index files: canonical format wins (user-defined standard)
- For log/wiki content files: ops-lint schema wins (linter contract)
- When both apply: include BOTH sets of fields, mark linter-only fields as optional in index context
- Do NOT silently drop `domain`, `scope`, `index_first_rule`, `auto_update`, `stale_check`, `refresh_cadence`, `maintained_by` from index files
- If ops-lint flags index files for missing `cadence`/`data_quality`, that's a false-positive — ignore for index files, fix only for content files

## Pitfalls

- **Schema mismatch with ops-lint**: ops-lint enforces `cadence`/`data_quality` as required universal fields. Index files should use the canonical format; ignore linter's missing-field warnings for index-specific fields (`domain`, `scope`, `index_first_rule`, `auto_update`, `stale_check`, `refresh_cadence`, `maintained_by`). File linter-only fields as optional in index context.
- **YAML parse errors cascade**: A single malformed index frontmatter causes the linter to report 175+ false-positive `Missing fields` across all other files, because `yaml.safe_load` fails on the bad file and the linter treats its fields as absent. **Always verify YAML parse immediately after writing an index file**:
  ```bash
  python3 -c "import yaml; fm=open('file.md').read().split('---',2)[1]; yaml.safe_load(fm); print('YAML OK')"
  ```
- **Duplicate frontmatter blocks**: Many files contain two `---` blocks back-to-back. The linter flags these. When encountered, preserve the first valid block and strip the duplicate.
- **Case schema fragmentation**: Two schemas coexist. When backfilling case files: derive `slug` from filename, default `priority` to MEDIUM (HIGH if name contains PCCC/relaunch/lu5), add empty `follow_up`.
- **Cross-profile identity loss**: Bulk index rewrites can overwrite domain-specific identity files (e.g. `_growth/_INDEX.md` knowledge-capture template) with generic index content. **Rule**: only template files whose identity is confirmed; read first, template second.
- **Absolute paths on Windows**: vault at `Documents/Warren_OS_Local` is outside Hermes workspace. `execute_code` bypasses write restrictions; terminal inside vault directory works for git/shell.

## Verification

After edit:
1. Run the watchdog script; expect "Synced ..." or "Index already up-to-date."
2. Confirm no unmatched "has no last_updated" flags remain.
3. Confirm command Step 1 counts match index row count.

## Related

- `references/canonical-index-format.md` — canonical template for all index files across profiles.
- `vault/10_OPERATION_DATA/OPERATION_INDEX.md` — Update Protocol section is the active contract.
- `vault/scripts/ops_index_lint_sync.py` — merged execution script (ops-index-sync + ops-lint).
- `vault/00_CORE_LOGIC/CONTEXT.md` §4 (Data Cadence, Automations & Commands) — SSOT cho commands, đã thay thế HERMES_COMMANDS.md.

## Cross-Profile Consistency

When updating index format in one profile, check the other profile for matching indexes that need the same schema update. The canonical format applies to warren-profile and personal-profile indexes.

## Agent Workspace Authority

```text
99_HERMES_AGENT_WORKSPACE/     = Hermes-internal SOPs, rules, indexes, scratch
30_KNOWLEDGE_BASE/wiki/        = human-facing knowledge base (Warren/docs)
hermes_* prefix                = canonical inside agent workspace
```

Do not write WIP/tracking/scratch into `30_KNOWLEDGE_BASE/wiki/`. Use the agent workspace instead.