# L'Usine Parser Pitfalls — Complete Reference

> **Full catalog of every parser pitfall encountered in production.**
> Main skill keeps top 8; this file has the complete 50+ entries.
> Last updated: 2026-07-21

---

| Issue | Fix |
|-------|-----|
| IndentationError in generated code | Use `write_file` not incremental patches for new parsers |
| ModuleNotFoundError: yaml | Install `pyyaml` in Python environment |
| KeyError: 'iso_week-1' | Use f-strings not `.format()` for template strings |
| Frontmatter duplication | Always strip old frontmatter before prepending new body |
| "source" / "parser" extra fields | Pop unexpected fields after `validate_and_sync_frontmatter()` |
| **GSheet merged cells → empty values** | Implement **forward-fill**: track `current_item_group`, update when cell has value, inherit when empty. Skip "Total" rows (item_name contains "Total"). See `luso-parsers` → `references/gsheet-merged-cells-forward-fill.md` |
| **`infer_category()` display vs price-target use** | `infer_category()` is for **price targets only** (Item Flags). **NEVER** use for display (Item Group column, Top group). Display must show raw sheet data or `—`/`Uncategorized` |
| **Store Breakdown 4-column + insight format** | Group by Item Group (not per-item), columns: Item Group | Qty | Revenue | Avg Price | % of Store. Follow with insight line. |
| **`patch` corrupts indentation on large blocks** | Use `terminal + python3 -c '...'` or a temp `.py` script instead of `patch` for multi-line replacements. `patch` is reliable for single-line/small blocks only. |
| **Monthly parsers: `--month` CLI override** | Monthly parsers (COGS, Wage, Wastage) should accept `--month YYYY-MM` so they can write entries for non-current months. Pattern: `argparse` → `--month` → split `YYYY-MM` → `date(int(y), int(m), 1)`. Fallback to `date.today().replace(day=1)`. |
| **Revenue display truncation: `int(value/1e6):.1f`** | `int()` truncates toward zero: `int(688.91972)` → `688`. Format `:.1f` displays `688.0` — losing up to 999,999 VND per store. **Fix**: remove `int()`, let `:.1f` round naturally: `f"{sys_r/1e6:.1f}tr"` produces `"688.9tr"`. Search all `int(x/1e6):.1f` in parser code and replace with `x/1e6:.1f`. |
| **Markdown table column alignment (pipe count)** | After writing any markdown table, verify pipe count matches header. Count `|` on header row vs data row. Common bug: missing closing pipe on first column shifts all data by one column. |
| **Missing table separator row (`---|---|---|`)** | Every markdown table needs a header separator line. Without it, Obsidian/GitHub render raw `|` pipes. Auto-fix in parser code: add `f"|{'---|' * col_count}"` after every table header row. |
| **Month name mapping duplicated across functions** | Extract `MONTH_NAMES` dict as module-level constant. Add `_parse_month(month)` helper instead of redefining in every function. |
| **GSheet date parsing: gviz returns Date(2026,4,15) format** | Use `parse_gviz_date()` from `_utils` -- handles both gviz Date() and ISO formats. Month in gviz is 0-indexed (4 = May). |
| **`_utils.py` lives in TWO locations** | `vault/scripts/_utils.py` has `fetch_gviz()` (HTTP/gviz). `vault/10_OPERATION_DATA/scripts/modules/_utils.py` has `fetch_gviz()` + `fetch_sheets_api()` (service account). Know which functions exist where. |
| **GSheet column date labels use MM/DD/YYYY** | Column names like `Period: from 6/22/2026 to 6/28/2026` use US month-first format. Fix: `f"{parts[2]}-{int(parts[0]):02d}-{int(parts[1]):02d}"` → `2026-06-22`. |
| **COGS ingredient names have /Vietnamese translations** | `Recipe_Index.json` ingredient names may include Vietnamese after `/`. Fix: Normalize both by splitting on `/` and taking first part: `name.split("/")[0].strip().lower()`. |
| **Deep copy recipe lookup before adjusting costs** | When modifying recipe costs based on COGS changes, `dict(original_dict)` only does a shallow copy. Use `copy.deepcopy()` to preserve originals for delta display. |
| **Accumulation JSON file accumulates orphan week keys** | Old-format keys with empty `items: {}` persist and corrupt `_metadata.months`. Fix: Add auto-clean in `accumulate_week()`: remove any week key where `items` is empty/falsy. |
| **MoM delta via `re.split` on month headers, not `re.search`** | `re.search` finds the FIRST match. Fix: split on month headers `re.split(r"\n(?=## \d{4}-\d{2} \|)", content)`, iterate sections, skip current month, take first older section. |
| **`build_entry()` pre-computed params to avoid double calculation** | When `main()` and `build_entry()` both compute the same metric, pass optional param: `def build_entry(..., total_gp_pct=None)`. |
| **Template fallback columns: `—` not proxy estimates** | When data source lacks per-store breakdown, fill with `—` not system-level proxy estimates. Proxy values mislead readers. |
| **Flags section: iterate ALL items, don't break on first match** | When generating flag bullets, `break` exits after the first flag. Fix: `continue` (or remove `break`). |
| **Cross-check revenue: match specific week, not all weeks** | When cross-checking Star Horse vs Revenue Log for a monthly parser, only compare the specific week that Star Horse data covers. Summing ALL RevLog weeks gives YTD totals that will always fail the ±4% gate. |
| **COGS log has two June 2026 sections (summary + detail)** | Priority: match `## YYYY-MM |` format first (has the detailed ingredient price tables). Fallback to `## MM/YYYY |`. |
| **Markdown table format varies by month for same data** | Old entries (March) may have extra columns. Use number heuristics: `num > 30` to find OT, not Staff count. |
| **Week date range formats are inconsistent** | Covers file uses 3 formats: DD/MM-DD/MM/YYYY (em dash), YYYY-MM-DD -> YYYY-MM-DD (ISO), single date. Use helper that tries ISO first, then DD/MM. |
| **D1 row label varies: `**D1**` vs `**Sum**`** | Older weeks may label the totals row `**Sum**` instead of `**D1**`. Both are valid. Match both. |
| **D1 semantics differ by week: regular vs actual covers** | W14-W18 old format has split orders in D1 comment. W19+ no split → D1 IS actual covers. Do NOT blindly add split orders to every D1. Parse the context. |
| **ALL section D1 row attributed to LU7** | When iterating store hourly tables, `### ALL -- System Summary` also has a D1 row. Fix: reset `current_store = None` on any `###` line that doesn't match LU3/LU5/LU7. |
| **`--month` must propagate through to write logic, not just fetch** | Monthly parsers accept `--month YYYY-MM` but the flag may only filter data fetching, not writing. Fix: pass target month as parameter to write function. |
| **Shortage/Surplus split in Inventory Reconciliation** | NEVER sum SHORTAGE and SURPLUS together. Separate `cat_sh` (recon < 0) from `cat_surplus` (recon > 0). |
| **HTML dashboard gen: avoid f-string + JS `${}` conflict** | Use `.replace()` on a static HTML template string instead of f-strings. Define HTML as module-level `_TEMPLATE` constant with `{PLACEHOLDER}` markers. |
| **Delta parser: reading previous month from old-format entries** | Write a `read_prev_month_entry()` function that tries multiple parse strategies in order. Always isolate the section first via `## YYYY-MM` regex. |
| **Data sheet per-store identifier** | CFO's turnover report has store info in column 32 as location codes like `LU3-BAR`. Parse column 32 via string match, do NOT rely on column 33 being populated. |
| **COGS Food/Beverage split via Account column** | Use Account column (col 34) to classify items as Food, Beverage, Chemical, etc. Aggregate `food_cogs` and `bev_cogs` separately. |
| **After writing new month rows, verify chronological order** | Sort `month_rows` by month index before writing, or collect ALL rows (existing + new) and re-sort. |
| **Δ MoM should use file data as baseline, not computed data** | When file already has authoritative month data and parser computes different numbers, Δ MoM = (new_current - file_prev) / file_prev. |
| **`--force` only overwrites month rows, not YTD/Executive Summary** | After `--force`, recompute YTD from scratch based on ALL rows present. |
| **write_index with state-machine boolean flags is fragile** | Better pattern: section-anchored rebuild. Find table header → insert new rows → skip original rows → preserve everything else. Single-pass, no flags. |
| **HTML comments in data file treated as parser template** | Use `[//]: # (...)` (markdown comment) instead of `<!-- ... -->` (HTML comment) for non-template annotations. |
| **Nested JSON in `<!-- gf_data -->` blocks — regex `[^}]+` fails** | Use a brace counter: walk forward counting `{`/`}`, extract substring when depth returns to 0. |
| **Chart.js scope bug: function can't access local variable** | Pass data as parameter: `function getDataset(weeks, key, label, color)`. |
| **Chart.js instance cleanup: `Chart.instances` is not a real API** | Manage instances with an array: `let charts = [];` push on create, destroy all on re-render. |
| **Inline CSS `color=` vs `color:`** | In HTML inline styles, use `:` not `=`: `style="color:#1B5E20;"` CORRECT. |
| **Deriving chart data from WEEKS object (pluck helper)** | Use a single `pluck(key, store)` helper instead of 11+ flat arrays. |
| **Cross-check actual covers against Revenue Log** | After computing `actual = gross - split`, verify against `01_Weekly_Revenue_Log.md`. Flag if >5% diff. |
| **`created` frontmatter field: auto-inject ONCE, never overwrite** | `validate_and_sync_frontmatter()` MUST set `created` on first write and PRESERVE it on every re-run. |
| **CRLF `---created:` gluing bug (backfill trap)** | Never slice `txt[:3]`. Inject after opening delimiter with regex matching `---\r?\n`. Use `write_frontmatter()` helper. |
| **Backfilling many files: re-verify ALL after, never `git reset --hard` mixed commit** | Follow backfill with YAML-parse loop over every touched file. Undo surgically, never `git reset --hard` on mixed commits. |
