# L'Usine iikoAPI Schema — IKKO POS Database

> Discovered 2026-07-24. SQL Server at store LAN (VPN required). Login: `pi` (read-only, iikoAPI only).
> Updated 2026-07-24: store mapping confirmed by Bố, Cost column discovered, GP% patterns added.

## Connection
- Server: `10.28.15.63,9433` (L'Usine LAN, reachable only via DrayTek VPN → 10.28.15.x subnet)
- Database: `iikoAPI` (only accessible DB; `Chain` & `Procurement` blocked for login `pi`)
- Driver: `SQL Server` (legacy Windows driver; Encrypt/TrustServerCertificate NOT supported)
- Tool: `vault/.scripts/sqlserver_client/sqlclient.py`
- Creds: `vault/.scripts/sqlserver_client/.env` (gitignored)

## Tables (5 — all under `dbo`)

### dbo.Orders — Header (hoá đơn)
Key columns: `RID`, `ShiftDate`, `DepartmentCode`, `DepartmentName`, `ShiftNum`, `CashRegisterNameNumber`, `OrderNum`, `TableName`, `GuestCount`, `OrderType`, `OpenTime`, `CloseTime`, `Cashier`, `AmountWithoutDiscount`, `DiscountAmount`, `ServiceCharge`, `TaxSum`, `AmountWithDiscount`, `OrderDeleted`, `Storned`

**Revenue analysis**: `AmountWithDiscount` = post-discount, pre-service-charge/VAT. `GuestCount` = covers. `ShiftDate` = date. Filter `OrderDeleted=0 AND Storned=0` for valid orders.

### dbo.Dishes — Line items (món gọi)
Key columns: `RID`, `ShiftDate`, `DepartmentCode`, `ShiftNum`, `CashRegisterNameNumber`, `OrderNum`, `TableName`, `DishCode`, `DishName`, `Unit`, `Category`, `DishCategoryAccounting`, `DishGroup`, `DishGroup1-3`, `TaxRate`, `Quantity`, `AmountWithoutDiscount`, `DiscountAmount`, `ServiceCharge`, `TaxSum`, `AmountWithDiscount`, **`Cost`**, `DeletedWithWriteoff`

**🚨 CRITICAL: `Cost` column IS populated** — enables direct GP% calculation from DB without cross-referencing any other source. GP = `AmountWithoutDiscount - Cost`, GP% = `(AmountWithoutDiscount - Cost) / AmountWithoutDiscount * 100`.

**Product mix**: group by `DishCode`/`DishName`/`Category`. Link to Orders via `OrderNum + ShiftDate + DepartmentCode`.

### dbo.Payments — Payments (thanh toán)
Key columns: `RID`, `ShiftDate`, `DepartmentCode`, `ShiftNum`, `CashRegisterNameNumber`, `OrderNum`, `TableName`, `PaymentType` (CASH/CARD), `Currency`, `NonCashPaymentType`, `Amount`

### dbo.Discounts — Discounts (giảm giá)
Key columns: `RID`, `ShiftDate`, `DepartmentCode`, `ShiftNum`, `CashRegisterNameNumber`, `OrderNum`, `TableName`, `DishCode`, `DiscountType`, `DiscountName`, `Amount`

### dbo.Taxes — Taxes (thuế)
Key columns: `RID`, `ShiftDate`, `DepartmentCode`, `ShiftNum`, `CashRegisterNameNumber`, `OrderNum`, `TableName`, `DishCode`, `TaxGroup`, `TaxRate`, `Amount`

## Store Mapping (CONFIRMED by Bố 2026-07-24)

| DepartmentCode | Store | Status |
|---------------|-------|--------|
| `LSLTT` | **LU3** (Lê Thánh Tôn) | ✅ Active |
| `LU5` | **LU5** (Phú Mỹ Hưng) | ✅ Active |
| `LU7` | **LU7** (Saigon Centre) | ✅ Active |
| `LSDK` | Old store | ❌ Closed — ignore |
| `LUTD` | Old store | ❌ Closed — ignore |
| `LSLL` | Old store | ❌ Closed — ignore |
| `NM1`, `NM2` | Old stores | ❌ Closed — ignore |
| `LU6`, `LU8` | Old stores | ❌ Closed — ignore |
| `SS2` | Old store | ❌ Closed — ignore |
| `LU5-TD-Q2`, `GG-TD-Q2` | Test/minor | ❌ Ignore |

## Data Range
- 2016-07-01 → 2026-07-24 (3,551 days, ~10 years)
- ~1,195,974 orders total
- Top by volume: LSLTT (354K), LU5 (184K), LSDK (173K), LUTD (138K), LSLL (106K), LU7 (98K)

## Known Limitations
- ❌ **Inventory (tồn kho)**: NOT in iikoAPI. Requires access to `Procurement` database (login `pi` blocked). Ask IT for read-only access.
- ❌ **Chain database**: Blocked. Contains chain config data.
- ⚠️ **Revenue formula**: `AmountWithDiscount` is post-discount, pre-service-charge/VAT. Net revenue may need adjustment (verify with Bố's 0.882 multiplier vs actual totals).
- ⚠️ **VPN required**: DrayTek Smart VPN Client, profile "TLG VPN", server `14.161.21.69:18443`. Without VPN, `10.28.15.63` is unreachable from Bố's home/office network.

## Quick Analysis Patterns

### Doanh số hàng ngày (30 ngày gần nhất)
```sql
SELECT DepartmentCode, ShiftDate, 
       SUM(AmountWithDiscount) AS Rev, 
       SUM(GuestCount) AS Covers
FROM Orders 
WHERE ShiftDate >= DATEADD(day,-30,GETDATE())
  AND OrderDeleted=0 AND Storned=0
GROUP BY DepartmentCode, ShiftDate
ORDER BY ShiftDate DESC, DepartmentCode;
```

### Best Seller + GP% (theo store, kỳ bất kỳ)
```sql
SELECT TOP 5
    DishName,
    SUM(Quantity) qty,
    SUM(AmountWithoutDiscount) rev,
    SUM(Cost) cost,
    ROUND((SUM(AmountWithoutDiscount) - SUM(Cost)) / SUM(AmountWithoutDiscount) * 100, 1) AS gp_pct
FROM Dishes
WHERE DepartmentCode = 'LU5'       -- thay store
  AND ShiftDate >= '2026-01-01'    -- thay kỳ
  AND Category = 'Food'            -- thay category: Food/Beverage/...
  AND AmountWithoutDiscount > 0
  AND Cost > 0                     -- loại món chưa có cost
GROUP BY DishName
ORDER BY qty DESC;
```

### Revenue + GP% trend theo tháng
```sql
SELECT 
    FORMAT(ShiftDate, 'yyyy-MM') AS Month,
    SUM(AmountWithoutDiscount) rev,
    SUM(Cost) cost,
    ROUND((SUM(AmountWithoutDiscount) - SUM(Cost)) / SUM(AmountWithoutDiscount) * 100, 1) AS gp_pct
FROM Dishes
WHERE DepartmentCode = 'LU5'
  AND ShiftDate >= '2026-01-01'
  AND Category = 'Food'
  AND AmountWithoutDiscount > 0
GROUP BY FORMAT(ShiftDate, 'yyyy-MM')
ORDER BY Month;
```

### Category breakdown + GP%
```sql
SELECT Category,
    SUM(Quantity) qty,
    SUM(AmountWithoutDiscount) rev,
    SUM(Cost) cost,
    ROUND((SUM(AmountWithoutDiscount) - SUM(Cost)) / SUM(AmountWithoutDiscount) * 100, 1) AS gp_pct
FROM Dishes
WHERE DepartmentCode = 'LU5'
  AND ShiftDate >= '2026-01-01'
  AND AmountWithoutDiscount > 0
GROUP BY Category
ORDER BY rev DESC;
```

> Run: `cd vault/.scripts/sqlserver_client && export MSSQL_DATABASE=iikoAPI && python3 sqlclient.py query "<sql>"`
