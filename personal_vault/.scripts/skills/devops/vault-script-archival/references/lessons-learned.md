# Phase 2A & 2B Lessons Learned

## Phase 2A — Success (18 scripts archived, 53 → 35, -34%)

### What Worked
- Explicit archive list variable — no glob surprises
- Two STOP gates (existence + imports) caught issues before any writes
- Dated archive folder (2026-06_phase2) — easy to find, versioned
- README in archive folder with rollback instructions — self-documenting
- Single commit — instant full rollback via `git revert`
- Report in `_kilo/.archive/` — permanent record outside git history

### Patterns for Reuse
- Naming convention signals: "debug_", "test_", "fix_", "setup_" = one-shot → HIGH confidence
- "may" in name = time-bound one-shot (gsheet_google_review_may.py)
- Feature disabled + scripts for it = safe archive (drive_sync.*)
- Exact duplicates (.bat vs .ps1) = safe archive

## Phase 2B — STOP (3 scripts NOT archived)

### What Blocked It
Import check found active references in CI pipeline:
- `gsheet_to_vault.py` — conditional imports for `google_review_parser.py` and `grabfood_parser.py`
- `gsheet_config.json` — `enabled: true` for both
- `generate_brief.py` — kanban task references `google_review_parser.py`
- CI workflows (not searched but implied) call `gsheet_to_vault.py` daily/weekly

### Root Cause
Pivot to "direct GSheet access" was a decision, not an implementation. The old pipeline (CSV → parser → MD) was still wired in config + code.

### Correct Deferred Action Path
If pivot is real:
1. Update `gsheet_to_vault.py` to fetch directly (remove parser imports)
2. Set `enabled: false` in `gsheet_config.json`
3. Run CI for 7 days — verify no errors
4. **Then** archive parsers with clean import check

### Pattern: "Decision ≠ Implementation"
User decisions about architecture often outpace code changes. Always verify the code matches the decision before archiving.

## Risk Confidence Framework

| Confidence | Signal | Example |
|------------|--------|---------|
| HIGH | Naming convention (debug/test/fix/setup) + not in CI | debug_slack.py |
| HIGH | Feature flag disabled in config + no CI reference | drive_sync.ps1 |
| HIGH | Exact duplicate of kept file | sync_rules.bat |
| MEDIUM | Warren says "not used (NO-but-might)" | process_voice.py |
| LOW | Referenced in active config/code/CI | grabfood_parser.py |

## Quick Reference: STOP Conditions

| Gate | Command | Exit if |
|------|---------|---------|
| Existence | `[ -f "vault/scripts/$f" ]` | Any MISSING |
| Imports | `grep -r "import $stem\|from $stem" vault/scripts/ .github/workflows/ vault/_kilo/` | Any hit outside file itself |
| Counts | `ls vault/scripts/*.py ... | wc -l` | Differs ±2 from expected |

## Archive Folder Naming Convention
`vault/scripts/.archive/YYYY-MM_phaseN/`
- YYYY-MM = year-month of archive
- phaseN = phase identifier (1A, 1B, 2A, 2B, etc.)
- Consistent across phases for easy discovery

## Rollback Time Targets
- Single file: < 30 seconds (`git mv`)
- Full phase: < 60 seconds (`git revert <hash>`)
- Both tested and working in Phase 2A