# Weekly Ops Report Workflow

> Pattern for `/ops-weekly-report`: synthesis từ 7 log files + cross-domain connections + CONTEXT §5 update.

## Data Sources (ordered by read priority)

| # | Domain | Log File | W27 Example |
|---|--------|----------|-------------|
| 1 | Revenue | `01_Weekly_Revenue_Log.md` | Full week table + MTD + YTD |
| 2 | Labour (COL) | `07_COL_Weekly_Log.md` | Scorecard + daily COL% + key flags |
| 3 | CX / Reviews | `05_Google_Review_Weekly_Log.md` | Rating snapshot + R/1k + sentiment |
| 4 | Delivery (GrabFood) | `06_GrabFood_Weekly_Log.md` | Revenue summary + daily breakdown + ad spend |
| 5 | Hourly Covers | `09_Hourly_Cover_Revenue_Log.md` | Actual covers, gross covers, split orders, RC |
| 6 | Item Sales | `11_Item_Sales_Weekly_Log_Star_Horse_Tracker.md` | Qty, revenue, avg price, deltas |
| 7 | HR / Staffing | `02_HR_Weekly_Log.md` | Vacancies, movements, OIL |
| 8 | LTO (optional) | `04_LTO_Weekly_Log.md` | Campaign performance — skip if no new data |

## Synthesis Structure

Output: `10_OPERATION_DATA/weekly_ops_synthesis.md`

### Section order (mandatory)
1. **Decisions for This Week** — table: # | Area | Decision Needed | Priority | Status
2. **Synthesis** — one subsection per domain, each with source citation, full week table, key takeaways
3. **Watchlist** — sorted 🔴/🟡/✅ items with notes
4. **Cross-Domain Connections** — table: # | Connection | Domains | Evidence | Signal
5. **Monday Handoff → CONTEXT §5** — bullet theme list for CONTEXT.md

### Cross-Domain Connection method
- Find patterns where 2+ domains interact (e.g. "revenue down + hours up = COL spike")
- Cite specific file, line range, metric values
- Signal tags: 🔴 Amplification, 🔴 Signal shift, 🟡 Correlation, 🟡 Hidden driver, 🟡 Opacity risk, ✅ Stable

### CONTEXT §5 Update (Phase 7)
- Keep "Workflow status" row with key metrics
- Update "Open items" — remove resolved, add new
- Update question rows with latest data
- Remove stale questions resolved by synthesis data
- Add new questions that emerged from cross-domain connections

### Data consistency cross-check
1. Cross-check covers: Hourly Log vs Revenue Log (<2% diff expected)
2. Cross-check revenue: Hourly Log vs Revenue Log (<1% diff expected)
3. Flag discrepancies >5% in report

### Template
Use the W26 entry in `weekly_ops_synthesis.md` as structure template — copy headers and replace W26→W{new} data.
