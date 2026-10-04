---
name: lusine-sql-revenue
description: "Query doanh thu L'Usine từ IKKO SQL Server — revenue NET (×0.882), covers, tickets, MTD, YTD, target từ Budget_vs_Actual.md. Dùng khi Bố hỏi doanh số / build pipeline SQL thay screenshot. Cross-checked với PowerBI 2026-07-24."
version: 1.1.0
trigger: "Bố hỏi 'doanh số SQL', 'query revenue', 'pipeline SQL', 'thay screenshot bằng SQL', 'cross-check SQL PowerBI', 'weekly revenue SQL'"
category: data-science
tags: [sql, ikko, revenue, ssot, pipeline, powerbi, cross-check, verified]
related_skills: [sqlserver-ikkopos-client, weekly-revenue-pipeline, weekly-revenue-screenshot-pipeline, verify-parser-output, reviewer-node, ikko-sql-firewall-patterns, lusine-sql-scripting, warren-sql-parser-build]
---

# lusine-sql-revenue — SQL Revenue Pipeline

> Query thẳng IKKO SQL → NET revenue matching PowerBI. Thay thế OCR screenshot pipeline.

## 🔑 Công thức xác nhận (cross-checked 2026-07-24, 99.9% khớp PowerBI)

### Cross-Check Proof (ngày 23/07/2026)

| Check | SQL (corrected) | PowerBI | Delta |
|-------|-----------------|---------|-------|
| NET Revenue | 91.0M × 0.882 = **80.3M** | 80.4M | -0.13% ✅ |
| Covers (non-split) | **299** | 299 | 0% ✅ |
| Tickets | **240** | 238 | -0.83% ✅ |
| AVG Spend | 80.3M / 299 = **268,548** | 268,903 | -0.13% ✅ |
| MTD NET | 2,413.3M × 0.882 = **2,128.5M** | 2,127.5M | +0.05% ✅ |

### 5 Công thức bắt buộc

```python
# 1. NET REVENUE: TẤT CẢ orders (kể cả split), ×0.882
NET_REVENUE = SUM(AmountWithDiscount) * 0.882

# 2. COVERS: LOẠI Split Order! GuestCount bị đếm trùng trên split
COVERS = SUM(GuestCount) WHERE OrderType != 'Split Order'

# 3. TICKETS: TẤT CẢ orders
TICKETS = COUNT(*)

# 4. AVG SPEND/COVER
AVG_SPEND = NET_REVENUE / COVERS

# 5. MTD/YTD
MTD = SUM(AmountWithDiscount * 0.882) WHERE ShiftDate BETWEEN '{month}-01' AND '{date}'
YTD = SUM(AmountWithDiscount * 0.882) WHERE ShiftDate BETWEEN '{year}-01-01' AND '{date}'
```

**0.882** = net/gross ratio (sau VAT 8% + service charge). Cross-checked daily + MTD vs PowerBI ngày 23/7.

## Query Patterns

### Doanh số 1 ngày (có filter split + deleted/storned)
```sql
-- Revenue + Tickets: TẤT CẢ orders
SELECT DepartmentCode,
  SUM(AmountWithDiscount) gross,
  COUNT(*) tickets
FROM dbo.Orders
WHERE ShiftDate = '2026-07-23'
  AND DepartmentCode IN ('LSLTT','LU5','LU7')
  AND OrderDeleted = 'NOT_DELETED'
  AND Storned = 'FALSE'
GROUP BY DepartmentCode

-- Covers: LOẠI Split Order
SELECT DepartmentCode,
  SUM(GuestCount) covers
FROM dbo.Orders
WHERE ShiftDate = '2026-07-23'
  AND DepartmentCode IN ('LSLTT','LU5','LU7')
  AND OrderType != 'Split Order'
  AND OrderDeleted = 'NOT_DELETED'
  AND Storned = 'FALSE'
GROUP BY DepartmentCode
```

### MTD + YTD
```sql
-- MTD
SELECT SUM(AmountWithDiscount) FROM dbo.Orders
WHERE ShiftDate BETWEEN '2026-07-01' AND '2026-07-23'
  AND DepartmentCode IN ('LSLTT','LU5','LU7')

-- YTD (cho Y/Y: query thêm cùng kỳ năm trước)
SELECT SUM(AmountWithDiscount) FROM dbo.Orders
WHERE ShiftDate BETWEEN '2026-01-01' AND '2026-07-23'
  AND DepartmentCode IN ('LSLTT','LU5','LU7')
```

### Doanh số cả tuần (cho pipeline)
```sql
SELECT DepartmentCode,
  SUM(AmountWithDiscount) gross,
  SUM(GuestCount) covers,
  COUNT(*) tickets
FROM dbo.Orders
WHERE ShiftDate BETWEEN '2026-07-20' AND '2026-07-26'
  AND DepartmentCode IN ('LSLTT','LU5','LU7')
  AND OrderDeleted = 'NOT_DELETED'
  AND Storned = 'FALSE'
GROUP BY DepartmentCode
```

## Target từ Budget file

**SSOT:** `vault/30_KNOWLEDGE_BASE/wiki/01_P&L_Budget/Budget_vs_Actual.md`

Target tháng từ CFO → tính daily/weekly:
```python
DAILY_TARGET = monthly_target / days_in_month
WEEKLY_TARGET = DAILY_TARGET × 7
TARGET_ACHV% = (actual_wtd / (DAILY_TARGET × elapsed_days)) × 100
```

Jul 2026 targets (31 ngày):
| Store | Monthly | Daily | Weekly |
|-------|---------|-------|--------|
| LU3 | 1,337.7M | 43.1M | 302.0M |
| LU5 | 1,031.1M | 33.3M | 232.8M |
| LU7 | 1,201.2M | 38.7M | 271.2M |
| ALL | 3,570.0M | 115.2M | 806.1M |

## Prerequisites (giống sqlserver-ikkopos-client)

- [ ] VPN DrayTek TLG VPN → IP 10.28.15.x
- [ ] `vault/.scripts/sqlserver_client/sqlclient.py`
- [ ] `MSSQL_DATABASE=iikoAPI`
- [ ] Store mapping: LSLTT=LU3, LU5=LU5, LU7=LU7

## Quick ad-hoc standalone query (temp script)
Khi Bố hỏi 1 câu SQL nhanh ngoài pipeline → viết temp `.py` trong `vault/.scripts/`, import `sqlclient`, **PHẢI gọi `sqlclient.load_env()` trước `run_query`**. Pattern + gotchas (load_env quên → access denied; MSYS path double-prefix) → `references/standalone-query-pattern.md`.

## Pipeline Integration (v3 Plan — approved 2026-07-24)

Thay OCR screenshot bằng SQL query:
1. Query SQL tuần trước (T2: tuần vừa xong)
2. Build payload giống format OCR parser
3. Verify gate: L1 sum-check (±0.1%), L3 internal reconcile
4. Write SSOT → Dashboard → Git → TG report
5. Target từ Budget file (không cần BI screenshot)

**Script mới:** `revenue_sql_parser.py` (T1)
**Orchestrator update:** `--source sql` flag (T2)

## Pitfalls

- **🔴 COVERS DOUBLE-COUNT — FIXED (2026-07-24):** `GuestCount` bị đếm trùng trên split orders. LU3 ngày 23/7: 15/86 orders là `OrderType='Split Order'` → covers 122 (sai) vs 107 (đúng). **Fix:** LUÔN lọc `WHERE OrderType != 'Split Order'` khi query covers. Revenue và tickets thì query TẤT CẢ orders (split order vẫn có doanh thu thật). Kết quả: covers khớp PowerBI 100% (299 vs 299).
- **Revenue SQL = GROSS, PowerBI = NET:** Luôn × 0.882 trước khi so sánh hoặc ghi SSOT.
- **OrderDeleted là NVARCHAR:** filter `= 'NOT_DELETED'`, không dùng `= 0`.
- **Storned là NVARCHAR:** filter `= 'FALSE'`, không dùng `= 0`.
- **AmountWithoutDiscount < AmountWithDiscount:** Ngược logic thông thường vì AmountWithDiscount đã include service charge. LUÔN dùng AmountWithDiscount cho revenue.
- **VPN required:** Nếu VPN đứt → fallback OCR pipeline. Cron cần alert Telegram khi VPN fail.
- **Target monthly → daily:** Dùng `days_in_month` thực tế (30/31/28), không hardcode 30.
- **🔴 QUÊN `sqlclient.load_env()` TRƯỚC `run_query` (2026-07-28):** Viết temp `.py` import `sqlclient` rồi gọi `run_query` ngay → connection string `SERVER=None` → `OperationalError 08001 SQL Server does not exist or access denied`. `.env` chỉ auto-load BÊN TRONG `main()`, import module KHÔNG load. **Fix:** gọi `sqlclient.load_env()` ngay sau `import sqlclient`. Full pattern + MSYS double-prefix → `references/standalone-query-pattern.md`.
- **MSYS path double-prefix:** gọi `python3` Windows-native với `C:/Users/...` (forward-slash), KHÔNG `/c/Users/...` (MSYS convert thành `C:\c\Users\...` → FileNotFoundError).
