---
name: vault-link-hygiene
description: "Audit and fix broken [[wikilinks]] in an Obsidian vault WITHOUT over-reporting. Obsidian resolves [[Target]] by basename across the whole vault, so a naive exact-path check false-positives 5-50x. Reusable classify-then-rewrite method + false-positive taxonomy + safe Python pathlib bulk rewrite. Use when a vault-structure-audit flags broken links, or before cleaning a link graph."
version: 1.0.0
author: Hermes
trigger: "/vault-link-hygiene [--dry-run] [--fix]"
category: devops
---

# /vault-link-hygiene — Broken [[wikilink]] Audit & Safe Rewrite

> **Why this skill exists:** A 2026-07-20 Monday vault-health-check ran a naive broken-link scan
> (`grep '\[\[..\]\]'` + exact-path-exists) and reported **500 broken across 99 files**. After
> resolving links the Obsidian way (basename, whole-vault), the REAL broken count was **~37 targets**.
> The naive method was 13x wrong. This skill encodes the correct method so future runs don't
> waste an hour on false positives or (worse) delete valid links.

## Core rule (do NOT skip)

**Obsidian resolves `[[Target]]` by basename, not by exact path.** `[[OIL_Tracking]]` from
`10_OPERATION_DATA/02_HR_Weekly_Log.md` correctly points to
`30_KNOWLEDGE_BASE/wiki/04_labour_costs/OIL_Tracking.md` even though the path differs. Any check
that does `os.path.exists(target_path_as_written)` will flag this as broken — falsely.

## Method (3 passes)

### Pass 1 — Build basename index
```python
import os, glob
os.chdir(VAULT)
files = [f for f in glob.glob('**/*.md', recursive=True) if '.git' not in f]
basemap = {}
for f in files:
    stem = os.path.splitext(os.path.basename(f))[0].lower()
    basemap.setdefault(stem, []).append(os.path.normpath(f))
```

### Pass 2 — Classify each UNIQUE `[[target]]` (not every occurrence)
For each link target `t`:
- `base = os.path.basename(t).lower()`, strip trailing `.md`
- If `base in basemap` → **OK (false positive if naive flagged it)**
- If `.html` suffix → search for the `.html` file anywhere; if exists → **convert to `file:///` URL** (see taxonomy); if missing → real broken
- If `.csv` suffix → usually a data artifact in `._assets/`; **ignore** (not a wiki link)
- Else → **GONE** (file truly deleted/renamed) → candidate for removal

### Pass 3 — Exclude these from "broken" (false-positive taxonomy)
| Class | Example | Action |
|-------|---------|--------|
| HTML dashboard exists | `[[COL_Trend_Dashboard.html]]` → file present | Convert `[[X.html]]` → `[X](file:///abs/path)` (Warren convention 2026-07-20: dashboards use `file:///`, NOT wikilinks) |
| CSV in `._assets/` | `13_Monthly_PL_Breakdown_2026_01_data.csv` | Ignore (data artifact, hidden dotfolder) |
| Folder link | `[[04_labour_costs/]]` | OK — Obsidian supports folder links |
| Placeholder docs | `<file>.html`, `<wikilink>`, `...` | Ignore (literal doc text) |
| Path-form to existing | `[[08_menu_cogs/Menu_Engineering.md]]` where file exists at that path | OK |
| Historical snapshots | `_archives/memory/WARREN_MEMORY_*.md`, `.archive/` backups | **EXCLUDE entirely** — do not rewrite history |

## Safe bulk rewrite (Windows MSYS — NO patch tool)

Use Python `pathlib` with **raw-string Windows paths**. The `patch` tool misfires on CRLF `.md`
(phantom multi-match) and on `/c/` MSYS prefixes. See `references/broken-link-audit-rewrite.md`
for the full working script (classify → dry-run count → exec → re-verify).

Rules:
- Preserve display text: `[[Target|alias]]` → keep `alias`; `[[Target]]` → keep `Target` (don't delete to empty)
- Convert HTML: `[label](file:///C:/.../X.html)`
- Skip dirs: `_archives/memory`, `.archive`
- After rewrite, **re-run the checker** to confirm 0 real broken remain; spot-check 2-3 converted files

## Pitfalls
- **Naive grep over-reports 10x+.** Always basename-resolve before declaring broken.
- **Don't touch `_archives/memory/`** — those are compressed memory snapshots; rewriting breaks history.
- **`search_files` lies on Windows** (stale cache / IO errors) — use `terminal` `find`/`grep` for ground truth on disk.
- **`patch` tool on CRLF `.md`** → phantom matches; prefer Python `pathlib` for bulk edits.
- **GONE list must strip `.md` suffix** before set-membership check, OR the check misses `path/form/Target.md` style links (basename still matches).

## References
- `references/broken-link-audit-rewrite.md` — full reusable Python script (classify + dry-run + exec + verify) from the 2026-07-20 run.
