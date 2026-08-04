# L'Usine Parser Inventory

Source: `C:/Users/khoans/Documents/Warren_OS_Local/.kilo/skills/`

## Parser Files

| File | Source | Output Log | Notes |
|---|---|---|---|
| `col_weekly_parser.py` | GSheet `COL_Weekly` | `vault/10_OPERATION_DATA/07_COL_Weekly_Log.md` | Uses `make_week_id()`. Weekly delta + monthly summary. |
| `col_cph.py` | XLSX payroll | `vault/10_OPERATION_DATA/12_Wage_Structure_by_Role_Monthly.md` | Orchestrator: calls payroll → updates markdown + inline analysis. |
| `cogs_parser.py` | GSheet `PRICE_CHANGE` | `vault/10_OPERATION_DATA/03_COGS_Supplier_Monthly_Log.md` | Dynamic column detection, sanity check on volume column. |
| `payroll_cph.py` | XLSX payroll | `vault/10_OPERATION_DATA/monthly/cph_result_YYYYMM.csv` | Must `from cph_config import SEGMENTS_ORDER, CPH_BENCHMARKS`. |
| `grabfood_parser.py` | GSheet `Grabfood` | `vault/10_OPERATION_DATA/06_GrabFood_Weekly_Log.md` | Commission flag, ROAS, rating, review sentiment, prev-week delta. |
| `hourly_cover_parser.py` | GSheet `09_Cover-Revenue` | `vault/10_OPERATION_DATA/09_Hourly_Cover_Revenue_Log.md` | Hourly covers, Net = Gross/1.133, newest-on-top sort. |
| `google_review_parser.py` | GSheet `Google Review Log` | `vault/10_OPERATION_DATA/05_Google_Review_Weekly_Log.md` | ccmment footer with metadata.

That footer seems odd. Let me just return the markdown block.