# Management Quality & Ownership Checklist (SSOT)

> **SSOT duy nhất** cho qualitative gate về quản trị + cấu trúc sở hữu + capital allocation.
> Nguồn gốc: framework NoLimit (@NoLimitGains, 2026-08-01) — chắt lọc theo chuẩn Buffett-Munger đang dùng.
> Các skill tham chiếu file này: `stock-deploy-capital` (scoring), `stock-ingest` (Integrity Gate), `stock-deep-research` (atomic items).
> **KHÔNG copy nội dung sang skill khác** — sửa ở đây, mọi nơi khác tự cập nhật.

## Cách dùng

Mỗi tiêu chí = **PASS/FAIL binary** (không nửa vời — cùng chuẩn Integrity Gate). 1 sub-criteria fail → cả tiêu chí FAIL.
Dữ liệu lấy từ: BCTC (note RPT, cash flow, phát hành/buyback), báo cáo thường niên (biên bản ĐHĐCĐ, thù lao HĐQT), báo cáo sở hữu (Vietstock/CafeF), tin tức. Tag confidence theo chuẩn SOUL: `[HIGH]` / `[MOD]` / `[LOW]`.

---

## 9. Insider Actual Buy (Bonus Signal — KHÔNG binary, cộng điểm)

> **SSOT data:** `030-Companies/100_Compliance/Internal_Dealing.md`
> **Quy tắc cứng:** CHỈ tính THỰC MUA (actual settled) ≥100 tỷ. Đăng ký KHÔNG tính.
> Ví dụ: TGD ĐK mua 100 tỷ (01/08→31/08), hết window chỉ mua 50 tỷ vì "giá không thích hợp" → ❌ KHÔNG đạt.

| Trạng thái | Điểm cộng vào stock-deploy-capital check #7 (trọng số 10) |
|------------|-----------------------------------------------------------|
| THỰC MUA ≥100 tỷ (Meets=✅) | **+2/10** (tín hiệu bull mạnh từ người trong cuộc) |
| THỰC MUA <100 tỷ hoặc Partial/Cancelled (Meets=❌) | 0 |
| Chưa có event / chưa báo cáo | 0 (KHÔNG penalize, chỉ không cộng) |

- Cập nhật: mỗi khi Bố báo insider event → ghi block vào `Internal_Dealing.md` (actual-only).
- Cross-ref: `stock-deploy-capital` check #7 đọc Meets từ SSOT này khi chấm điểm /100.
- Source tag: `[HIGH]` CBTT / `[MOD]` báo chí.

---

## 8 Tiêu Chí

### 1. Capital Allocation — Tiền đi đâu? (dữ liệu: BCTC cash flow + tin phát hành/buyback)

| Check | PASS khi | FAIL khi |
|-------|----------|----------|
| Buyback timing | Mua lại CP khi giá rẻ (P/B thấp, PE thấp) hoặc không buyback | Buyback lúc đỉnh cao + đồng thời phát hành thêm CP để mua bán sáp nhập |
| Bolt-on vs empire | M&A nhỏ, hợp lý, cùng ngành, tạo synergies rõ | M&A lớn, khác ngành, "đế chế" (empire building), trả giá quá cao |
| Vốn hóa lãi vay | Lãi vay ghi nhận chi phí bình thường | Vốn hóa lãi vay vào tài sản dở dang (che giấu chi phí thật) |

### 2. Insider Ownership — Sở hữu thật của người trong cuộc

| Check | PASS khi | FAIL khi |
|-------|----------|----------|
| Ownership thật | Founder/management nắm cổ phần đáng kể từ tiền của họ (≥5-10% [MOD theo ngành]) | Nắm chủ yếu qua cổ phiếu được cấp (granted/ESOP), bán ra liên tục |
| Hành vi | Mua thêm khi giá rẻ, giữ lâu, nhận lương hợp lý | Bán liên tục, cầm cố cổ phần, nhận thù lao khủng khi công ty làm ăn kém |
| Alignment | Quyền lợi họ gắn với cổ đông thiểu số | Giao dịch nội bộ có lợi cho nhóm lớn, thiểu số bị bỏ rơi |

### 3. Ownership Structure — Ai nắm cổ phần?

| Check | PASS khi | FAIL khi |
|-------|----------|----------|
| Institutional | Có tổ chức lớn nắm giữ đáng kể (funds, foreign room) | Chủ yếu retail, "hype" mạnh trên MXH |
| Short interest | Short interest thấp + institutional sponsorship tốt | Short interest cao + sponsorship yếu (shorts thường được thông tin tốt hơn) |
| Cơ cấu minh bạch | Cổ đông lớn rõ ràng, không ẩn danh | Cơ cấu tầng lớp (pyramid), cổ đông lớn ẩn danh |

### 4. Valuation vs Normalized Earnings — Định giá trên lợi nhuận CHUẨN HÓA

| Check | PASS khi | FAIL khi |
|-------|----------|----------|
| Normalized earnings | Dùng earnings trung bình chu kỳ (5Y avg / mid-cycle), KHÔNG peak | Dùng earnings đỉnh chu kỳ (peak cycle) để kể chuyện "rẻ" |
| FCF yield | FCF yield ≥ 5-6% [MOD theo ngành] | FCF âm hoặc yield thấp mà PE vẫn đắt |
| EV/EBIT | EV/EBIT hợp lý vs ngành + lịch sử | EV/EBIT cao bất thường |
| Reverse DCF | Tăng trưởng ẩn trong giá < khả năng thực hiện | Growth priced-in vượt xa khả năng (đã "priced in" quá đà) |

### 5. Moat & Customer Concentration — Hào + ai mua hàng?

| Check | PASS khi | FAIL khi |
|-------|----------|----------|
| Pricing power | Tăng giá không mất khách (test qua biên gộp ổn định khi tăng giá) | Tăng giá → mất khách ngay (biên gộp co) |
| Switching cost / network | Khách đổi vendor tốn kém / network effects rõ | Hàng hóa dễ thay thế hoàn toàn |
| Customer concentration | Khách lớn nhất < 15-20% doanh thu, top 2 khách < 30% | 2 khách = ≥30% doanh thu → 1 cuộc gọi phá thesis |

### 6. Management Compensation — Họ được trả thế nào?

| Check | PASS khi | FAIL khi |
|-------|----------|----------|
| Cấu trúc trả lương | Equity dài hạn (multi-year vesting) > bonus tiền mặt theo EPS quý | Bonus tiền mặt ngắn hạn theo EPS quý là chủ đạo |
| Tenure | Team sống sót qua ≥1 chu kỳ đầy đủ (cả bull lẫn bear) | Team chỉ thấy bull market, chưa qua bear |
| Thù lao hợp lý | Thù lao tương xứng kết quả | Lương thưởng khủng khi KQKD đi xuống |

### 7. Patience Discipline — Ngồi yên (dành cho Hermes khi tư vấn)

| Check | PASS khi | FAIL khi |
|-------|----------|----------|
| Buy-the-fear | Đề xuất mua khi người ta sợ 1 business tốt | Đuổi theo khi crowd đang hét (edge đã hết) |
| Hold discipline | Thesis còn nguyên → giữ, bỏ qua noise | Bán vì sợ hãi / mua vì FOMO ngắn hạn |
| "Do nothing" | Không có gì để làm = không làm gì, KHÔNG ép trade | Cảm thấy phải làm gì đó mỗi ngày |

### 8. One-Line Quality Test (tổng hợp)

> PASS khi đủ: **Quality business, high returns on capital, clean balance sheet, sensible valuation, trading near the long-term trend.**
> FAIL khi thiếu 1 trong 5. Boring = đúng; exciting = nghi ngờ.

---

## Verdict Template

```
MANAGEMENT QUALITY: PASS X/8 — [tiêu chí fail]
[2-3 dòng bằng chứng ngắn, có tag confidence]
```

## Lưu ý khi dùng với VN market

- **Insider ownership VN:** nhiều công ty gia đình nắm >50% — điều này TỐT cho alignment nhưng cần check giao dịch nội bộ + RPT (VN đặc thù: RPT với công ty gia đình là rủi ro chính).
- **Institutional VN:** foreign room + khối ngoại là proxy institutional chính. Retail-heavy là đặc thù VN — dùng làm red flag nhẹ, không hard FAIL.
- **Normalized earnings VN:** nhiều công ty cyclical (thép, BĐS, dầu khí) → bắt buộc dùng 5Y avg, cấm peak-year EPS (đúng bài học NVL/HPG).
- **FCF yield VN:** ngân hàng dùng PPOP proxy (như Integrity Gate adaptation); BĐS distressed dùng SOTP/NAV thay FCF.
