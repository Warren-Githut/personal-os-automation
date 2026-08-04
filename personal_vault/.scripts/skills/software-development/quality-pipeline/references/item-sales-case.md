# Case study: Item Sales SQL backfill + quality pipeline (2026-07-27)

Real session that birthed this skill. Condensed for reuse.

## What was built
- `vault/.scripts/item_sales_sql_parser.py` — IKKO SQL → tracker (replaces GSheet Star Horse).
  Added `--live` (idempotent newest-on-top upsert), `build_multiweek_payload()` (sort W18-W29).
- `11_Item_Sales_Weekly_Log_Star_Horse_Tracker.md` — 12 weeks W18-W29, X2 format.
- `item_sales_trend.html` (built) + `item_sales_trend.template.html` (placeholder) — multi-week trend.

## Bugs caught by the pipeline (proof the chain earns its keep)
1. **6 legacy GSheet entries** still in tracker (dup weeks, different numbers) → deleted.
   Cross-week A6 still 100% after delete (SQL untouched).
2. **Template stale risk** — built file overwrote template, killing `__PAYLOADS__`.
   Fixed: template kept separate + `--emit-html` ERR-guards missing placeholder.
3. **Frontmatter stale** (GSheet v2.0) → updated to SQL v3.0.
4. **upsert_week MOVE-UP BUG (reviewer-4 execution-verified)** — re-running an old week
   via `--live` put it ABOVE newest. Verify gate only checked `count==1`. → **Rewrote
   upsert_week as parse-all-blocks → sort-desc-by-ISO-week → rebuild.** Ordering correct
   by construction. Unit test asserts W29 stays on top after re-run.
5. Dead code (`md_entry`, `RUBBISH_MARKER`, `prev_sys_*`, `enumerate if False`,
   `prev_monday`) → deleted. `aggregate` called twice → deduped. `iso_week` → shared
   `make_week_id`. Atomic write + TOCTOU drop. JSON-parse silent `except:pass` → warn.
6. Dead generator `gen_item_sales_dashboard.py` archived.

## Reviewer-4 (Altitude) FINDING 2 — flagged as OWN TASK, not inlined
"newest-on-top idempotent week upsert" reimplemented in ≥5 places:
- `_utils.insert_or_replace_weekly()` — DEAD (zero callers, also order-breaking) → delete
- `hourly_cover_sql_parser.write_log_atomic()` — atomic write (reuse)
- `col_weekly_parser.sort_week_blocks_on_top()` — CORRECT pattern (sort desc + HARD-ASSERT)
- `_reorder_hourly_blocks.py` — standalone repair script (proof bug class recurred)
- `item_sales_sql_parser.upsert_week()` — fragile variant (now sort-desc, still dup logic)
**Recommended deep fix:** extract `_tracker_writer.py` (parse→upsert→sort-desc→atomic write),
adopt into item-sales first, migrate other parsers, delete dead helper. → Handoff written
to `vault/_inbox/HANDOFF_2026-07-27_tracker_writer_extract.md`.

## RISKY findings FLAGGED (own tasks, not applied)
- Promote `NET_FACTOR=0.882` / `STORE_MAP` / `_run_sql()` to shared `_sql_common.py` (5 parsers).
- `--backfill 2026-W18..W29` 1-process mode (24→13 SQL queries over VPN).
- SQL `GROUP BY` server-side (MED risk; verify identical on 1 week before swapping).

## Verify evidence (no node on this machine)
- Unit inject: 8/8 PASS (incl. upsert sort-desc).
- Abtest: baseline vs simplified payload IDENTICAL.
- Cross-week A6: 12/12 @ 100% (65,750 items / 8,452.4M, Δ=0.0%) via DIRECT SQL recompute.
- `node` absent → JS runtime check skipped (flagged "JS runtime unchecked"); struct-check
  + independent recompute used instead (R3).

## Committed
`85eec97..0002443 master` (github Warren-Githut/warren-os-lusine). CRLF warnings harmless.
