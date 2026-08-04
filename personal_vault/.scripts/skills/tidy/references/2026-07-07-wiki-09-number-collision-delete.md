---
created: 2026-07-07
type: case-study
topic: wiki numbered-folder collision + dead shell deletion
---

# Case: 09_connections/ vs 09_hourly_cover_revenue/ (2026-07-07)

## Trigger
Warren noticed 2 wiki folders both prefixed `09`. Turned out to be a rename collision:
- `09_hourly_cover_revenue/` — real dashboard, used daily. Valid.
- `09_connections/` — originally `_connections/` (FRONTMATTER_CACHE.json still had `wiki/_connections/_CONNECTIONS_Hub.md`). Someone slapped `09_` on it, colliding with the dashboard.

## Investigation
1. Read `_CONNECTIONS_Hub.md` — self-declared dead: "Cross-domain connections đã merge vào `/ops-weekly-report`... `weekly_connections_log.md` archived."
2. Folder was EMPTY except the Hub shell — zero promoted connection notes.
3. References found: WIKI_INDEX.md (section "10. _connections" + Where-To-Go row), FRONTMATTER_CACHE.json (stale path `_connections`).
4. No cron/skill/ops-data depended on it.

## Decision (Warren approved DELETE)
3 options presented + recommended:
- A [RECOMMENDED] Delete + patch index + remove cache
- B Keep but rename → 10_connections (pointless — empty shell)
- C Keep as-is (collision stays)

## Execution
1. `rm -rf` the folder (empty, no Windows restore issue this time)
2. Patch WIKI_INDEX.md — remove section "10. _connections" + Where-To-Go row
3. Patch FRONTMATTER_CACHE.json — remove stale `wiki/_connections/_CONNECTIONS_Hub.md` block
4. Verify: `search_files` vault-wide for `09_connections | _connections/ | CONNECTIONS_Hub` = 0 matches

## Commit
- `git reset -q HEAD .` then selective `git add` of only 3 target files (avoid sweeping ghost temp + unrelated files)
- battle-test pre-commit hook passed
- push: first attempt timed out (github.com:443), retry succeeded

## Lessons
- **WIKI_INDEX integrity:** add "no two numbered folders share same NN_ prefix" to Wiki health checklist.
- **FRONTMATTER_CACHE.json is a referencer:** when deleting/renaming a wiki file, search the cache by BOTH old and new path names — cache lags reality.
- **Dead-shell signal:** a folder whose own index file says "merged into X, archived" AND contains zero content notes = safe delete.
- **git hygiene:** after writing an ad-hoc verify temp script, delete it in the SAME terminal call. A leaked `hermes-verify-*.py` phantom appeared in `git status` (from a heredoc that created-but-never-consumed the temp file). Caught via `git status --short` before commit; unstaged it.
