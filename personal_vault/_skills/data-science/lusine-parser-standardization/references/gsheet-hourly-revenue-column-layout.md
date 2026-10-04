# GSheet Hourly_Revenue Tab -- Column Layout & Parsing

## Tab Location
- **Tab name:** `09_Hourly_Cover_Revenue_Log` (NOT `Hourly_Revenue` as in frontmatter)
- **Sheet ID:** `1ZtIocc_Ic1z-tO1JGd4ZLnRB_7ZHHkvpJ5emaWJyeEE`
- **GID:** `1841157748`

## Column Layout (Irregular -- due to merged cells)

Column indices are NON-uniform because the header has merged cells. DO NOT use `3 + di*3`.

### Correct day column mapping:

| Day | Guests col | Rev col |
|-----|:----------:|:-------:|
| Mon | 3 | 5 |
| Tue | 6 | 7 |
| Wed | 8 | 10 |
| Thu | 11 | 12 |
| Fri | 13 | 14 |
| Sat | 15 | 16 |
| Sun | 17 | 18 |
| Wk total | 19 | 20 |

```python
DAY_COLS = {'mon':(3,5),'tue':(6,7),'wed':(8,10),'thu':(11,12),'fri':(13,14),'sat':(15,16),'sun':(17,18)}
```

## Row Structure

| Row 0 | Title |
| Row 2 | Period header (`Period: from 6/29/2026 to 7/5/2026`) |
| Row 5 | Column headers |
| Rows 6+ | Data |

### Data row variants:

1. **Order-type row** -- `Outlet | hour | order_type | day_data...`. Multiple per hour (Dine in, GrabFood, Split Order, etc.)
2. **Hour Total row** -- `empty | "08 Total" | empty | day_data...`. Matches `r'^(\d+)\s*Total$'`. **This is the preferred row for hourly breakdown.**
3. **Store Total row** -- `"LU3-LTT-Q1 Total" | empty | empty | week_data...`. col[19]=guests, col[20]=gross_rev.
4. **Grand Total** -- `"Grand Total" | ...`. System-wide total.

### LU3 Hour 7: No Total row
LU3 H7 data only exists as order-type rows (Dine in, R6). Sum manually. LU5/LU7 have no H7.

## Active Covers Formula

`actual_covers = gross_covers - split_orders` (defined in frontmatter)

1. Sum ALL `Order Type = 'Split Order'` covers across the week
2. Subtract from store total covers

## Cross-Check Protocol

After computing actual covers from GSheet, cross-check against `01_Weekly_Revenue_Log.md`:

```python
diff_pct = (actual - revlog_covers) / revlog_covers * 100
if abs(diff_pct) > 5: FLAG = "RED"
```

**W27 result:** GSheet actual=2,226 vs RevLog=2,216 = 0.5% OK

## Cell Format (Hourly Detail Tables)

Format: `covers.revM` where `.` is middle dot `\xb7` (U+00B7)

```
10.3M     = 10 covers, 3M revenue
2.0.6M    = 2 covers, 0.6M revenue
886.225M  = 886 covers, 225M revenue (D1)
```

Revenue: M (trieu VND), 1 decimal. Whole number: `3` not `3.0`.

```python
def cell(c, rv):
    r_m = round(rv / 1e6, 1)
    r_str = str(r_m)
    if r_m == int(r_m): r_str = str(int(r_m))
    return f"{c}\xb7{r_str}M"
```

## Day Headers: 1-letter

M T W T F S S (Tue/Thu both "T" -- context disambiguates)
