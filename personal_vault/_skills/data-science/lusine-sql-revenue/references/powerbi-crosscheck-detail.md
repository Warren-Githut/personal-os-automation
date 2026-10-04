# PowerBI Cross-Check — 2026-07-24

## Raw data

### Daily (23/07/2026)

**SQL (gross):**
| Store | Revenue | Covers | Tickets |
|-------|---------|--------|---------|
| LU3 (LSLTT) | 31,984,707 | 122 | 86 |
| LU5 | 29,148,364 | 98 | 81 |
| LU7 | 29,905,409 | 114 | 73 |
| ALL | 91,038,480 | 334 | 240 |

**PowerBI (NET):**
- NET REVENUE: 80,402,050
- COVERS: 299
- AVG SPEND/COVER: 268,903
- TICKETS: 238
- DAILY TARGET ACHIEVED: 0%

**Cross-check:**
```
SQL ALL Gross × 0.882 = 91,038,480 × 0.882 = 80,295,939
PowerBI NET = 80,402,050
Δ = 0.13% ✅
```

### MTD (01-23/07/2026)

| | SQL | ×0.882 | PowerBI | Δ |
|---|-----|--------|---------|----|
| Revenue | 2,413,291,206 | 2,128,522,844 | 2,127,468,820 | +0.05% |

**PowerBI MTD screenshot:**
- MTD REVENUE: 2,127,468,820
- MTD REVENUE Y/Y: 3%
- MTD COVER Y/Y: -7%
- MTD SPEND/COVER Y/Y: 11%
- MTD REVENUE M/M: -4%

### YTD

**PowerBI YTD:**
- YTD REVENUE: 21,138,507,061
- YTD REVENUE Y/Y: 15%
- YTD COVERS Y/Y: 10%
- YTD SPEND/COVER Y/Y: 5%
- YTD SPEND/COVER: 258,619

### W/W (vs tuần trước)

**PowerBI W/W (ngày 23/7 vs tuần trước):**
- % REVENUE W/W: -88%
- REVENUE W/W: -600,271,450
- % COVERS W/W: -88%
- COVERS W/W: -2,227
- % SPEND/COVER W/W: -0%

## Column types verified

```sql
SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='Orders'
```
Key columns: RID, ShiftDate, DepartmentCode, DepartmentName, ShiftNum, CashRegisterNameNumber, OrderNum, TableName, GuestCount, OrderType, OpenTime, CloseTime, Cashier, AmountWithoutDiscount, DiscountAmount, ServiceCharge, TaxSum, AmountWithDiscount, **OrderDeleted** (NVARCHAR), **Storned** (NVARCHAR)

- OrderDeleted = 'NOT_DELETED' (not INT 0/1)
- Storned = 'FALSE' (not INT 0/1)
- All 86 LSLTT orders on 23/7 were NOT_DELETED + FALSE → covers discrepancy NOT from deletions

## PowerBI link

`https://app.powerbi.com/groups/me/reports/44d43f8a-adfc-4f23-9aaa-4944f0470481/ReportSectionddf2fb01629cc75900b1?ctid=853cce59-a9e5-413a-a5a4-6ad8eb153319&experience=power-bi`
