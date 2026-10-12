---
name: ops-purchasing-dashboard
description: Builds an interactive HTML Purchasing Dashboard for L-Concepts (LU3, LU5, LU7) from monthly Purchases report by goods and suppliers Excel exports. Trigger when user says purchasing dashboard, chạy purchasing, or drops Purchases YYYY.MM.xlsx files.
---

# Ops Purchasing Dashboard — L-Concepts

## Files needed

Bố gửi file Purchases tháng:
- Purchases YYYY.MM.xlsx (hoặc tập file nhiều tháng)

## Steps

1. Đọc mọi file tháng.
2. Lọc chỉ external supplier (loại bỏ internal transfer và LU4).
3. Tính spend theo store và category.
4. Phân tích biến động giá: dollar-impact movers, Laspeyres index, supplier price creep.
5. Xuất HTML dashboard với store selector, chart, bảng item detail.
6. Lưu Purchasing_Dashboard_YYYY-MM.html vào artifacts/.

## Notes

- Internal transfer (có ":" trong contractor) không tính là purchase thật.
- LU4 đã đóng, loại bỏ.
- Chi tiết đầy đủ xem file gốc Vicky trong purchasing-dashboard.zip.
