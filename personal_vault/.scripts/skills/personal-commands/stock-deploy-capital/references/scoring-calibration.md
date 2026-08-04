# Scoring Calibration — stock-deploy-capital

## Moat (20 điểm)

| Sub-chỉ số | Full điểm | 1 nửa | 0 |
|---|---|---|---|
| ROE ≥15% 4/5 năm | 8 | 4/5 có ROE ≥10% | <4/5 năm |
| Gross margin stable ±5% | 7 | Biến động 5-10% | >10% |
| Top 3 thị phần | 5 | Top 5 | Ngoài top 5 |

## Survival (20 điểm)

| Sub-chỉ số | Full điểm | 1 nửa | 0 |
|---|---|---|---|
| D/E <1 | 8 | D/E 1-2 | >2 |
| Interest coverage >5x | 7 | 3-5x | <3x |
| OCF dương 5 năm liên tiếp | 5 | 4/5 năm | <4/5 năm |

## Integrity gate (20 điểm)

| Sub-chỉ số | Full điểm | 1 nửa | 0 |
|---|---|---|---|
| OCF/NI ≥70% (jewelry ≥30%) — divergence CHỈ tính chiều NI vượt OCF; OCF >> NI (≥100%) = PASS (kế toán bảo thủ; fix 25/06/2026 theo stock-ingest) | 7 | OCF/NI 50-70% (jewelry 30-50%) | OCF/NI <50% (jewelry <30%) |
| Receivables ≤ revenue growth | 6 | Chênh <10% | >10% |
| Goodwill <30% equity | 4 | 30-50% | >50% |
| RPT sạch | 3 | Có RPT nhưng nhỏ | RPT lớn/đáng ngờ |

> ⚠️ Diễn giải OCF/NI (lỗi thật PNJ 2026-08-01): mọi chênh lệch so với 1:1 đều tính divergence = |OCF−NI|/NI — OCF/NI 168% = divergence 68% → **0đ**, KHÔNG pass vì "OCF cao hơn NI". Cấm tự đặt ngưỡng ngành mới (vd "jewelry ≥30%") khi chưa patch file này. Loại trừ add-back không bằng tiền (trích lập dự phòng) khỏi OCF trước khi đánh giá. Check TỪNG NĂM, không chỉ kỳ mới nhất (PNJ 2024: 3,9%, 2025: 0,7% → Integrity không thể full dù 6T/2026 đạt 168%).

## Predictability (10 điểm)

| Sub-chỉ số | Full điểm | 1 nửa | 0 |
|---|---|---|---|
| Revenue CAGR >5% 5Y | 5 | CAGR 0-5% | Âm |
| Không scandal/restatement | 3 | Restatement nhỏ >3 năm trước | Có scandal |
| EPS ổn định | 2 | EPS biến động <30% | >30% |

## Vĩ mô & ngành (8 điểm)

| Sub-chỉ số | Full điểm | 1 nửa | 0 |
|---|---|---|---|
| Ngành uptrend/neutral | 3 | Neutral nhưng rủi ro | Downtrend rõ |
| Lãi suất thuận lợi | 3 | Neutral | Bất lợi |
| Không chính sách bất lợi đang chờ | 2 | Có dự thảo nhưng chưa chốt | Có chính sách bất lợi đã ban hành |

## Catalyst (10 điểm)

| Sub-chỉ số | Full điểm | 1 nửa | 0 |
|---|---|---|---|
| ≥2 driver cụ thể | 5 | 1 driver | 0 driver |
| Timeline <6 tháng | 3 | 6-12 tháng | >12 tháng |
| Không phụ thuộc 1 yếu tố | 2 | 2 yếu tố | 1 yếu tố duy nhất |

## Management, Ownership & Capital Allocation + Anti-thesis (10 điểm)

> **Scheme mới (2026-08-01):** chi tiết 8 tiêu chí PASS/FAIL tại `references/management-quality-checklist.md` (SSOT — capital allocation, insider ownership, institutional vs retail, normalized earnings, customer concentration, compensation, tenure, patience). Điểm = số tiêu chí PASS / 8 × 10. Legacy breakdown bên dưới chỉ còn giá trị tham khảo — xem note phía sau.

| Sub-chỉ số | Full điểm | 1 nửa | 0 |
|---|---|---|---|
| Cổ tức 5 năm liên tiếp | 4 | 3-4/5 năm | <3/5 năm |
| Anti-thesis có trigger cụ thể + con số | 4 | Có trigger nhưng mơ hồ | Không có anti-thesis |
| RPT sạch | 2 | Có RPT nhỏ | RPT lớn |

> ⚠️ Legacy note: breakdown cũ (cổ tức/anti-thesis/RPT) chỉ áp dụng như 3 tiêu chí phụ của checklist mới — 5 tiêu chí còn lại (capital allocation, insider, institutional, customer concentration, compensation/tenure) tính theo `management-quality-checklist.md`. Điểm cuối = max(scheme cũ, PASS/8 × 10) hoặc thuần PASS/8 × 10 khi đủ data — ưu tiên checklist mới khi có dữ liệu.

## State backing (2 điểm)

| Sub-chỉ số | Full điểm | 1 nửa | 0 |
|---|---|---|---|
| State >50% HOẶC ngành chiến lược | 2 | State 25-50% | State <25% và không chiến lược |

## Valuation trigger (PASS/FAIL — không tính điểm)

| Trigger | PASS | FAIL |
|---|---|---|
| P/E vs 5Y avg (trên NORMALIZED EPS — 5Y avg / ex-one-off) | < 0.8x | ≥ 0.8x |
| MOS (P/E 5Y avg × NORMALIZED EPS) | >10% | ≤10% |
| P/B vs ROE | P/B ≤ ROE × 0.1 | P/B > ROE × 0.1 |
| EV/EBITDA vs sector | < median | ≥ median |

- 4/4 PASS = ✅\n- 3/4 PASS = ⚠️ (nếu P/B fail là FAIL duy nhất → vẫn ✅ — xem edge case bên dưới)\n- ≤2/4 PASS = 🛑

> **Normalized EPS (bắt buộc từ 2026-08-01 — Tầng 2 ops-architect / Buffett lens):** Trigger #1 + MOS dùng earnings CHUẨN HÓA (5Y avg / mid-cycle / ex-one-off), KHÔNG dùng TTM EPS thô khi có one-off trọng yếu (vd: dự phòng 865,5 tỷ PNJ Q2/2026; thoái vốn NVL). Áp dụng cả 2 chiều: peak-cycle (bài học semis) lẫn one-off hạ earnings đều làm méo P/E. **FCF yield + EV/EBIT = data point hiển thị trong breakdown, KHÔNG phải hard trigger** — tránh tự chặn doanh nghiệp working-capital-heavy (bán lẻ: PNJ FCF âm 2024-2025) vốn là deal tốt ở giá hợp lý.

## Edge cases

- **Bán lẻ trang sức (jewelry — PNJ/DOJ/SJI):** OCF/NI structural thấp do inventory-heavy (vàng chiếm 70-80% tài sản) → ngưỡng Integrity giảm còn ≥30% (theo `stock-ingest` jewelry-retail-financial-analysis). OCF >> NI (≥100%) = tín hiệu TỐT (kế toán bảo thủ), KHÔNG tính là divergence xấu.
- **Ngân hàng:** Dùng P/B thay P/E. ROE benchmark 12% (không 15%). D/E không áp dụng — dùng LDR thay thế (<85% = PASS).
- **Công nghệ / Asset-light (ROE >25%, hữu hình thấp):** P/B tự nhiên cao do tài sản vô hình (nhân lực, IP, quan hệ khách hàng) không ghi nhận trên BCTC. P/B > ROE × 0.1 không phải red flag — gắn ⚠️ thay vì ❌. Giải thích trong output.
- **Không có 5Y data:** Ghi rõ "[LIMITED]" trong output. Điểm nhóm đó dựa trên dữ liệu có sẵn.
- **Không có BCTC:** SKIP hoàn toàn. Không chấm.
- **Ticker có BCTC cũ (>6 tháng):** Cảnh báo "BCTC cũ — cần cập nhật." Vẫn chạy nhưng gắn cờ.