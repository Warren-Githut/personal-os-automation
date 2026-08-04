---
name: sqlserver-ikkopos-client
description: Kết nối read-only SQL Server IKKO POS (iikoAPI) — query doanh số, covers, best seller, GP%. Dùng khi Bố hỏi phân tích doanh số/best seller/so sánh kỳ từ nguồn IKKO SQL.
version: 1.0.0
trigger: Bố hỏi "doanh số LUx", "best seller", "top món", "GP%", "so sánh kỳ IKKO", "query DB", "doanh thu tháng X"
category: data-science
tags: [sql, ikko, pos, doanh-so, best-seller, gp, sqlserver]
related_skills: [warren-parser-gate, verify-parser-output, reviewer-node, warren-sql-parser-build, ikko-sql-firewall-patterns, lusine-sql-revenue, lusine-sql-scripting]
---

# sqlserver-ikkopos-client

> Kết nối read-only IKKO POS SQL Server. 5 bảng, 1.2M orders, 10 năm data. Tất cả query qua tool `sqlclient.py` — firewall read-only chặn INSERT/UPDATE/DELETE.

## Prerequisites (trước mỗi query)

- [ ] **VPN:** DrayTek Smart VPN Client → profile `TLG VPN` → status Connected (IP 10.28.15.x)
- [ ] **Tool path:** `vault/.scripts/sqlserver_client/sqlclient.py`
- [ ] **DB:** `iikoAPI` (chỉ DB này login `pi` có quyền — không access được Chain/Procurement)
- [ ] **Driver:** `SQL Server` (legacy ODBC, không hỗ trợ Encrypt/TrustServerCertificate)

## Schema (luôn nằm trong tool context)

| Bảng | Cột chính | Dùng cho |
|------|-----------|----------|
| Orders | ShiftDate, DepartmentCode, GuestCount, AmountWithoutDiscount, AmountWithDiscount, ServiceCharge, TaxSum, OpenTime, CloseTime | Doanh số, covers, giờ cao điểm |
| Dishes | DishName, DishCode, Category, DishGroup, Quantity, AmountWithoutDiscount, **Cost** | Best seller, GP%, category mix |
| Payments | PaymentType (CASH/CARD), Amount | Split thanh toán |
| Discounts | DiscountType, DiscountName, Amount | Phân tích khuyến mãi |
| Taxes | TaxGroup, TaxRate, Amount | VAT breakdown |

**Store mapping:** LSLTT=LU3, LU5=LU5, LU7=LU7

## Query Workflow (6 bước — completion criterion mỗi bước)

### B1. Verify VPN
```bash
# Completion: thấy IP 10.28.15.x trong ipconfig
python3 -c "import socket; s=socket.socket(); s.settimeout(3); s.connect(('10.28.15.63',9433)); print('✅ VPN OK'); s.close()"
```
→ Nếu timeout: báo Bố "VPN chưa bật, cần mở DrayTek TLG VPN".

### B2. Load tool + set DB
```bash
cd vault/.scripts/sqlserver_client
export MSSQL_DATABASE=iikoAPI
```

### B3. Chạy query (read-only, chỉ SELECT/WITH)
Query qua `sqlclient.py query "SELECT ..."` hoặc inline Python `import sqlclient`.

**Query patterns có sẵn (copy-paste):**

```sql
-- Doanh số theo store + ngày
SELECT DepartmentCode, ShiftDate,
  SUM(AmountWithDiscount) revenue, SUM(GuestCount) covers
FROM dbo.Orders
WHERE ShiftDate>='2026-07-01' AND DepartmentCode IN ('LSLTT','LU5','LU7')
GROUP BY DepartmentCode, ShiftDate ORDER BY ShiftDate

-- Top N best seller + GP%
SELECT TOP 5 DishName, SUM(Quantity) qty,
  SUM(AmountWithoutDiscount) rev, SUM(Cost) cost,
  ROUND((SUM(AmountWithoutDiscount)-SUM(Cost))/SUM(AmountWithoutDiscount)*100,1) gp
FROM dbo.Dishes
WHERE DepartmentCode='LU5' AND ShiftDate>='2026-01-01'
  AND Category='Food' AND DishName!=''
GROUP BY DishName ORDER BY qty DESC

-- Covers theo giờ (peak hours)
SELECT DATEPART(HOUR, OpenTime) h, SUM(GuestCount) covers
FROM dbo.Orders
WHERE DepartmentCode='LSLTT' AND ShiftDate>='2026-07-01'
GROUP BY DATEPART(HOUR, OpenTime) ORDER BY h
```

### B4. Format output → markdown
- Revenue: `M` (triệu VND, 1 decimal) — `round(val/1e6, 1)`
- GP%: `round(gp, 1)` + `%`
- Bảng: `| | | | |` format, tiếng Việt có dấu
- Confidence tags: [HIGH]/[MOD]/[LOW] cho insight

### B5. 🚨 Reviewer-node gate (bắt buộc — 2026-07-24 rule)
**Trước khi báo Bố kết quả phân tích từ SQL:**
1. `verify-parser-output` (nếu có số aggregate từ query)
2. `delegate_task` spawn `reviewer-node` (goal="Review this SQL analysis output", context=output markdown + domain checklist OPS)
3. Chỉ báo Bố khi có token `🔍 REVIEWER: ✅`

→ **Completion:** output được review bởi reviewer-node (fresh context).

### B6. Save vào vault (nếu phân tích mới)
- File: `10_OPERATION_DATA/15_IKKO_SQL_Analysis.md`
- Prepend entry mới lên đầu file
- Update `last_updated` frontmatter
- Update `00_OPERATION_INDEX.md`

## Pitfalls

- **Quên VPN:** IP không phải 10.28.15.x → query timeout. Check B1 trước.
- **Sai database:** `MSSQL_DATABASE` phải là `iikoAPI` — Chain/Procurement bị chặn.
- **Driver cũ:** không dùng `Encrypt=`/`TrustServerCertificate=` với driver `SQL Server` (lỗi "Invalid connection string attribute"). Tool `sqlclient.py` tự xử lý.
- **DepartmentCode ≠ store name:** LU3 = `LSLTT` (legacy code). KHÔNG dùng `LU3` trong query.
- **Category rỗng:** Lọc `Category='Food'` tránh modifier rác (DINE IN, Customer, VM...).
- **Cost = 0:** Một số món có thể có Cost=0 (chưa nhập). GP% sẽ là 100% sai → flag khi thấy Cost=0.
- **VPN disconnect giữa chừng:** DrayTek VPN có thể ngắt sau 1 thời gian. Re-check B1 nếu query timeout.

## Verification

- [ ] VPN active (B1 checked)
- [ ] Query chỉ SELECT/WITH (firewall enforced by sqlclient.py)
- [ ] Output Vietnamese + M format + [CONFIDENCE] tags
- [ ] Reviewer-node passed (B5)
- [ ] Vault saved + index updated (B6, nếu persist)
