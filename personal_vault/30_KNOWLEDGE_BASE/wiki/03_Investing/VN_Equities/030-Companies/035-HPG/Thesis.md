---
current_price: 22
domain: investing
type: thesis
ticker: HPG
company_name: "Cổ phần Tập đoàn Hòa Phát (HPG)"
sector: Thép
industry: "Thép xây dựng/HRC"
status: watching
created: 2026-06-20
last_updated: 2026-07-17
source_files: ["HPG_Bao_cao_phan_tich_chi_tiet_VI.pdf", "20260327-hpg-bctc-hop-nhat-nam-2025-sau-kiem-toan.pdf"]
integrity:
  status: EVALUATED
  result: EVALUATED
  score: 4/6
  last_run: 2026-06-20
  summary: >-
    Check 1-4 EVALUATED; 5-6 CLEAN. Q1/2026 OCF đã dương (6.817 tỷ), không còn mismatch với 2025.
    Còn 2 điểm cần xác nhận chi tiết: revenue spike + OCF và RPT tổng hợp cho trước khi lên GREEN/YELLOW.
valuation:
  methods: ["Munger_PE15x","Lynch_PEGY","Damodaran_SOTP","Damodaran_DCF","Peer_PE"]
  composite_intrinsic: null
  current_price: 23600
  premium_discount: null
conviction: MOD
position_target: "10%"
tags: ["HPG", "steel"]
related: ["Holdings.md", "Watchlist.md", "BCTC - Rolling.md"]
review_log:
  - date: 2026-06-20
    action: first_ingest
    note: "Create thesis from TCBS first-coverage report (15/06/2026). Source-based only; chưa có BCTC gốc."
  - date: 2026-06-21
    action: fix_vi
    note: "Sửa toàn bộ tiếng Việt có dấu theo hard rule."
---

# Thesis - HPG (Hòa Phát)

> **Trạng thái:** WATCHING - chưa vào lệnh. Chờ base-case BCTC gốc + entry trigger dưới giá hợp lý.

---

## TL;DR - Executive Summary

- **DQ2 đã vào thu hoạch:** công suất 16 triệu tấn/năm, năm 2025 sản xuất 11 triệu tấn (+26%).
- **Q1/2026 bứt phá:** doanh thu 52.901 tỷ (+40,6% YoY), LNST trên 9.000 tỷ (+170%).
- **Margin phục hồi:** biên gộp 2025 lên 15,7%, hỗ trợ bởi chênh lệch giá nguyên liệu - thành phẩm + CBPG HRC 27,83% từ 7/2025.
- **Định giá hữu dụng:** P/E TTM ~9,3x (thấp hơn ~30% so bình quân 5 năm 13,6x); EV/EBITDA ~8,6x.
- **Rủi ro chính:** chu kỳ giá thép + áp lực xuất khẩu Trung Quốc + đòn bẩy tài chính hơi cao.

---

## Quick Decision Card

| Question | Answer | Status |
|---|---|---|
| **Fair value?** | Chưa có composite. P/E peer 13,6x -> fair ~ 31.648 VND nếu EPS ~2,328đ | Pending |
| **Current premium?** | 11/06/2026: ~23.300 so với peer avg | Undervalued |
| **Integrity?** | Chưa chạy gate (chưa có BCTC gốc) | Required |
| **Entry price?** | Cần xác định sau khi có BCTC + composite | - |
| **Watch level?** | Theo dõi mốc 19.000-21.000 | Monitor |
| **Ready to buy now?** | **NO** | **HOLD** |

---

## 1. Bull Case

- **Top 30 thế giới:** DQ2 đưa HPG lên 16 triệu tấn/năm; xuất khẩu ~18-30%, rẻ hơn trong ASEAN.
- **Margin cải thiện structural:** CBPG HRC + chênh lệch nguyên liệu - thành phẩm; biên gộp lên 15,7% (2025), Q1/2026 tiếp tục tốt.
- **Capex qua đỉnh:** giảm từ 35.495 tỷ (2024) xuống 25.748 tỷ (2025); FCF hồi phục.
- **Đa dạng hóa:** HPG, HPA, BĐS KCN đẩy mạnh khi biến động ngành; giảm phụ thuộc vào thép.
- **Định giá hấp dẫn:** P/E 9,3x, P/B 1,4x (thấp hơn bình quân 5 năm). EV/EBITDA ~8,6x.

---

## 2. Bear Case / Rủi ro

- **Chu kỳ giá thép nặng nề:** HRC < 460 USD/tấn sẽ cạnh tranh mạnh -> margin giảm.
- **Tài chính cao:** Nợ vay ròng ~64.400 tỷ; Net Debt/EBITDA ~2,2x; quy mô lớn, nhạy cảm với lãi suất.
- **Chính sách thương mại bất định:** CBPG có thể điều chỉnh theo WTO/FTA; thuế tự vệ ngược EU.
- **Phụ thuộc 82% thị trường nội địa:** giảm xuất khẩu, đơn hàng lớn nhà máy + bên trong.
- **Bán phá giá/chống phá giá Trung Quốc:** áp lực giá mạnh, tỷ trọng xuất khẩu Trung Quốc lớn.

---

## 3. BCTC Q1/2026 + 2025
## 3. BCTC Q1/2026 + 2025
**Nguồn:** BCTC hợp nhất Quý I/2026 + BCTC hợp nhất 2025 đã kiểm toán Deloitte.
Raw: `bctc-hop-nhat-quy-i-2026.pdf` / `20260327-hpg-bctc-hop-nhat-nam-2025-sau-kiem-toan.pdf`
Rolling: `BCTC - Rolling.md` (newest-on-top, Q1/2026 -> 2025).

### Income Statement

| Chỉ tiêu | Q1/2026 | Q1/2025 | YoY |
|---|---|---|---|
| Doanh thu thuần | 52.901 tỷ | ~37.700 tỷ | +40,6% |
| LNST | >9.000 tỷ | ~3.300 tỷ | +170% |
| Biên LNST | ~17,1% | - | - |

### Balance + Cash

| Chỉ tiêu | 2025/2026E | Ghi chú |
|---|---|---|
| Tổng nợ vay | ~92.174 tỷ | vay ròng ~64.400 tỷ |
| Net Debt/EBITDA | ~2,2x | cần theo dõi theo biến động EBITDA |
| Chi phí lãi vay | ~3.100 tỷ/năm | 2025 |

### Cash Flow / Capex

- Capex giảm: ~35.495 tỷ (2024) -> ~25.748 tỷ (2025) -> DQ2 đẩy mạnh.
- Mục tiêu 2026: doanh thu 210.000 tỷ, LNST 22.000 tỷ (+41,8% YoY).

---

## 4. INTEGRITY GATE
## 4. INTEGRITY GATE
> Cập nhật 2026-06-20: đã có BCTC 2025 audited + Q1/2026 BCTC hợp nhất gốc. Gate đã chạy lại; verdict hiện tại: YELLOW (4/6 CLEAN; 2 yếu tố cần xác nhận chi tiết).

| # | Check | Finding | Flag |
|---|---:|---|---|
|| 1 | Revenue spike + negative OCF | Q1/2026 OCF đã dương 6.817 tỷ; 2025 OCF 17.366 tỷ, phủ định | CLEAN |
| 2 | High profit + low interest coverage | LNST tăng mạnh, lãi vay tăng 112,7% YoY Q1; EBITDA/interest đang ổn | EVALUATED |
| 3 | Related-party transactions | Chưa có tổng hợp RPT chi tiết từ thuyết minh | EVALUATED |
| 4 | Receivable/inventory build-up | Phải thu ngắn hạn tăng; hàng tồn kho giảm => cần đối chiếu chu kỳ | EVALUATED |
| 5 | Policy change | Không phát hiện thay đổi đáng kể so với 2024 | CLEAN |
| 6 | Goodwill | Không có bất thường theo báo cáo | CLEAN |

Verdict: **EVALUATED — có thể nâng lên YELLOW sau khi xác nhận RPT + coverage**.

---

## 5. Valuation

> Giá tham chiếu: **23.300 VND** | P/E TTM: **9,3x** | P/B: **1,4x** | EV/EBITDA: **8,6x**

### 5A. Munger Owner Earnings

| Multiple | FY2025E | FY2026E |
|---|---|---|
| 8x | Low | 20.800-24.000 |
| 9x (TTM coverage) | ~20.800 | 23.400-27.000 |
| 10x | ~23.160 | 26.000-30.000 |

### 5B. Peter Lynch PEGY

| Metric | FY2025 | Q1/2026 annualized | Ghi chú |
|---|---:|---:|---|
| EPS | ~2.014 đồng | ~4.688 đồng | EPS Fwd cao hơn do margin bứt phá Q1 |
| EPS growth | ~+41,8% (2025 vs 2024) | - | Tăng trưởng ấn tượng |
| P/E TTM | 9,3x | - | Trailing |
| Fair P/E (growth-adjusted) | ~11-12x | - | Không quá discount growth |
| Implied fair value | ~22.000-24.000 đồng | ~47.000 đồng | Forward cao hơn; dùng blended cho composite |

> Dùng blended EPS 3.500 đồng (giữa 2025 và 2026E) với P/E 10x cho entry, 12x cho fair => **35.000 đồng** làm trọng tâm.

### 5C. Damodaran SOTP `[MOD]`

| Scenario | Fair Value/cp |
|---|---|
| Asia steel peer avg (13,6x TTM) | 31.648 |
| HPG historical discount (~2023) | ~27.000 |
| SOTP blended | 29.324 |
| 5yr DCF (conservative) | 35.000 |

| Method | Fair Value (VND) | Confidence |
|---|---|---|
| Peer P/E 13,6x | 31.648 | `[MOD]` |
| Munger 9x TTM EPS (FY2025) | ~20.800 | `[LOW]` |
| Munger 10x FY2026E EPS | ~33.200 | `[MOD]` |
| Damodaran SOTP | 29.324 | `[MOD]` |
| Damodaran DCF | 35.000 | `[LOW]` |
| Lynch PEGY | ~35.000 | `[HIGH]` |

Composite target: **~34.500 VND** | Hiện tại: 23.600 -> chiết khấu ~32%

> Note: Composite tăng nhẹ từ ~31.500 lên ~34.500 sau khi có Q1/2026 gốc và OCF dương.

---

## 6. Entry Trigger

- [ ] Giá < composite intrinsic (~34.500 VND)
- [ ] BCTC gốc integrity: EVALUATED (4/6)
- [ ] P/E < 13x peer average (hiện tại 9,3x)
- [ ] OCF dương + ổn định (đã xác nhận Q1/2026)
- [ ] Biên gộp >= 15% (đã đáp ứng 15,7%)
- [ ] Position size <= 10% equity portfolio

---

## 7. Scenarios

### Scenario 1: WAIT FOR BASE CASE
- **Trigger:** Nhận BCTC gốc -> chạy Integrity Gate -> có composite -> entry <= intrinsic.
- **Action:** Monitor Q2/2026 results (TCBS phân tích); nếu margin giữ 15%+ thì tiến cuộc.
- **Timeline:** 1-3 tháng

### Scenario 2: CATCH DOWNTURN
- **Trigger:** Giá về 19.000-21.000 do rủi ro thiếu đất/CRM hoặc chính sách.
- **Action:** Batch first check, giới hạn 10% portfolio.
- **Position:** Max 10% equity.

### Scenario 3: STRUCTURAL EXPANSION
- **Trigger:** DQ2 full ramp + CBPG ổn định + LNG/multiply segment tăng trưởng.
- **Action:** Reassess intrinsic up; mở dự phòng.
- **Probability:** Medium

---

## 8. Open Questions

- [x] BCTC gốc 2025/Q1/2026 đã có; Integrity Gate đã chạy (YELLOW).
- [ ] CBPG được kéo dài 5 năm? -> theo dõi WTO/FTA mới.
- [ ] DQ2 vận hành ổn -> sản lượng thực tế so với kế hoạch? -> kiểm tra báo cáo.
- [ ] Net debt/EBITDA giảm dưới 2x trong 2026E? -> theo dõi capex.
- [ ] HPA và BĐS KCN có tạo free cash flow giai đoạn thu hoạch?

---

## 9. Review Log

| Date | Note |
|---|---|
| 2026-06-20 | Bổ sung BCTC hợp nhất năm 2025 đã kiểm toán (Deloitte, 24/03/2026). BCTC gốc đã có; chuyển Integrity Gate từ PENDING sang EVALUATED. |
| 2026-06-21 | Fixed to tiếng Việt có dấu, bổ sung section/field chuẩn đầu vào. |
| 2026-06-20 | First ingest từ TCBS Research 15/06/2026. Dựa trên báo cáo phân tích, BCTC gốc chưa có. P/E 9,3x; Composite ~31.500 VND. Entry đang deferred. |
