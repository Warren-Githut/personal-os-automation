---
name: personal-morning-brief-fixed
description: "Fixed fork of personal-morning-brief — same brief protocol, with corrected file paths + weekend awareness. Cron: hằng ngày 07:00."
version: 1.1
tags: [personal_os, daily, brief, cron, synthesis]
---

# /personal-morning-brief — Daily Morning Brief

## Purpose
Mỗi sáng lúc 07:00 — đọc toàn bộ vault state + live data (thị trường, thời tiết) → compile 1 bản tin ngắn gọn (Tiếng Việt có dấu, conclusion-first) → deliver trực tiếp cho Warren. Không ghi vào vault file — chỉ deliver.

**Trigger:** Cron job mỗi ngày 07:00 (không interactive — auto-deliver)

## Protocol — 7 blocks, execute in order

### Block 0: Load session state
- Đọc `00_CORE_LOGIC/PERSONAL_CONTEXT.md` — đặc biệt §2 (Family), §4 (Health), §11 (Thinking Patterns)
- Đọc `00_CORE_LOGIC/PERSONAL_MEMORY.md` (nếu có) — áp dụng preferences/corrections
- Đọc `00_CORE_LOGIC/PERSONAL_USER.md` — Warren profile
- Đọc `00_CORE_LOGIC/STOCK_CONTEXT.md` (nếu cần trader reference) — watchlist, catalysts, valuations

### Block 1: Pháp lý & Gia đình 🏛️
- Đọc `_cases/active/*.md` — đặc biệt `legal_divorce_court_GG_access.md`
- Check `follow_up` date: nếu hôm nay = follow_up → 🔴 KHẨN
- **Cũng check `_cases/closed/*.md`** — closed cases có thể còn follow_up cũ chưa được dọn.
  Nếu closed case vẫn còn follow_up date = hôm nay → stale reference → báo cáo như 🟡 cần cleanup.
- Tính days_since_last_update: nếu > 7 ngày → 🔴 Critical gap
- Tóm tắt: status, follow_up, next step

### Block 2: Sức khỏe 🏥
- Đọc `10_PULSE/Daily_Pulse.md` — latest 3-5 entries (lấy health bullets)
- Đọc `10_PULSE/050_Health_Log.md` — latest health metrics
- Nếu `10_PULSE/051_Sleep_Log.md` tồn tại → đọc latest entries
- So sánh với baseline từ PERSONAL_CONTEXT.md §4 (Health Baseline)
- **Flags cần check:**
  - Cân nặng: deviation ≥ ±2kg từ baseline 63kg
  - Huyết áp: deviation ≥ ±10 từ baseline (95-99 systolic)
  - Sleep: < 6h × 2 đêm liên tiếp
  - Fasting: > 18h kéo dài > 3 ngày
  - Workout: 0 → nhắc nhở
  - LDL/ApoB chưa có intervention → flag nếu lab cũ > 30 ngày

### Block 3: Thị trường 📊
- **Weekend rule:** Nếu hôm nay là Thứ Bảy/Chủ Nhật → search ngày giao dịch cuối cùng (Thứ Sáu), không search "hôm nay".
  Công thức: `ngày_gd_cuối = hôm_nay - (weekday - 5)` (ví dụ: Thứ Bảy → search "VN-Index 03/07").
- Web search: "VN-Index {ngày}", "dầu Brent giá {ngày}"
- Web search: giá GAS, PVD — search LUÔN nếu watchlist có GAS/PVD (không đợi "nếu cần" — mất 2 search, chi phí thấp)
- Nếu đầu tháng/tuần → search macro news (FTSE, LDR, chính sách)
- So sánh với STOCK_CONTEXT.md (watchlist + valuations)
- **Flags cần check:**
  - VN-Index: biến động > 3% so với phiên trước
  - Dầu Brent: biến động > 5% so với phiên trước
  - Giá GAS/PVD biến động > 5%
  - Catalyst stacking (FTSE, LDR, earnings, etc.)
  - Nếu dữ liệu live khác xa dữ liệu STOCK_CONTEXT.md cũ → flag discrepancy

### Block 4: Inbox & Pending 📥
- Kiểm tra `_inbox/01_unprocessed/` — còn item nào không?
- Kiểm tra `_inbox/02_processed_archived/stock_pending/` — Bonnejed JSON pending? Tính days_since_creation.
- Kiểm tra pending stock ingests (BCTC PDFs, broker files)
- Nếu inbox sạch → ✅ Không có gì pending
- Nếu có item tồn > 3 ngày → flag 🟡 (nếu > 7 ngày → 🔴)
- Nếu có stock_pending files tồn > 3 ngày → flag 🟡

### Block 5: Thời tiết 🌤️
- Web extract: `https://nchmf.gov.vn/kttvSite/vi-VN/1/sai-gon-tp-ho-chi-minh-w15.html`
- Extract: nhiệt độ hiện tại, max hôm nay, xác suất mưa
- Gợi ý nếu cần: mang ô (mưa > 60%), mặc áo gì (nhiệt độ)

### Block 6: Hôm nay priorities 🗓️
- Tổng hợp từ các block trên → xác định priorities:
  - 🔴 P0: Khẩn cấp — cần action hôm nay
  - 🟡 P1: Quan trọng — cần tracking
  - 🟢 P2: Nên làm
- Gợi ý cụ thể: "Đo BP lại", "Kiểm tra Bonnejed JSON", "Gọi hỏi thăm GG"

### Block 7: Overall assessment 💡
- 1-2 câu tổng quan: tình hình tổng thể, điểm đáng chú ý
- Dùng confidence tag: [HIGH/MOD/LOW]
- Nếu có paradox/mâu thuẫn → flag rõ

## Output Format
(Giống format trong original skill — xem personal-morning-brief.)

## Web Search Patterns (exact queries to use)

```python
# Market data — date = last trading day (Fri or earlier if weekend)
queries = [
    "VN-Index {last_trading_day}",
    "dầu Brent giá {last_trading_day}",
    "GAS cổ phiếu giá {last_trading_day}",
    "PVD cổ phiếu giá {last_trading_day}",
]
# Macro news (first-of-month / first-of-week)
macro_queries = [
    "FTSE Vietnam upgrade September 2026",
    "LDR easing TT 25/2026 Việt Nam",
    "VN30 stock market news {date}",
]
```

## Cross-Reference Rules (improved)
- **PERSONAL_CONTEXT.md** cho health baseline (§4), family status (§2), thinking patterns (§11)
- **STOCK_CONTEXT.md** cho watchlist, valuations, catalysts
- Search results là live data → trust search over vault data if contradictory
- Flag discrepancies > 5% giữa vault và live data

## Signal Priority (cho overall assessment)

| Signal | Weight | Example |
|--------|--------|---------|
| 🔴 Legal gap > 7 days | Highest | "13 NGÀY chưa update — paralyses all financial planning" |
| 🩺 Health threshold breach | High | "Cân nặng -2kg trong 5 ngày" |
| 🔥 Catalyst × Block | High | "Catalysts stacking nhưng capital blocked bởi EF + legal" |
| 🟡 Paradox | Medium | "Sleep improves, weight drops, BP creeps — contradictory trend" |
| 🟡 Pending gunk > 7 days | Medium | "Bonnejed JSON tồn 13 ngày" |
| ✅ Normal | Low | "Inbox sạch, market ổn định" |

## Pitfalls / Lessons (updated)

1. **PERSONAL_CONTEXT.md §4 may be stale on commodity prices** — Dầu Brent được ghi $87-93 trong vault nhưng thực tế có thể đã giảm 23%. Luôn fetch live price và flag discrepancy.
2. **Daily_Pulse có thể outdated** — Warren ngừng Daily_Pulse khi stress (legal). Health data vẫn có thể từ 050_Health_Log hoặc 051_Sleep_Log. Cross-reference, đừng kết luận "không có health data" từ Daily_Pulse gap.
3. **051_Sleep_Log.md có thể chưa tồn tại** — PULSE_INDEX.md liệt kê nó nhưng file có thể chưa được tạo. Nếu không tìm thấy, skip gracefully.
4. **Inbox 01_unprocessed/ thường empty** — process-notes cron chạy trước morning brief. Nếu inbox sạch, kiểm tra `_inbox/02_processed_archived/stock_pending/` cho items pending.
5. **Ngày cuối tuần (Sat-Sun) không có giao dịch VN-Index** — Dùng dữ liệu phiên cuối cùng của tuần trước. Search "{ticker} {last trading day}" thay vì "hôm nay". Công thức: last_trading_day = today - (weekday - 5) for Sat, today - (weekday - 6) for Sun.
6. **Số liệu PERSONAL_CONTEXT.md cần verify lại sau 7+ ngày** — Nếu PERSONAL_CONTEXT.md viết "Dầu Brent $87-93" từ 7 ngày trước, fetch live data và tự động so sánh. Nếu khác biệt lớn, ghi chú trong brief.
7. **Confidence tag untagged = LOW** — Mặc định [LOW] nếu không tag. Chỉ dùng [HIGH] khi dữ liệu đã verify từ 2+ nguồn.
8. **SILENT protocol** — Nếu không có gì mới so với hôm qua (cùng số liệu, cùng trạng thái, không có follow_up hôm nay), trả về "[SILENT]" để suppress delivery.
9. **Closed cases can have stale follow_up** — Case đã đóng nhưng file vẫn còn follow_up date cũ chưa dọn. Check `_cases/closed/*.md` follow_up và báo 🟡 nếu phát hiện.
10. **Stock_pending có thể tồn lâu** — Bonnejed JSON files có thể tích tụ nhiều ngày. Tính days_since_creation cho file mới nhất và cũ nhất để ước lượng backlog.

## Related Skills
- `personal-weekly-connections`
- `personal-context-update`
- `personal-process-notes`
- `capture-sleep`
- `stock-capture`
- `personal-inbox-routing`
- **NOTE:** Original skill `personal-morning-brief` (warren-profile) có lỗi file path — dùng bản `personal-morning-brief-fixed` này thay thế khi run cron.