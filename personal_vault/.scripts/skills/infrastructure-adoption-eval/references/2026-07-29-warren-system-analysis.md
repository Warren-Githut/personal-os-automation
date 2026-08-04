# Reference: Warren System Analysis (2026-07-29)

> Full analysis từ session evaluate "có nên xài Nous Cloud / Hetzner Cloud?"

## Hệ Thống Hiện Tại

**Workload:** Siêu nhẹ.
- 154 scripts (4.4MB trong `.scripts/`)
- 25 cron jobs (Hermes scheduler)
- 95% là no_agent (0 token, chạy <1s) hoặc LLM-driven gọi DeepSeek API (cloud)

**Compute heavy lifting:** KHÔNG. Không AI inference local, không GPU, không render nặng.

**Cần laptop ON:**
- Cron: giờ HC 6-17 Mon-Fri
- Telegram bot LUsineWorkBot: cần 24/7 → chết nếu laptop sleep
- IKKO SQL VPN: chỉ khi query

**Chi phí LLM:** DeepSeek API (billed separately, không liên quan hosting)

## Option Analysis

| Option | Tháng | Lợi | Hại | Verdict |
|--------|-------|-----|-----|---------|
| **Giữ local** | 0₫ (điện ~54k) | Đang chạy, không thêm | Bot chết nếu laptop sleep | ✅ OK |
| **Hetzner CX23** | ~175k₫ | 24/7 uptime, cron+bot sống | Setup Linux, sửa Windows path, VPN IKKO, mất GUI chat | 🟡 Chưa cần |
| **Nous Cloud** | ? (preview) | 1-click deploy, auto-scale | Beta pricing, chưa clear, mất control | ❌ Chưa chín |

## Blocker Thật Sự

1. **IKKO SQL = on-prem LAN** — Cloud server ở Đức/Phần Lan ping vào L'Usine LAN qua DrayTek VPN không rõ hoạt động. Network latency có thể làm parser SQL fail.
2. **Windows hardcode paths** — `C:\Users\khoans\...` trong ~154 scripts, phải sửa toàn bộ khi sang Linux.
3. **Hermes Desktop GUI** — Cloud Hermes là CLI (Telegram-only). Bố mất kênh chat chat trực tiếp.
4. **Hybrid setup lằng nhằng** — Cloud cho cron+bot, local cho chat → 2 hệ thống, sync phức tạp.

## Robot Vacuum Test

Nếu GG sống 100% trên cloud (Bố không bật laptop):
- ✅ Telegram bot vẫn sống 24/7
- ✅ Cron chạy đúng giờ (không phụ thuộc laptop ON)
- ❌ Chat Hermes Desktop mất — chỉ còn Telegram gõ lệnh
- ❌ Obsidian vault không tự sync — mất khả năng đọc/sửa file nhanh
- ❌ Không mở được dashboard HTML local

## Khuyến Nghị

**Giữ local.** Chỉ cân nhắc cloud khi:
1. Bố cần Telegram bot 24/7 (hiện tại chết khi laptop sleep)
2. Hoặc mở LU8 thêm store → data volume ×2+
3. Hoặc Nous Cloud ra stable pricing + hỗ trợ VPN site-to-site

Trước mắt: chỉ cần setting laptop "never sleep khi cắm sạc" là giải quyết 90% vấn đề.
