# LU_COL_ENGINE_V4 — All Automated GSheet Sources

Single source: **Google Sheet ID: `1ZtIocc_Ic1z-tO1JGd4ZLnRB_7ZHHkvpJ5emaWJyeEE`**
All automated parsers read from different tabs via `gid` parameter.

## Source Table

| # | Data Source | Tab Name | GID | Parser | Target Log | Frequency | Auto? |
|---|-------------|----------|-----|--------|------------|-----------|-------|
| 1 | **COL / Working Hours** | `COL_Weekly_` | 1732633441 | `col_weekly_parser.py` | `07_COL_Weekly_Log.md` | Weekly (Mon 09:45) + Daily (09:30) | ✅ YES |
| 2 | **COGS Supplier** | `PRICE_CHANGE` | 865155568 | `cogs_parser.py` | `03_COGS_Supplier_Monthly_Log.md` | Monthly (Mon 09:45) | ✅ YES |
| 3 | **Google Reviews** | `Google Review Log` | 762945748 | `google_review_parser.py` | `05_Google_Review_Weekly_Log.md` | Weekly (Mon 09:45) | ✅ YES |
| 4 | **GrabFood** | `Grabfood` | 689394201 | `grabfood_parser.py` | `06_GrabFood_Weekly_Log.md` | Weekly (Mon 09:45) | ✅ YES |
| 5 | **Item Sales (Star Horse)** | `Star Horse` | 72569880 | `item_sales_parser.py` | `11_Item_Sales_Weekly_Log_Star_Horse_Tracker.md` | Weekly (Mon 09:45) | ✅ YES |
| 6 | **LTO Tracker** | `LTO` | 2144443698 | `lto_parser.py` | `04_LTO_Weekly_Log.md` | Weekly (Mon 09:45) | ✅ YES |
| 7 | **Hourly Cover + Revenue** | `Hourly_Revenue` | TBD | `hourly_cover_parser.py` (TBD) | `09_Hourly_Cover_Revenue_Log.md` | Weekly (Mon 09:45) | 🆕 TBD |

## Manual Sources (Not in LU_COL_ENGINE_V4)

| # | Data Source | Method | Target Log | Frequency |
|---|-------------|--------|------------|-----------|
| 1 | Revenue (PowerBI screenshot) | Warren pastes → `_inbox/` | `01_Weekly_Revenue_Log.md` | Weekly (Mon) |
| 2 | HR Movements | Warren forwards Excel → `_inbox/` | `02_HR_Weekly_Log.md` | Weekly (Fri) |
| 3 | COGS Invoices (PDF/Excel) | Warren drops → `/ops-ingest` | `Cost_Impact_Report.md` | Monthly (~10th) |
| 4 | Wage Structure | Payroll export → `/ops-ingest` | `12_Wage_Structure_by_Role_Monthly.md` | Monthly |
| 5 | P&L | CFO sends → `/ops-ingest` | `wiki/P&L_Budget/` | Monthly (~10th) |

## Monday Cron Sequence (09:45 → 10:30)

```
09:45  → Monday GSheet Parsers (run_monday_gsheet_parsers.py)
         1. COL Weekly          (required)
         2. COGS Supplier       (required)
         3. Item Sales          (optional)
         4. LTO Tracker         (optional)
         5. Hourly Cover        (optional, TBD)
         6. Google Reviews      (optional)
         7. GrabFood            (optional)
10:00  → Daily TODAY Regeneration
10:30  → Auto Process-Logs GSheet (verify automated sources)
```

## GSheet URL Pattern

All tabs in same sheet: `https://docs.google.com/spreadsheets/d/1ZtIocc_Ic1z-tO1JGd4ZLnRB_7ZHHkvpJ5emaWJyeEE/edit?gid=<GID>#gid=<GID>`

Parser fetch URL: `https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:json&gid={SHEET_GID}`

## Adding a New Automated Source

1. Confirm tab exists in `LU_COL_ENGINE_V4` with expected columns
2. Get GID from URL (`#gid=XXXXXXXX`)
3. Create parser using `gsheet-parser-template.md`
4. Add to `run_monday_gsheet_parsers.py` PARSERS list
5. Update this table
6. Test with `LUSINE_HEADLESS=1`