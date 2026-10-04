# 2026-07-10 — P&L Wiki Cascade Delete (case study / recipe)

## Trigger
Warren: "delete hết mấy cái này luôn được ko? nếu được, xóa luôn" — 5 P&L wiki pages:
`PL_Variance_Tracker_2026.md`, `analysis/Breakeven_Analysis.md`,
`analysis/Q1_2026_Consolidated_P&L.md`, `analysis/Rent_Fixed_Costs.md`,
`analysis/Staffing_Breakeven_Implications.md`.

## Lesson
Warren underestimated blast radius ("đâu có ảnh hưởng gì"). Actual: 48 active files held
`- [[Name]]` list-items (143 lines) + WIKI_GRAPH / FRONTMATTER_CACHE / INDEX entries.
Deleting without cascade = vault full of red broken links.

## Reusable recipe
1. **Find referencers**: `search_files` each PageName across `vault/`; also inspect
   `WIKI_GRAPH.json`, `FRONTMATTER_CACHE.json`, `00_WIKI_INDEX.md`, `*_Hub.md`.
2. **Delete targets** (PowerShell preferred; `&` in `01_P&L_Budget` breaks `cd` → use absolute quoted path):
   ```powershell
   Remove-Item -LiteralPath 'C:/Users/khoans/Documents/Warren_OS_Local/vault/30_KNOWLEDGE_BASE/wiki/01_P&L_Budget/PL_Variance_Tracker_2026.md' -Force
   ```
   # fallback that worked this session: `rm -f "/absolute/quoted/File.md"`
3. **Strip broken list-items across ACTIVE files only** (skip `10_archive`):
   temp script, regex `^\s*-\s*\[\[(NAME1|NAME2|...)\]\]\s*$`,
   `rglob('*.md')` under `wiki/`, drop matching lines, rewrite file.
4. **Regenerate**: `python scripts/rebuild_wiki_index.py --graph --frontmatter`
   (rewrites graph + cache + index from disk; removes dead nodes/edges).
5. **Verify**: `search_files [[Name]]` over `wiki/` → 0 active hits (archive allowed).
6. **Ad-hoc verify** script under `%TEMP%` (`hermes-verify-*.py`), run, `rm` immediately.

## Outcome
5 files deleted, 143 lines cleaned in 48 files, graph+cache+index regenerated clean.
Data note: `PL_Variance_Tracker_2026` was a standalone "Actuals vs CFO Target" tracker
(NOT in SSOT `13_Monthly_PL_Breakdown.md`) — deleting it loses that tracker permanently;
need CFO to resend source if ever wanted again.
