# 2026-06-12 vault-parser-audit session notes

Scope: `C:\Users\khoans\Documents\Warren_OS_Local\.kilo\skills` (non-cache parser set, 12 files).

## Parser inventory

| File | Source | Output |
|------|--------|--------|
| col_weekly_parser.py | GSheet COL_Weekly | 07_COL_Weekly_Log.md |
| col_cph.py | XLSX payroll | 12_Wage_Structure_by_Role_Monthly.md + inline |
| cogs_parser.py | GSheet PRICE_CHANGE | 03_COGS_Supplier_Monthly_Log.md |
| grabfood_parser.py | GSheet Grabfood | 06_GrabFood_Weekly_Log.md |
| hourly_cover_parser.py | GSheet 09_Cover-Revenue | 09_Hourly_Cover_Revenue_Log.md |
| google_review_parser.py | GSheet Google Review Log | 05_Google_Review_Weekly_Log.md |
| hr_movements_parser.py | XLSX Weekly report + Recruitment | 02_HR_Weekly_Log.md |
| item_sales_weekly_parser.py | GSheet 11_Item_Sales_Weekly_Log_Star_Horse | 11_Item_Sales_Weekly_Log_Star_Horse.md |
| lto_weekly_parser.py | GSheet LTO_Log | 04_LTO_Weekly_Log.md |
| payroll_cph.py | XLSX payroll | monthly/cph_result_YYYYMM.csv |
| cph_config.py | config | shared SEGMENTS_ORDER + CPH_BENCHMARKS |
| _utils.py | shared | _ask prompt helper |

## Key findings to address

- Duplicate GSheet fetch and gviz parsing in many parsers; candidate for shared `fetch_gviz()` helper.
- `payroll_cph.py` contains a hard-coded copy of `CPH_BENCHMARKS` and `SEGMENT_MAP` despite `cph_config.py` existing and being importable.
- Week detection implemented inconsistently across parsers (`days_to_sunday`, `days_since_sunday`, filename-only, isocalendar).
- `hr_movements_parser.py` uses `input()` directly, bypassing headless-friendly `_ask()` from `_utils.py`.
- Output formatting and week id strings vary (`W22` vs `2026-W22`), date separators vary (`->` vs `→`), frontmatter presence varies.
