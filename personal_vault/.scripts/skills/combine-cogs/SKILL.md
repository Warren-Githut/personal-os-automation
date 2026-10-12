---
name: combine-cogs
description: Generate monthly COGS dashboard for Lusine stores (LU3, LU5, LU7). Use when user says chạy COGS tháng X, combine-cogs, or COGS dashboard. Requires 6 inventory files (BAR + KIT per store) and optional Sales Report.
---

# Combine COGS — Monthly Dashboard

## Files needed

Bố gửi 6 file inventory tháng X:
- LU3-BAR YYYY-MM.xlsx
- LU3-KIT YYYY-MM.xlsx
- LU5-BAR YYYY-MM.xlsx
- LU5-KIT YYYY-MM.xlsx
- LU7-BAR YYYY-MM.xlsx
- LU7-KIT YYYY-MM.xlsx

Tùy chọn: Report.xlsx (có sheet Data) để lấy Revenue chính xác.

## Steps

1. Đọc cột theo tên (Opening, Sales, Write-offs, Inventory surplus, Inventory shortage, Closing). Không dùng vị trí cố.
2. Tính COGS = Sales + Write-off + Reconciliation (Surplus + Shortage).
3. Xuất HTML dashboard:
   - KPI cards (Revenue, COGS, COGS %, Write-off, Net variance)
   - Chart Revenue vs COGS
   - Chart Food vs Beverage
   - Bảng WO & Recon % of revenue
   - Top 25 items (Write-off / Shortage / Surplus tabs)
   - Monthly tracking (nếu có data tháng trước)
4. Lưu file COGS_Dashboard_YYYY-MM.html vào artifacts/.

## Notes

- Inventory Sales là số âm (cost). Revenue lấy từ Report nếu có.
- Tháng 8 có cột VAT. Tháng 9 không có. Đọc theo tên cột để an toàn.
- Store selector: All / LU3 / LU5 / LU7.
