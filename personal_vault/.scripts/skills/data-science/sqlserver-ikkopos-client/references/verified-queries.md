# Verified SQL Queries — IKKO POS (iikoAPI)

> Đã chạy thực tế 2026-07-24, output verified. Copy-paste + sửa tham số.

## Top N Best Seller + GP%

```sql
SELECT TOP 5
    DishName,
    SUM(Quantity) qty,
    SUM(AmountWithoutDiscount) rev,
    SUM(Cost) cost,
    ROUND((SUM(AmountWithoutDiscount)-SUM(Cost))/SUM(AmountWithoutDiscount)*100, 1) gp
FROM dbo.Dishes
WHERE DepartmentCode='LU5'
  AND ShiftDate>='2026-01-01'
  AND Category='Food'
  AND DishName!=''
  AND AmountWithoutDiscount>0
GROUP BY DishName
ORDER BY qty DESC
```

## Doanh số theo store + ngày

```sql
SELECT DepartmentCode, ShiftDate,
  SUM(AmountWithDiscount) rev,
  SUM(GuestCount) covers
FROM dbo.Orders
WHERE ShiftDate>='2026-07-01'
  AND DepartmentCode IN ('LSLTT','LU5','LU7')
GROUP BY DepartmentCode, ShiftDate
ORDER BY ShiftDate
```

## Category Mix (theo store + category)

```sql
SELECT DepartmentCode, Category,
  SUM(Quantity) qty,
  SUM(AmountWithoutDiscount) rev
FROM dbo.Dishes
WHERE ShiftDate>='2026-01-01'
  AND DepartmentCode IN ('LSLTT','LU5','LU7')
GROUP BY DepartmentCode, Category
ORDER BY DepartmentCode, qty DESC
```

## Distinct Department Codes + Order Count

```sql
SELECT DepartmentCode, COUNT(*) cnt
FROM dbo.Orders
GROUP BY DepartmentCode
ORDER BY cnt DESC
```

## Date Range Check

```sql
SELECT MIN(ShiftDate), MAX(ShiftDate), COUNT(DISTINCT ShiftDate) days
FROM dbo.Orders
```

## Covers theo giờ (Peak Hours)

```sql
SELECT DATEPART(HOUR, OpenTime) h, SUM(GuestCount) covers
FROM dbo.Orders
WHERE DepartmentCode='LSLTT'
  AND ShiftDate>='2026-07-01'
GROUP BY DATEPART(HOUR, OpenTime)
ORDER BY h
```

---

## Session 2026-07-24 — Top 5 Best Seller LU5 Food 2026

| # | Món | SL | Doanh thu | Cost | GP% |
|---|-----|----|-----------|------|-----|
| 1 | Beef Kimchi Fried Rice | 1,057 | 257.9M | 59.1M | 77.1% |
| 2 | Cơm Tấm Broken Rice 3.0 | 992 | 203.6M | 53.6M | 73.7% |
| 3 | The Big Breakfast | 879 | 202.1M | 74.3M | 63.2% |
| 4 | Crispy Skin Salmon | 823 | 262.1M | 95.8M | 63.4% |
| 5 | L'Usine Wholesome Breakfast | 743 | 184.6M | 49.5M | 73.2% |

**Tổng Top 5:** 4,494 món · 1.11B doanh thu · 332.3M cost · GP% bình quân 70.1%

---

## Pitfalls từ session này

| Pitfall | Fix |
|---------|-----|
| Category='' (rỗng) — modifier rác (DINE IN, Customer, VM...) với qty cao nhưng rev=0 | Luôn lọc `Category='Food'` hoặc `Category!='' AND AmountWithoutDiscount>0` |
| `AmountWithoutDiscount` vs `AmountWithDiscount` — khác biệt có thể có ở ServiceCharge+TaxSum | Orders dùng `AmountWithDiscount` cho revenue net; Dishes dùng `AmountWithoutDiscount` cho GP% |
| Driver cũ `SQL Server` không hỗ trợ `Encrypt=` → lỗi "Invalid connection string attribute" | `sqlclient.py` tự detect driver, bỏ qua Encrypt nếu driver legacy |
| VPN DrayTek có thể ngắt sau thời gian dài → query timeout | Check VPN trước mỗi query batch (B1 trong skill) |
| `Database=` mặc định về `master` nếu không set `MSSQL_DATABASE` → query sai DB | Luôn `export MSSQL_DATABASE=iikoAPI` trước khi query |
