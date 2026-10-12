---
name: ops-revenue-snapshot
description: Build or refresh the L'Usine daily revenue snapshot. Trigger when user says revenue snapshot, chạy revenue, or update revenue numbers. Requires VPN + SQL access.
---

# Ops Revenue Snapshot — L'Usine

## Files needed

- VPN connected.
- SQL Server access (iikoAPI).
- Daily_Budget_Target_by_Store.xlsx (nếu có).

## Steps

1. Confirm VPN. Nếu timeout thì báo Bố.
2. Query Today / MTD / YTD / last-year / last-month.
3. Lấy top 10 items, Food/Bev mix, day-part.
4. Copy report_template.html và điền số mới.
5. Xuất Revenue_Snapshot_YYYY-MM-DD.html.

## Notes

- Cần VPN. Không hardcode password.
- Store colors: LU3 navy, LU5 teal, LU7 bronze.
- Chi tiết đầy đủ xem file gốc Vicky trong revenue-snapshot.zip.
