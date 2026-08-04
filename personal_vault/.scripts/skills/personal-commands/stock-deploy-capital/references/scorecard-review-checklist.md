# Scorecard Review Checklist — QA output stock-deploy-capital (PASS/FAIL)

> Khi nào: "Review output stock-deploy-capital [TICKER]" / "PASS hoặc FAIL + list lỗi theo 5 trục + 3 cách conclusion sai". KHÔNG sửa output — chỉ flag.

## Flow

1. Load SSOT trước: SKILL.md + `references/scoring-calibration.md` + `references/management-quality-checklist.md` + `references/peer-mapping.md`.
2. Tìm vault: `$HOME/Documents/Stock_OS/stock_vault/30_KNOWLEDGE_BASE/wiki/03_Investing/VN_Equities/030-Companies/*{TICKER}*/` — đọc Thesis.md (frontmatter `integrity_score`), Anti-thesis.md (status thắng/thua), `BCTC - Rolling.md` (quý mới nhất), Catalyst-watch.md.
3. Recompute từng sub-score theo calibration; verify số học tổng.
4. Check action cards tự nhất quán (stop vs dữ kiện đã công bố; entry vs giá hiện tại).
5. Emit: PASS/FAIL + lỗi 5 trục + 3 cách conclusion sai.

## 5 trục

| Trục | Check |
|---|---|
| SỐ LIỆU | Mỗi sub-score traceable tới calibration; mọi số cross-check vault; không ngưỡng tự đặt; [LIMITED] khi thiếu data; đơn vị nhất quán |
| FORMAT | Tag [HIGH]/[MOD]/[LOW] trên MỌI số (anchor A3); breakdown sub-score từng nhóm; "5 năm" phải 5 mốc |
| LOGIC | Verdict vs stop/exit đã breach; entry < giá hiện tại; catalyst độc lập; anti-thesis status; dự phòng ≥30% LNST TTM = không thể Integrity full |
| CONSISTENCY | Anchors A1-A8; checklist SSOT không trộn legacy; score output vs Thesis integrity_score; position vs Holdings |
| COMPLETENESS | 5A-5E đủ (5D peer 2VN+2SEA, 5E stress test ngành — vàng BẮT BUỘC); normalized earnings; forward/guidance; sensitivity/kịch bản; pre-flight |

## Adversarial — 3 cách conclusion sai (khuôn mẫu)

1. **Trái luật chơi:** stop/exit đã breach theo dữ kiện ĐÃ công bố (vd: stop "mua lại >100%" nhưng tháng trước 237%) → verdict đúng phải TRÁNH, không CHỜ.
2. **Điểm sai nền:** sub-score trái SSOT (vd: OCF/NI 168% → 0/7 theo divergence) → chất lượng thực khác → có thể rơi khỏi góc "CHẤT LƯỢNG CAO" → verdict đổi.
3. **Valuation ảo:** earnings chứa one-off dự phòng chưa normalized; growth ex-dự phòng "không bền vững" [MOD] dùng làm PEG → PEGY/MOS đổi → trigger fail → "rẻ" là value trap.

## Worked example: PNJ 2026-08-01 (flags thật — FAIL)

- Integrity 20/20 sai: OCF/NI 168% = divergence 68% → 0/7 (SSOT); 2024: 3,9%, 2025: 0,7%; OCF 1.990 tỷ gồm add-back dự phòng 1.228 tỷ; vault `integrity_score: 7/11`.
- "Receivables giảm" sai: phải thu 97 → 193 tỷ Q2/2026 (+99%).
- "OCF dương 5 năm" chỉ 3 mốc (2024/2025/6T) → thiếu 2021-2023 → [LIMITED].
- Mgmt 6/8 trộn legacy (cổ tức 5 năm, anti-thesis trigger, control nội bộ) — SSOT 8 tiêu chí khác.
- Stop "mua lại T8-9 >100%" đã breach (T7 = 237%) mà verdict CHỜ → mâu thuẫn luật chơi.
- Entry 1 "≤36.000 (MOS 30%)" trong khi giá 31.000 → entry vô nghĩa; MOS 30% @36.000 không khớp IV 45-57k (thực 20-37%).
- A3: 0 tag → FAIL; thiếu 5D peer, stress test vàng (bắt buộc), forward P/E 6,3-7,2x (có sẵn trong Thesis), sensitivity 20/45/35, normalized earnings.
- Portfolio 2.300 cp @ 47.018 vs Thesis review log 1.700 cp @ 50.400 → lệch cần giải thích.
- Số học tổng đúng (85 = 20+20+20+5+6+7+7+0) nhưng nền sub-score sai → điểm thực ~78, không SSOT-traceable.

## Pitfall chính

Đừng tự tin vào output vì tổng số học đúng — lỗi nằm ở sub-score rationale và self-consistency của action card, không nằm ở phép cộng.

## Vòng 2+ verification (re-review fixes) — bài học PNJ 2026-08-01 vòng 2

Khi verify "đã fix N mục": verify NỘI DUNG THỰC của output, KHÔNG tin narrative fix (round-2 vẫn tái phạm lỗi round-1 dù fix-log ghi đã sửa). Các kỹ thuật bắt lỗi đã chứng minh:

1. **Legacy-mix regression:** fix-log nói "6/8 theo SSOT checklist" nhưng output thực tế vẫn liệt kê "cổ tức 5y ✓, anti-thesis trigger ✓" (legacy) vào tally và bỏ sót ownership structure / patience / one-line quality test. Cách bắt: so TỪNG item trong breakdown với 8 tiêu chí `management-quality-checklist.md` — đếm SSOT items, đừng đếm tổng số ✓ (số ✓ = 8 nhưng item set sai vẫn FAIL).
2. **Entry vs exit line overlap:** Entry 3 ≤25.000 trùng exit "giá <25.000" — cùng mức giá vừa mua vừa bán. Check: entry levels KHÔNG được cắt exit line; entry zone phải khớp Entry Trigger trong Thesis (vd thesis 28-30k vs action card ≤36k = lệch).
3. **CAGR/5-mốc mâu thuẫn cross-entry:** "CAGR>5% [LIMITED]" full 5 vs entry CŨ hơn trong vault ("Revenue CAGR ~3%") — luôn đối chiếu claim với entry cũ; thiếu 5 mốc (2021-22) → đòi cite hoặc hạ nửa điểm.
4. **Untraceable numbers:** "phải thu KH 48,8 tỷ cuối 2025", "trả trước NB 113 tỷ" không có trong BCTC Rolling (chỉ tổng phải thu NH 97 tỷ) → flag traceability + yêu cầu cite, đừng chấp nhận vì "hợp lý".
5. **EBITDA/EV recompute:** EBITDA TTM = LN HĐKD TTM + khấu hao TTM; TTM = năm − 6T cũ + 6T mới (PNJ: 3.520−1.398+1.518 = 3.640; D&A 85−44+38 = 79 → 3.719 ✓ khớp output). Cross-assert EBITDA ≥ EBIT + D&A trước khi chấm trigger EV/EBITDA.
6. **Dual-IV MOS:** MOS headline theo calibration (5Y avg P/E × EPS TTM, [LOW]) có thể ≠ MOS thực theo Thesis IV (45-57k → 31-46% vs 52%) — flag trình bày 2 IV song song dễ đọc nhầm "rẻ hơn thực tế"; tính cả 2 và yêu cầu chú thích.
7. **Điểm sai 2 chiều:** calibration bug (OCF >> NI bị phạt 3,5/7 dù là dấu hiệu TỐT, đã đề xuất patch) → điểm có thể UNDERSTATE. Review phải check cả hướng "điểm cao hơn thực" lẫn "điểm thấp hơn thực", không chỉ tìm lỗi hạ điểm.

### Adversarial #4 — Gộp 2 quyết định vào 1 verdict
CHỜ đúng cho TIỀN MỚI (cổng scandal đóng = không mua) nhưng câu trả lời cho VỊ THẾ CŨ (đang giữ, lỗ -34%, anti-thesis "đang THẮNG") có thể là TRÁNH/exit — gộp làm 1 verdict "CHỜ" gây đọc nhầm. Flag: verdict phải phân tách "mua mới" vs "giữ/thoát vị thế cũ", đặc biệt khi Holdings.md có position đang lỗ sâu và file Anti-thesis.md ghi kết luận bất lợi.
