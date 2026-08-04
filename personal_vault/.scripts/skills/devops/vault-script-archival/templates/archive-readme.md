# Phase N — Archived Scripts (YYYY-MM-DD)

## Why archived
- Not called by CI (.github/workflows/)
- Not imported by other scripts
- Warren confirmed not used in last 30 days (audit interview)

## Rollback
Single file: git mv vault/scripts/.archive/YYYY-MM_phaseN/<file> vault/scripts/<file>
All: git revert <commit-hash>

## Archived files (N total)

| File | Reason archived |
|---|---|
| debug_slack.py | "debug" name = one-shot, not in CI |
| test_gsheet.py | "test" name = one-shot |
| fix_recipe_index.py | "fix" name = one-shot |
| diacritics_check.py | One-shot check, not CI |
| setup-hooks.ps1 | Setup script, runs once |
| setup_slack_tokens.ps1 | Setup script, runs once |
| sync_rules.bat | Duplicate of sync_rules.ps1 (kept) |
| drive_sync.ps1 | Drive Backup disabled Phase 1D |
| run_drive_sync.cmd | Drive Backup disabled Phase 1D |
| process_voice.py | Warren: not used (NO-but-might) |
| index_vault_to_qdrant.py | Warren: not used (NO-but-might), no Docker setup |
| build_frontmatter_cache.py | Wiki dup: kept rebuild_wiki_index.py only |
| convert_wiki_index_links.py | Wiki dup |
| inject_wiki_links.py | Wiki dup |
| rebuild_wiki_graph.py | Wiki dup |
| wiki_index_updater.mjs | Wiki dup |
| ops_index_watchdog.py | Wiki dup |
| gsheet_google_review_may.py | "may" in name = one-shot for May 2026 |