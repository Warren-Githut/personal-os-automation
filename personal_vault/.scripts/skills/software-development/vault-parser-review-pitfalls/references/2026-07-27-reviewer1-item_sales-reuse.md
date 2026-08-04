# REVIEWER-1 Code-Reuse findings — item_sales_sql_parser.py (2026-07-27)

Scope: `vault/.scripts/item_sales_sql_parser.py` (397 lines) + `vault/30_KNOWLEDGE_BASE/wiki/dashboards/item_sales_trend.html`.
Compared against `vault/.scripts/_utils.py`, `_week_utils.py`, and sibling SQL parsers in `vault/10_OPERATION_DATA/.parsers/`.

Chesterton's Fence: `git blame` → entire file authored in ONE commit `7f9ef992`
(2026-07-27 11:06, author ORION). Duplication is from initial authoring — no
deliberate divergence, no historical "fence". Safe to dedupe.

## Findings (file:line → problem → cost → fix | confidence | risk)

F1 SAFE — `iso_week(d)` (L47-49, `return f"{y}-W{w:02d}"`) is byte-exact dup of
`_utils.make_week_id()` (`_utils.py:90-92`) and `_week_utils.make_week_id()`
(`_week_utils.py:42-44`). 3 lines dead, week-id format drift risk.
Fix: `from _utils import make_week_id` (same `.scripts/` dir) and replace calls.
Confidence HIGH · Risk SAFE.

F2 CAREFUL — `NET_FACTOR = 0.882` (L28) redefined in revenue_sql_parser.py:35,
hourly_cover_sql_parser.py:43, lto_sql_parser.py:28, build_item_sales_dashboard_data.py:14,
item_sales_parser.py:59 (`NET_REVENUE_FACTOR`). Canonical net=0.882 in 5+ places.
Fix: promote to one shared constant (new `_sql_common.py` or `_utils.py`), import.
Confidence HIGH · Risk CAREFUL (touch all files; verify rename in item_sales_parser.py).

F3 CAREFUL — `STORE_MAP`/`STORES` (L29-30) redefined in revenue_sql_parser.py:36-37,
hourly_cover_sql_parser.py:45-46, lto_sql_parser.py. Fix: shared
`STORE_MAP={"LSLTT":"LU3",...}`, `STORES=[...]`. Confidence HIGH · Risk CAREFUL.

F4 CAREFUL — `_run_sql()`/`_setup_sql_env()` sqlclient wiring (L16-26) reimplemented
verbatim in revenue_sql_parser.py:43-58, hourly_cover_sql_parser.py:57-69,
lto_sql_parser.py:34-47. No shared wrapper exists yet. Fix: extract one `run_sql()`
(load_env + `MSSQL_DATABASE=iikoAPI` + `sqlclient.run_query`) → `_sql_common.py`,
call it. Confidence HIGH · Risk CAREFUL (central to firewall — test after).

F5 RISKY — `upsert_week()` (L270-325) vs `_utils.insert_or_replace_weekly()`
(`_utils.py:141-154`). Both newest-on-top replace, but `upsert_week` also preserves
the `📊 **Dashboard:**` link line AND repositions backfilled weeks under the top entry.
`insert_or_replace_weekly` strips to `---` separators, drops the dashboard link.
Fix: NOT drop-in; extend shared fn with `preserve_lines` hook or leave as-is.
Confidence MED · Risk RISKY (naive swap drops dashboard link).

F6 CAREFUL — `monday_of(d)` (L56-57) ≈ `_week_utils.current_week_bounds()[0]` ONLY
when `d == today` (its single call site L349 is `monday_of(today)`). For an arbitrary
date there is no exact shared fn. Fix: `monday_of(today)` → `current_week_bounds()[0]`.
Confidence MED · Risk CAREFUL (valid only for the `today` call site).

F7 CAREFUL — `week_bounds(monday)` (L51-53) returns `(monday, monday+6)`. Shared
`_utils.week_bounds()` is today-relative; `_week_utils.prev_week_bounds()` computes a
*previous* week, not `(monday, sunday)`. No exact shared equivalent. Fix: leave or add
`week_bounds_of(monday)` to `_week_utils`. Confidence MED · Risk CAREFUL.

F8 CAREFUL (file-level) — `gen_item_sales_dashboard.py` is a DEAD/orphan dashboard
generator for the SAME tracker. It injects `__PAYLOAD__` and expects schema
`{weeks, current.System, qty_series, ...}` (L32-93), incompatible with the live
SQL-parser `--emit-html` path which injects `__PAYLOADS__` with schema
`{week, system, stores, bcg, scatter, cost_missing}`. Two generators, two schemas, one
HTML file. The SQL parser `--emit-html` is the one wired to `item_sales_trend.html`
(the committed built file inlines a `PAYLOADS` array, the template lives in
`_archives/dashboards/item_sales_trend_template_2026-07-27.html`). Fix: confirm live
pipeline, archive the dead generator. Confidence MED · Risk CAREFUL.

## Secondary note
`item_sales_trend.html` is a ~478 KB committed BUILT file (data inlined). The
`__PAYLOADS__` placeholder lives only in its template. No code-reuse defect in the HTML
itself beyond the schema split noted in F8 (full treatment in SKILL.md §16).

## Files changed this session
None — REVIEWER-1 was read-only (report only, no patches).
