---
name: vault-block-format
description: Decision-first 3-second-scan format + clickable cross-ref + giá SSOT cron convention cho stock vault data blocks. Bố duyệt 02/08/2026.
---

# Vault Block Format Convention (stock vault)

## Nguyên tắc (Bố duyệt 02/08/2026)
Dân đầu tư 30 năm phải nhìn block trong 3 giây biết chỗ nào là QUYẾT ĐỊNH.

### 1. Decision-first
- Dòng 🎯 **QUYẾT ĐỊNH** lên ĐẦU block: kết luận (✅/❌) + điểm số ảnh hưởng.
- Số liệu tham khảo (đăng ký, giá, window) xuống DƯỚI.
- Status có màu: 🟡 Registered / 🟠 Partial / 🟢 Completed / 🔴 Cancelled.

### 2. Clickable cross-ref (full path, relative)
- Dùng markdown link đầy đủ, KHÔNG dùng placeholder `../03X-[TICKER]`.
- Từ `030-Companies/100_Compliance/` → lùi 2 cấp: `[...](../../030-Companies/040-PNJ/Catalyst-watch.md)`
- Format: `[030-Companies/040-PNJ/Catalyst-watch.md](../../030-Companies/040-PNJ/Catalyst-watch.md)`

### 3. Giá SSOT = cron Telegram daily
- Giá tham khảo = từ cron `stock-price-daily` (Entrade/Yahoo, 15:30 T2-T6, sync `Holdings.md`/`Candidates_Watchlist.md`).
- KHÔNG dùng giá trade-confirmation cũ (giá Bố mua ngày X đã lỗi thời).
- KHÔNG web search bịa (Firecrawl hay hết credit → dùng giá vault).

### 4. Actual-only rule (insider-dealing)
- Đăng ký ≠ THỰC MUA. Chỉ THỰC MUA settled ≥100 tỷ mới Meets=✅ + điểm.
- Ví dụ: ĐK 100 tỷ nhưng chỉ mua 50 tỷ (giá không thích hợp) → ❌.

## Template (insider-dealing block)
```
### [TICKER] — [Tên] ([Vai trò]) — [MM/YYYY]
🎯 **QUYẾT ĐỊNH:** Meets >100 tỷ (ACTUAL) = ✅/❌ | Điểm cộng deploy = +2/0
- Lý do: [...]
- Status: 🟡 Registered / 🟠 Partial / 🟢 Completed / 🔴 Cancelled
- Đăng ký: [X] cp | window [từ]→[đến]
- Tổng ĐK [Y] tỷ (giá SSOT [Z] [HIGH-cron])
- THỰC MUA: [Z] cp | tổng THỰC [W] tỷ | ngày kết thúc [DD/MM/YYYY]
- 📎 Catalyst-watch: [030-Companies/03X-[TICKER]/Catalyst-watch.md](../../030-Companies/03X-[TICKER]/Catalyst-watch.md)
- Ghi chú: [...]
```

## Example (PNJ — Phan Quốc Công, TV HĐQT, 08/2026)
```
### PNJ — Phan Quốc Công (TV HĐQT) — 08/2026
🎯 **QUYẾT ĐỊNH:** Meets >100 tỷ (ACTUAL) = ❌ | Điểm cộng deploy = 0/10
- Lý do: Chưa kết thúc window (14/08). ĐK 31 tỷ < 100 tỷ dù mua đủ → khó đạt.
- Status: 🟡 Registered (đang chờ thực mua)
- Đăng ký: 1.000.000 cp | window 17/07/2026→14/08/2026
- Tổng ĐK ~31 tỷ (giá SSOT 31.000 [HIGH-cron 31/07])
- THỰC MUA: 0 cp | tổng THỰC 0 tỷ | ngày kết thúc: —
- 📎 Catalyst-watch: [030-Companies/040-PNJ/Catalyst-watch.md](../../030-Companies/040-PNJ/Catalyst-watch.md)
- Ghi chú: LẦN 1 (đăng ký). Chờ 14/08 báo thực mua → con tính lại Meets.
```
