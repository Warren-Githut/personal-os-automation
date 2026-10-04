---
name: verify-data-window
description: "Gate bắt buộc TRƯỚC mọi số aggregate/baseline trong analysis L'Usine — đếm số tuần thật CÓ ĐỦ data giờ (không compressed), <4 tuần → DỪNG + hỏi Bố. Chạy trước promo-eval / ops-mkt-manager-os DISCOVER / dashboard / wiki analysis."
version: 1.0.0
tags: [data, governance, verify, window, baseline, lusine]
category: ops
related_skills: [promo-eval, ops-mkt-manager-os, verify-parser-output, ops-pnl-ingest, ops-weekly-report]
---

# verify-data-window — Data Window Gate (L'Usine)

> **Mục đích:** Ngăn agent xuất baseline/aggregate số từ <4 tuần data, hoặc dùng tuần compressed (thiếu giờ) làm baseline. Enforce HARD RULE WARREN_MEMORY 2026-07-17 + gate 2026-07-19.
> **Mode:** Pure prompt-skill. KHÔNG script. Chạy TRƯỚC KHI gõ bất kỳ số aggregate nào.

---

## KHI NÀO DÙNG

- Sắp tính baseline (covers/tuần, revenue, uplift, target) từ `09_Hourly` / `01_Weekly` / bất kỳ rolling log.
- Sắp chạy promo-eval Mode B, ops-mkt-manager-os DISCOVER, dashboard gen, wiki analysis.
- Mọi task "phân tích", "so sánh", "eval promo", "baseline".

---

## QUY TRÌNH (HARD — 4 bước)

1. **Liệt kê tuần có data ĐỦ GIỜ** trong source (vd `09_Hourly_Cover_Revenue_Log.md`):
   - Tuần có breakdown theo giờ (bảng `Hourly Detail` với cột M-T-W-T-F-S-S) = **1 tuần đủ giờ** ✅
   - Tuần ghi `<!-- Compressed -->` (chỉ còn JSON total, thiếu giờ) = **0 tuần đủ giờ** ❌ (KHÔNG tính)
2. **Đếm N** = số tuần đủ giờ liên tiếp gần nhất.
3. **Quyết định:**
   - N ≥ 4 → ✅ TIẾP TỤC, dùng N tuần đó làm baseline.
   - N < 4 → 🔴 DỪNG. KHÔNG gõ số. Hỏi Bố approve (Zone 🟡) mới tiếp.
4. **In dòng minh bạch BẮT BUỘC** vào output:
   - `✅ DATA WINDOW: N tuần đủ giờ (Wxx–Wyy), exclude Wzz compressed`
   - hoặc `🔴 THIẾU DATA: chỉ N tuần đủ giờ (Wxx–Wyy), cần Bố duyệt trước khi chạy.`

---

## VÍ DỤ (từ lỗi 19/07)

**Sai (con từng làm):** Lấy W28 đơn lẻ làm baseline trưa → vi phạm (<4 tuần).

**Đúng:**
- `09_Hourly` có: W28 (đủ giờ), W27 (đủ), W26 (đủ), W25 (COMPRESSED → 0), W24 (COMPRESSED → 0).
- N = 3 (W26/W27/W28).
- → `🔴 THIẾU DATA: chỉ 3 tuần đủ giờ (W26–W28), W25/W24 compressed, cần Bố duyệt trước khi chạy.`
- → DỪNG, hỏi Bố: (a) duyệt 3 tuần, hoặc (b) cho con restore W25/W24 từ dashboard HTML để có 4 tuần đủ giờ.

---

## BANNED PATTERNS

- ❌ Dùng 1 tuần (W28 đơn lẻ) làm baseline.
- ❌ Đếm tuần compressed vào N (W25 compressed ≠ 1 tuần đủ giờ).
- ❌ Claim "đủ 4 tuần" khi chưa verify từng tuần có giờ.
- ❌ Gõ số aggregate trước khi in dòng DATA WINDOW.
- ❌ Tự bịa data tuần thiếu.

---

## INTEGRATION

- **promo-eval Mode B:** step 3.5 (Data Window Gate).
- **ops-mkt-manager-os DISCOVER:** step 4.5.
- **WARREN_MEMORY HARD RULE:** dòng `[2026-07-19] GATE BẮT BUỘC...`.
- Mọi module analysis khác (dashboard, wiki, ops-weekly-report) → chạy gate này trước bước compute.

---

## VERIFY (sau sửa skill)

- [ ] Gate có 4 bước rõ ràng (liệt kê → đếm → quyết → in dòng)
- [ ] Phân biệt compressed = 0 tuần đủ giờ
- [ ] Dòng minh bạch có cả 2 trạng thái ✅/🔴
- [ ] Link về promo-eval + ops-mkt-manager-os step tương ứng
- [ ] Tiếng Việt có dấu
