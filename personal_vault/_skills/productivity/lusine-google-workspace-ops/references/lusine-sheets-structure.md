# L'Usine Google Sheets — Structure & Gotchas

> Learned during `/ops-col` implementation, 2026-06-20, and hourly revenue v5.0 redesign 2026-07-06.
> Source sheet: `1ZtIocc_Ic1z-tO1JGd4ZLnRB_7ZHHkvpJ5emaWJyeEE`

## Sheet Tabs (verified)

| Tab | GID | Purpose |
|-----|-----|---------|
| `INPUT MỖI THANG` | 189554315 | Monthly input |
| `02_MASTER_CPH` | 871133523 | CPH rates per month/store/role (9 columns: A-I) |
| `07_COL_Weekly_Log` | 1732633441 | COL daily data — 43 columns (A-AQ), ~334 rows |
| `01_Weekly_Revenue_Log` | 1610041413 | Weekly revenue |
| `DASHBOARD` | 1136410646 | Dashboard |

## Gotcha 1: CPH Range Must Be A1:I (9 columns)

**Problem:** Reading `02_MASTER_CPH!A1:H20` returns 8 columns, missing the `Cleaner` column in I. All CPH values for Cleaner become `None`.

**Fix:** Always use `A1:I` or wider range. The sheet has 9 data columns:
```
A: YEARMONTH  B: Store  C-I: 7 role CPH rates
```

```python
# ✅ CORRECT
range = "'02_MASTER_CPH'!A1:I20"

# ❌ WRONG — Cleaner column (I) is cut off
range = "'02_MASTER_CPH'!A1:H20"
```

## Gotcha 2: Scope Substring Check

**Problem:** `'spreadsheets' in scopes_list` fails because scopes are full URLs like `'https://www.googleapis.com/auth/spreadsheets'`. The string `'spreadsheets'` is NOT an exact match for the URL.

**Fix:** Use substring match:
```python
# ✅ CORRECT
has_sheets = any('spreadsheets' in s for s in token_data.get('scopes', []))

# ❌ WRONG — exact string comparison
if 'spreadsheets' not in token_data.get('scopes', []):
```

## Gotcha 3: CPH Numbers Contain Commas

**Problem:** CPH values like `'81,173'` fail on `float()`.

**Fix:** Strip commas before parsing:
```python
raw = row[j+2].replace(',', '').strip()
rate = float(raw) if raw else None
```

## Gotcha 4: COL_Weekly Date Format = YYYYMMDD (Not DD/MM/YYYY)

**Problem:** Querying `07_COL_Weekly_Log` by `/06/` or `/05/` to find June/May rows returns zero results because dates are stored as compact integers (`20260601`), not display-formatted strings.

The date column (A, index 0) uses `YYYYMMDD` format:
```
20260301 → March 1, 2026
20260501 → May 1, 2026
20260601 → June 1, 2026
20260630 → June 30, 2026
```

**Fix:** Use `str(date_val).startswith('202605')` for May, `startswith('202606')` for June:

```python
# ✅ CORRECT
may_rows = [r for r in rows if r and str(r[0]).startswith('202605')]
june_rows = [r for r in rows if r and str(r[0]).startswith('202606')]

# ❌ WRONG — date is NOT 'DD/MM/YYYY' or 'DD/MM' format
may_rows = [r for r in rows if '/05/' in str(r[0])]
```

**Row frequency:** 3 rows per day (LU3, LU5, LU7) → ~90 rows/month for a full 30-day month. The sheet as of July 2026 has ~382 rows covering Mar–Jul.

## Gotcha 5: COL_Weekly Total_Hours_Whole_Store Is Key Column

When aggregating total working hours by store, use **column index 13** (`Total_Hours_Whole_Store`). Do NOT sum FOH+BAR + BOH + Cleaner from the breakdown columns — the whole-store total is authoritative; breakdown columns may have minor rounding discrepancies (1-3h differences observed).

| Index | Column Header | Use |
|:-----:|--------------|-----|
| 13 | `Total_Hours_Whole_Store` | **Primary** — store daily total |
| 16 | `Total_Hours_FOH+BAR` | Department breakdown |
| 17 | `Total_Hours_BOH` | Department breakdown |
| 18 | `Total_Hours_Cleaner` | Department breakdown |

## Gotcha 6: COL Sheet Has 43 Fixed Columns

The `07_COL_Weekly_Log` sheet has exactly 43 columns (A-AQ), fixed order per SOP V2:

```
Date, Day_of_the_Week, Store, Revenue, Food_Revenue, Beverage_Revenue,
Hrs_FOH_Management, Hrs_FOH_Floor_Lead, Hrs_FOH_Service_Agent, Hrs_FOH_Bar_Team,
Hrs_BOH_Leader, Hrs_BOH_Cook, Hrs_Cleaner,
Total_Hours_Whole_Store, Total_Hours_FOH, Total_Hours_BAR, Total_Hours_FOH+BAR,
Total_Hours_BOH, Total_Hours_Cleaner,
Total_Wage_Whole_Store, Total_Wage_FOH, Total_Wage_Bar, Total_Wage_FOH+BAR,
Total_Wage_BOH, Total_Wage_Cleaner,
COL_Percentage_Whole_Store, COL_FOH_Percentage, COL_BAR_Percentage,
COL_FOH+BAR_Percentage, COL_BOH_Percentage, COL_Cleaner_Percentage,
SPLH_Whole_Store, SPLH_FOH, SPLH_BAR, SPLH_FOH+BAR, SPLH_BOH,
Productivity_Index, Status,
LW_Revenue, LW_Hours, LW_COL, LW_SPLH, Trend
```

Hours input columns are at indices 6-12 (0-indexed), not 7-13.

## Verified Append Pattern

```python
# Source: https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/append
body = {'values': rows}  # rows = list of 43-element lists
result = service.spreadsheets().values().append(
    spreadsheetId=SHEET_ID,
    range="'07_COL_Weekly_Log'!A1",
    valueInputOption='USER_ENTERED',   # parse numbers as numbers, not strings
    insertDataOption='INSERT_ROWS',    # insert new rows at end
    body=body,
).execute()
```

## Gotcha 7: Hourly_Revenue Tab Has Merged-Cell Columns (Inconsistent Pattern)

**Problem:** The `09_Hourly_Cover_Revenue_Log` tab (gid: 1841157748) uses merged cells in the header row, creating an inconsistent column pattern. Each day's block of (guests, empty, revenue) has different width depending on whether the day header is merged:

| Day | Col Pattern | Guests Index | Revenue Index |
|-----|-------------|:------------:|:-------------:|
| Mon | guests, empty, revenue | 3 | 5 |
| Tue | guests, revenue (no empty) | 6 | 7 |
| Wed | guests, empty, revenue | 8 | 10 |
| Thu | guests, revenue (no empty) | 11 | 12 |
| Fri | guests, revenue (no empty) | 13 | 14 |
| Sat | guests, revenue (no empty) | 15 | 16 |
| Sun | guests, empty, revenue | 17 | 18 |
| Weekly total | guests, empty, revenue | 19 | 20 |

**Fix:** Hardcode day-by-day column indices instead of computing them with a formula:

```python
# ✅ CORRECT — explicit per-day mapping
DAY_COLS = {
    'mon': (3, 5),   # (guests_col, rev_col)
    'tue': (6, 7),
    'wed': (8, 10),
    'thu': (11, 12),
    'fri': (13, 14),
    'sat': (15, 16),
    'sun': (17, 18),
}

# ❌ WRONG — assumed uniform 3-column pattern
guests_col = 3 + di * 3   # gives wrong indices for Tue-Sat
rev_col = 5 + di * 3      # gives wrong indices
```

**Data rows structure:** The tab groups data by store (LU3-LTT-Q1, LU5-CM-Q7, LU7-SC-Q1). Each store section has:
- Individual order-type rows per hour (Dine in, GrabFood, Split Order, Take away, Delivery Now)
- `XX Total` rows per hour (e.g., `08 Total`, `09 Total`) — these are the authoritative hourly totals
- A store total row at the end of the section

**Parsing approach:** Read only `XX Total` rows for hourly data, plus the store total row. Use the 3-element Store Total row (last in store section) for `cn(total_row[19])` = weekly guests, `cn(total_row[20])` = weekly gross revenue.

```python
# Helper to clean GSheet cell values
def cn(v):
    if v is None or str(v).strip() in ('', '0'): return 0
    s = str(v).replace(',','').replace(' ','').strip()
    try: return int(float(s))
    except: return 0
```

## OAuth Token Path (warren-profile)

```
Token: C:\Users\khoans\AppData\Local\hermes\google_token.json
Scopes: [..., 'https://www.googleapis.com/auth/spreadsheets', ...]
```

The token is at the global hermes level (not per-profile). Works for both `warren-profile` and `personal_profile` sessions.