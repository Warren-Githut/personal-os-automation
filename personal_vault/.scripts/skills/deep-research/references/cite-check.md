# Cite-Check Procedure (Bước 14.5 của deep-research)

> Áp dụng skill `verify-parser-output` làm gate. Mục tiêu: mọi `[N]` trong báo cáo phải
> được 1 source thật support. Không PASS = KHÔNG write vault.

## Nguyên tắc (từ hyperresearch, adapt cho Hermes)
1. **Citation-sentence binding:** mỗi câu có `[N]` phải được source `[N]` thực sự support.
2. **Skeptical spot-check:** lấy mẫu 30% các `[N]` → đọc lại source gốc → xác nhận quote
   nguyên văn hoặc ý đúng.
3. **Retraction block:** nếu source bị rút lại (retracted) → báo cáo phải note hoặc drop claim.
4. **No fabrication:** quote bịa / source không tồn tại = hard block (báo Bố, không ship).

## Quy trình (dùng verify-parser-output)
1. Load: `skill_view(name='verify-parser-output')`.
2. Đọc `report v3` (hoặc `final.md`): liệt kê mọi `[N]` + câu chứa nó.
3. Với mỗi `[N]`:
   - Tìm source link tương ứng trong `raw/` hoặc digest.
   - `web_extract` hoặc đọc lại file raw → confirm có đoạn support claim đó.
   - Nếu không → đánh dấu `[N] UNVERIFIED`.
4. Chạy independent recompute (cross-assert): số `[N]` claimed = số `[N]` verified.
5. Viết `cite-report.md`:
   - Tổng số `[N]`: X
   - Verified: Y
   - Unverified: Z (list cụ thể)
   - Kết luận: PASS (Z=0) / BLOCK (Z>0)

## Kill criterion
- Z > 0 (có claim không verify được) → **BLOCK**. Con báo Bố, sửa hoặc drop claim,
  rồi re-run gate. KHÔNG bao giờ write vault khi chưa PASS.

## Ví dụ (format cite-report)
```
Cite-check cho: ai-impact-fnb-vn
Tổng [N]: 12
Verified: 12
Unverified: 0
Kết luận: PASS ✅
→ Được write vault/_inbox/research/ai-impact-fnb-vn.md
```
