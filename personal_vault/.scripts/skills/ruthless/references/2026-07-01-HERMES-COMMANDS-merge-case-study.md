# 2026-07-01: HERMES_COMMANDS.md consolidation into CONTEXT.md §4

## Summary

- **Source:** `00_CORE_LOGIC/HERMES_COMMANDS.md` (112 lines, standalone SSOT cho commands)
- **Target:** `00_CORE_LOGIC/CONTEXT.md` §4 — Data Cadence, Automations & Commands
- **Verdict:** DELETE — absorbed into CONTEXT.md §4C (Command Quick Map) + §4B (Scheduled Automations)
- **File deleted?** Yes — not just deprecated, permanently removed

## Why

HERMES_COMMANDS.md had 4 sections:
1. IDEAS & CREATIVITY — `/brainstorm`, `/ruthless`, `/explore`, `/generate-plan`
2. DATA INGEST — `/ops-ingest`, `/ops-process-notes`, `/capture`
3. OPERATIONS & DECISIONS — `/ops-morning-brief`, `/ops-deep-research`, `/ops-cases`, etc.
4. REVIEW & QUALITY — `/ops-lint`, `/restate`, `/review-plan`, etc.
5. ROUTINE / CRON-DRIVEN — cron schedule table (overlapped with CONTEXT §4B)
6. COMMAND QUICK MAP — 15-row "cần làm gì → gõ lệnh gì" table

Problems:
- **Cron schedule existed in 2 places** (HERMES §5 + CONTEXT §4B) — different format, same data
- **Detailed command specs** (§1-4) were never read by Warren (non-IT, only uses quick map)
- **Hermes already knew commands from skills/SOUL** — the specs were low-value
- **Only the Quick Map had real daily value** (15 rows, what Warren actually uses)

## Merge approach

### What moved to CONTEXT.md §4

**§4B Scheduled Automations (SSOT):**
- Merged missing cron: Daily Case Sweep, Daily Today Revenue, Daily TODAY Regeneration, Auto Process-Logs GSheet
- Added Script/Skill column (was missing in original CONTEXT table)
- Standardized names: "Weekly Lint" → "Weekly Vault Lint"

**§4C Command Quick Map (new subsection):**
- All 15 rows from HERMES §6
- Dropped merged/strikethrough commands (ops-context-update, ops-weekly-connections)
- Added `/brainstorm` and `/ruthless` (were in §1 but missing from original Quick Map)

### What was discarded (not moved)
- Detailed command specs (§1-4 with "khi nào dùng + tác dụng + file ảnh hưởng") — low-value
- "Format mỗi entry" and "Ghi chú" sections — informational only, not actionable

### Reference updates
| File | Change |
|------|--------|
| `tidy/SKILL.md` | `HERMES_COMMANDS.md` → `CONTEXT.md §4` |
| `vault-index-sync/SKILL.md` | `HERMES_COMMANDS.md §5` → `CONTEXT.md §4` |
| `CONTEXT.md` deprecated command-index ref | `[[deprecated]]` → `See §4 bên dưới` |

### What was kept as-is (intentional)
- `audit-automation/SKILL.md` — generic heuristic, not a file reference
- `ruthless/references/*.md` — historical records (document past states)

## Pattern: File-to-section merge (vs skill-to-skill merge)

This was a different consolidation pattern from ops-lint/ops-index-sync:

| Aspect | Skill merge (ops-lint + ops-index-sync) | File-to-section merge (HERMES_COMMANDS → CONTEXT) |
|--------|----------------------------------------|---------------------------------------------------|
| What moved | Code + logic → unified script | Content → parent file subsection |
| Source | Skill (SKILL.md + scripts) | Standalone .md file |
| Target | New merged script | Existing parent file |
| Deletion | Source skill marked deprecated | Source file **deleted completely** |
| Risk | Low (skills are execution layer) | Low (content is informational, not executable) |

## Verification

1. `git add -A && git commit` — 5 files changed, 114 insertions, 136 deletions
2. `git push` — master updated
3. Searched vault + skills for remaining `HERMES_COMMANDS` refs — only intentional notes remain (historical records, replacement notice)
4. Checked for `[[HERMES_COMMANDS]]` wikilinks — zero found

## Key learning: Warren's deletion criteria

Warren agreed to delete (not just deprecate) after being asked and answering these questions:
1. **Tác dụng gì?** — Single source of truth for commands
2. **Sao tồn tại?** — Replaced a deprecated command-index file; now redundant with CONTEXT §4
3. **Tốt cho ai?** — Both Hermes + Warren, but value already in CONTEXT §4 or skills
4. **Xoá được ko?** — Yes, if all content absorbed + references updated + verified
