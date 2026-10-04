# IKKO Hourly Query — SQL detail + weekday remap

Source: `dbo.Orders` (iikoAPI). Verified 2026-07-26 via SQL probe (Warren VPN on).

## Schema (cols used)
`RID, ShiftDate, DepartmentCode, DepartmentName, ShiftNum, CashRegisterNameNumber,
OrderNum, TableName, GuestCount, OrderType, OpenTime, CloseTime, Cashier,
AmountWithoutDiscount, DiscountAmount, ServiceCharge, TaxSum, AmountWithDiscount,
OrderDeleted, Storned`

## Filter (canonical)
```
DepartmentCode IN ('LSLTT','LU5','LU7')
AND OrderDeleted = 'NOT_DELETED'
AND Storned = 'FALSE'
```

## Hourly GROUP BY (hourly_cover_sql_parser v6.0)
```sql
SELECT DepartmentCode,
       DATEPART(WEEKDAY, OpenTime) as dow,
       DATEPART(HOUR, OpenTime) as hr,
       SUM(CASE WHEN OrderType != 'Split Order' THEN GuestCount ELSE 0 END) as covers,
       SUM(AmountWithDiscount) as gross_rev
FROM dbo.Orders
WHERE ShiftDate >= '{start}' AND ShiftDate <= '{end}'
  AND DepartmentCode IN ('LSLTT','LU5','LU7')
  AND OrderDeleted = 'NOT_DELETED' AND Storned = 'FALSE'
GROUP BY DepartmentCode, DATEPART(WEEKDAY, OpenTime), DATEPART(HOUR, OpenTime)
```

## Weekday remap (TRAP)
SQL Server `DATEPART(WEEKDAY, ...)` is **1=Sunday .. 7=Saturday** under default
`@@DATEFIRST` (US). Warren's DAY_ORDER is Mon-first:
```python
dow_to_day = {1:"sun", 2:"mon", 3:"tue", 4:"wed", 5:"thu", 6:"fri", 7:"sat"}
```
If you forget this, every day shifts by 1 → covers land on wrong weekday column.
(Confirm `@@DATEFIRST` on the server; if it's 1 (Monday-first) the map flips — but
default iikoAPI install = 7, so the map above holds. Re-verify if data looks off.)

## Net factor
`net = gross_rev * 0.882` — applied ONCE at aggregation. Never re-multiply in compute.

## Hour range
Keep `7 <= hr <= 21`. LU7 opens 10h (mall reg A1) → hr 7/8/9 legitimately 0 for LU7.
Do NOT penalize LU7 for empty morning hours.
