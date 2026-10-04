# Quality Pipeline Gotchas (Warren 2026-07-26)

Thực tế chạy chuỗi `improve-codebase-architecture → ab-test + debugging → code-simplification → simplify-code → code-review-and-quality` trên skill `weekly-lto-sql` (đo promo B+C từ SQL IKKO). Bài học cụ thể đúc kết lại:

## 1. Delegation split (S1)
`delegate_task(tasks=[N goals])` với nội dung >~8K tokens/gọi → **stream timeout, không deliver**.
FIX: dispatch **N call lẻ** (mỗi agent 1 `delegate_task`), chạy song song nền tự nhiên. Con vẫn tổng hợp findings sau.

## 2. Markdown table delimiter BẮT BUỘC (legibility)
BỐT correction: *"bị lỗi syntax |||, ko có bảng trong obsidian"*.
Nguyên nhân: `build_promo_block` sinh `| Metric | Promo Wk |... |` header NHƯNG **THIẾU dòng `| --- | --- | --- | --- | --- |`** → Obsidian không render → hiện raw `|||`.
FIX: **mọi bảng markdown sinh bằng code PHẢI có dòng delimiter ngay sau header.**
Áp dụng: parser logs, dashboard tables, bất kỳ programmatic markdown table nào.

## 3. Registry extensibility — đừng claim "1 dòng" nếu chưa test
Claim "thêm promo D = 1 dòng vào registry" là **SAI**: parser hardcode title
(`if store=='LU5' else 'C. MORNING KICKSTART...'`) + `verify_lto_gate` hardcode check string B/C.
Thêm D (store khác) → rơi vào nhánh `else` → nhận nhầm title "C. MORNING KICKSTART — LU7".
FIX: put **ALL presentation strings (prefix, title) vào registry**, parser nhận param từ caller.
`verify_gate` loop registry thay vì hardcode. **SAU ĐÓ test thêm promo D thật** mới được claim "1 dòng".

## 4. TDD fixture phải mirror thực tế (SQL parser)
Unit fixture dễ CHE 2 bug chỉ lộ ở E2E thật:
- quên `/1e6` VND→M (net hiển thị `21004576.7` thay `21.0M`)
- baseline gộp N tuần=1 số (`361` thay `90.2`/tuần)
FIX: fixture `net` đã ở M, baseline = 1 elem/tuần. **LUÔN E2E dry thực tế trước khi báo xong.**
(Xem WARREN_MEMORY §SQL PARSER PITFALLS P1/P2 cho Double NET_FACTOR — `×0.882` chỉ 1 lần.)

## 5. Year-hardcoded regex trong time-series tracker (CRITICAL, tái diễn — 2026-07-27 google-review-cron)
**Pattern:** Parser regex bắt week-header `^##\s+(?P<week>2026-W\d{2})\s*\|` (hardcode năm)
→ 2027+ trả 0 entries = **mất toàn bộ data năm mới**, im lặng.

**Fix PHẢI 2 phần (sửa 1 phần = chưa đủ):**
1. Regex → `\d{4}-W\d{2}`.
2. Downstream sort/label: nếu key = week-number alone (`int(week.split("-W")[1])`)
   → cross-year MIS-SORT (2027-W05 trước 2026-W52) + label trùng (`W05` 2 lần).
   Fix: sort tuple `(year, week)`; label `"W05 '27"` khi ≥2 năm, giữ `"Wxx"` single-year (zero regression).

**Lesson:** reviewer-node (independent critic) bắt được phần 2 SAU KHI phần 1 đã qua TDD 11/11.
→ Luôn thêm **cross-year fixture test** khi sửa time-series parser, KHÔNG chỉ test năm hiện tại.
Áp dụng MỌI tracker `Wxx` L'Usine (revenue, hourly, COL, reviews, LTO).
**Verify:** ab-test Before(0)/After(1) cho synthetic `2027-W05`; TDD assert
`["W52 '26","W01 '27","W05 '27"]` order + single-year giữ `"Wxx"`.
