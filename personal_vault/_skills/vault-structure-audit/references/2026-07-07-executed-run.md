# 2026-07-07 — WIKI INDEX Phantom Cleanup (15 entries)

**Trigger:** `/vault-structure-audit` dry-run → discovered 15 phantom WIKI_INDEX entries
**Mode:** `--execute` (targeted — only Phase 1F fix)
**Fixes by:** Hermes

## Summary

Fixed 15 phantom entries in `00_WIKI_INDEX.md` that referenced files not at the listed paths. 9 were path-shift issues (files moved to `SOP/` or `POLICY/` subfolders during June restructure), 6 were truly deleted/never-created files.

## Changes Made

| Count | Fix Type | Files |
|-------|----------|-------|
| 9 | Path corrected | SOP files → `SOP/` subfolder (6) or `POLICY/` subfolder (3) |
| 6 | Row deleted | Truly missing files (CEO_COL_Report_Template, Workflow_Guide_NonIT, Lessons_Learned, Profit_Loss_Analysis, Q1_2026_Store_P&L, Rent_Occupancy_Cost) |
| 3 | Pipe bug fixed | `|| ` → `| ` on GF_Channel_PL, GF_Trend_Dashboard, GF_Rolling_Tracker |
| 1 | total_files updated | 111 → 105 |
| 1 | Duplicate removed | LU3_Profile appeared twice (patch tool fuzzy-match artifact) |

## Bugs Encountered & Fixes

### 1. Pipe Concatenation (old bug, hit again)
When patching markdown table rows, the new_string's opening `|` concatenated with the preceding row's closing `|`, producing `|| ` instead of `| `. Fixed by patching each line individually.

### 2. Patch Tool Row Duplication (NEW)
When deleting 3 phantom rows + blank line near LU3_Profile, the patch tool's fuzzy matcher matched the opening region (including LU3_Profile near the phantom rows) instead of just the target region, duplicating the LU3_Profile entry. Had to detect and delete the duplicate separately.

### 3. sed Backtick Issue
Initial sed command `sed -i 's/^||| `/| `/'` failed because bash can't handle backticks inside single quotes on MSYS. Switched to patch tool (line-by-line), then later used Python for the final fix.

### 4. execute_code Blocked
Tried to use `execute_code` for a Python-based bulk fix but got blocked by cron_mode restriction. Had to use individual `patch` calls instead.

## Verification

- Section 02 (SOP): all 9 rows start with `| `, paths point to `SOP/` or `POLICY/` subfolders
- Section 04 (labour): CEO_COL_Report_Template removed, no blank lines
- Section 06 (ops): 5 phantom rows removed, pipe bug fixed, no duplicate entries
- total_files: 105 (matches actual indexed count)
- last_updated: 2026-07-07
