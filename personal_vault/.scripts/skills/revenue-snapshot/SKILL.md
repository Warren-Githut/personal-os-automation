---
name: revenue-snapshot
description: Build or refresh the L'Usine daily revenue snapshot report (System-Wide + By Location + Top 10 Items) for stores LU3/LU5/LU7, pulling live data from the iikoAPI SQL Server database and the Daily_Budget_Target_by_Store.xlsx budget file, then publish it as a JP-Morgan-style HTML artifact. Use this skill whenever the user says "revenue snapshot", asks for a daily/MTD/YTD revenue report, covers report, L'Usine store performance, or wants to check/update/refresh the numbers on the existing snapshot report — even if they just say "chạy lại báo cáo" or "update the numbers" without naming the skill explicitly.
---

# L'Usine Revenue Snapshot (Bố — on demand only)

**Bố workflow:** Chỉ chạy khi cần check nhanh. Cần VPN + quyền SQL. Con query, generate HTML. Bố đối chiếu MTD vs Budget/Target.

This skill rebuilds the exact report already agreed with the user across a long design session. Don't redesign it — reuse `assets/report_template.html` as the starting point and only swap in fresh numbers, following the formulas below exactly. The full narrative of every decision (including things that were tried and rejected) lives in `C:\Users\Pham Thi Kim Loan\Desktop\Claude\Daily Revenue Snaphot\Revenue_Snapshot_Build_Log.md` — read it if anything here is ambiguous or if the user asks "why did we do X."

## Before anything: connect and confirm scope

1. Connect to SQL Server via `pymssql` (install with `pip install pymssql openpyxl` if missing — this machine has no `sqlcmd`/ODBC driver):
   - Server: `10.28.15.63`, Port: `9433`
   - Login: `pi` / Password: `pi@12345`
   - Database: `iikoAPI` (this login only has access to `iikoAPI`, `master`, `msdb`, `tempdb` — not `Procurement`/`Chain`/`model`)
   - **Requires the company VPN to be connected first** — if the connection times out, ask the user to check their VPN before anything else.
   - Treat this password like any other credential: don't print it in responses beyond what's needed to run the query, and delete any scratch script that embeds it once you're done (same discipline used throughout the original build).
2. Confirm the **snapshot date**: use the most recent date where all 3 stores (`LSLTT`=LU3, `LU5`, `LU7`) have a *complete* day of orders — check recent daily order counts per store; a day still in progress will show an abnormally low count for the current date, so fall back to the prior day.
3. Read the budget file at `C:\Users\Pham Thi Kim Loan\Desktop\Claude\Daily Revenue Snaphot\Daily_Budget_Target_by_Store.xlsx` (sheet `Daily Summary (All Stores)`) with `openpyxl`. It currently only has rows for `2026-07-01` through `2026-12-31` — if the snapshot date falls outside that range, tell the user the Budget/Target tiles can't be computed and ask whether to omit them or whether they've added new rows to the file.

## Exact formulas (verified against the user's reference dashboard — do not deviate)

| Metric | SQL | Why |
|---|---|---|
| Net Revenue | `SUM(AmountWithDiscount - TaxSum)` | `AmountWithDiscount` has VAT (8%) baked in — confirmed `TaxSum = AmountWithDiscount * 8/108` on real rows. Subtracting `TaxSum` gives the true net-of-VAT figure. |
| Covers | `SUM(GuestCount) WHERE OrderType <> 'Split Order'` | `Split Order` rows are bill-split artifacts (GuestCount=1 padding, not real guests). This matches the reference dashboard exactly for a single day (267=267). MTD/YTD were still off by a small amount (6,199 vs 6,187; 91,352 vs 90,755) after this fix — investigated and ruled out deleted orders/items as the cause. Best guess is the reference report was a cached snapshot from an earlier refresh, not a formula error, but flag this open question to the user if they ask for exact parity again. |
| Avg Spend/Cover | `Net Revenue / Covers` | |
| Delivery Revenue | Net Revenue where `OrderType IN ('GrabFood','BAEMIN','Delivery','Delivery (Deactivated)','Delivery Now','FoodBooking','PassGo')` | |
| Orders filter | Always `Storned <> 'TRUE'`. `OrderDeleted` is always `'NOT_DELETED'` for these 3 stores across all history, so no extra filter is needed there. | |
| Dishes filter (top items, Food/Bev) | `DeletedWithWriteoff = 'NOT_DELETED' AND Category <> ''` | Blank category rows are non-item modifier/system rows (e.g. "DINE IN", "Customer", "VF"), not real dishes. |
| MTD Budget/Target Achieved | `MTD actual revenue ÷ FULL-MONTH budget/target sum` (the whole month, e.g. Aug 1–31 — not just the days elapsed so far) | Getting this wrong (dividing by only the elapsed-days budget) inflates the % a lot — this was corrected once already; don't reintroduce the bug. |
| Food/Beverage mix | Share of **MTD** dish revenue by `Category`, as % of the **whole** total (Food / Beverage / Other), not normalized to just Food+Beverage. `Other` = Gift Cards - G&G, Set Lunch Menu, MorningKickStart, LU Happy Hour 50%, Extra, Lusine Wine. | |
| Revenue by day-part | **MTD** revenue bucketed by hour of `Orders.OpenTime`: `06-10`, `11-14`, `15-17`, `18-22` | |
| Calendar % | `day-of-month / days-in-month` | |

Y/Y comparisons use the same date range one year earlier; M/M comparisons use the same date range in the prior calendar month (e.g. MTD Aug 1–17 vs Jul 1–17).

## Report structure (don't reorder without the user asking)

1. Header: "L'USINE" wordmark + "Daily Revenue Snapshot" + date badge + LU3/LU5/LU7 store chips
2. **01 · System-Wide**: Achievement band (Calendar / MTD Budget Achieved / MTD Target Achieved) → KPI band (Net Revenue / Covers / Avg Spend per Cover, each with Today, MTD w/ Y-Y+M-M, YTD w/ Y-Y) → Revenue Trend area chart (30 days, with a dashed 30-day-average line — this chart only)
3. **02 · By Location**: one full-width horizontal row per store (not a 3-column grid — this was explicitly changed from vertical cards to horizontal rows for readability), each row split into: Identity + MTD Budget/Target meters | KPI table (Revenue/Covers/Avg-per-Cover/Delivery × Today/MTD/YTD) | Food/Beverage mix bar (MTD only) | Revenue by day-part bars (MTD only). Below the three rows: a Revenue Trend by Location chart (3 lines, one per store — no dashed average line here, that's system-wide only).
4. **03 · Top 10 Items**: two tables, "By Revenue" and "By Volume", both system-wide but broken out into `Item | LU3 | LU5 | LU7 | Total` columns. Use `<colgroup>` with fixed `%` widths (not auto) so the two tables' columns line up — this was a real bug once.
5. Footer: one-line data-source note listing the formulas actually used (mirror what's in the template).

## Visual design (already finalized — reuse, don't reinvent)

- Institutional "JP Morgan" look: white background, navy `#0A2A66` as the primary accent, Calibri font throughout (both headings and body — this replaced an earlier serif/dark-mode design after user feedback).
- Store colors: LU3 = navy `#0A2A66`, LU5 = steel teal `#2E7D9A`, LU7 = bronze `#B7791F`.
- Food/Beverage bar colors: Food = `#0B132B`, Beverage = `#39FF88` (neon green — a specific, deliberate user choice, keep it as-is).
- Positive/negative deltas: green `#157F3C` / red `#B42318`.
- Every multi-row table needs `<colgroup>` with fixed-percentage column widths and `table-layout: fixed`, or columns will silently drift out of alignment between tables that sit side by side or stacked.
- Include `<meta charset="utf-8">` at the top (needed for the ₫ symbol to render correctly in some hosting contexts).

## How to execute

1. Query the fresh numbers using the formulas above (Today, MTD, MTD-last-year, MTD-last-month, YTD, YTD-last-year, 30-day trend, top 10 items by revenue/volume with per-store breakdown, Food/Bev category mix, day-part buckets, budget/target). Use temp Python scripts in the scratchpad directory and delete them when done (they contain the DB password).
2. Copy `assets/report_template.html` to your scratchpad as the working file, then edit in place — swap the numbers, dates, deltas, chart data arrays, and table rows to match the new snapshot date. Keep every CSS class, color, and structural element unchanged unless the user explicitly asks for a design change.
3. Publish via the Artifact tool. If there's a previously-published version of this exact report in the conversation or the user gives you its URL, pass that URL to update it in place rather than creating a new artifact — ask the user for the link if you don't have it and they haven't mentioned starting fresh.
4. Sanity-check before declaring done: does today's per-store total match the system-wide total? Do the three location rows' `<colgroup>` widths match each other? Did you delete the scratch script holding the DB password?

## If the user asks to change the design or add a metric

Don't just bolt it on. Follow the pattern used throughout the original build: build a small standalone HTML preview (matching the existing design tokens) showing just the change, publish it as a separate quick artifact, and get the user's sign-off before touching the main report file. This project has a long history of iterating this way — it works well and avoids wasted rebuilds.
