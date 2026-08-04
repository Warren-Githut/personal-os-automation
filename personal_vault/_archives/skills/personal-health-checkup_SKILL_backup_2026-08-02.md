---
name: personal-health-checkup
description: "Plan Warren blood tests from vault; recency + vitals gate."
version: 1.0.0
author: Hermes
trigger: "Warren hỏi nên xét nghiệm gì / test máu chỉ số nào / đóng vai personal doctor."
category: personal-commands
tags: ['health', 'bloodwork', 'checkup', 'personal-doctor']
---

# Personal Health Checkup — lập / review toa xét nghiệm từ vault

> Mục đích: Từ data sức khỏe trong vault, đề xuất panel xét nghiệm máu CHÍNH XÁC, không bịa, KHÔNG lặp test vừa làm gần đây.

## Quy trình (bắt buộc, theo thứ tự)

1. **Đọc vault trước khi chẩn đoán** (index-first, search_files/browser không thay thế):
   - `10_PULSE/050_Health_Log.md` — lịch sử bloodwork (mới nhất ở trên top)
   - `10_PULSE/051_Sleep_Log.md` + `.csv` — sinh hiệu HÀNG NGÀY (BP, weight, HR)
   - `30_KNOWLEDGE_BASE/wiki/02_Health/aa_Bloodwork_Health_Baseline/` — baseline + biomarker interpretation
   - `.../ab_Doctor_Reports/` — phân tích bác sĩ prior (tần suất lặp)
   - `.../ac_Warren_Genetics_Report/GPro_Master_Health_Protocol.md` — tần suất xét nghiệm theo gen

2. **Xây dựng candidate list** từ: red flags trong baseline + gen flags + mục tiêu (targets trong baseline).

3. **🔴 RECENCY GATE** — với MỖI candidate, tra ngày làm gần nhất trong Health_Log:
   - Nếu nằm trong tần suất protocol → **BỎ**, ghi rõ "đã làm ngày X, lùi tới Y".
   - Tần suất chuẩn (từ GPro Protocol + doctor reports trong vault): xem `references/recency_rules.md`.

4. **🔴 VITALS CROSS-CHECK** — trước khi đề xuất đo BP / HR / mạch tại lab:
   - Check `051_Sleep_Log`: Bố track BP HÀNG NGÀY (systolic 95-99, diastolic 70-72, ổn định).
   - Nếu đã có data dày → **KHÔNG** đề xuất đo tại lab, ghi "đã track hàng ngày, đủ, không cần đo ở lab".

5. **Output** theo nhóm ưu tiên:
   - 🔴 Bắt buộc (core, lặp trend) | 🟡 Nên làm (follow-up / theo gen) | 🟢 Tùy chọn (chưa có data)
   - Mỗi dòng: chỉ số + lý do (cite vault) + ngày làm gần nhất (nếu có).

## Tone

- Khi Bố nói "vai trò bác sĩ tư / consultant 30 năm kinh nghiệm" → conclusion-first, thêm clinical judgment kiểu lão làng, vẫn Tiếng Việt có dấu, blunt khi cần.
- Luôn cite nguồn vault (Health_Log / doctor report / GPro).

## Pitfalls

- **Đừng re-recommend test gần đây.** Lần đầu con đề xuất hs-CRP + VitD + gan dù Bố mới làm 11/06 → Bố challenge. Luôn chạy Recency Gate (bước 3) trước khi đưa vào toa.
- **Đừng bịa giá lab.** Web search (Firecrawl) có thể hết credit (Payment Required); DIAG web (diag.vn) KHÔNG có catalog giá công khai (chỉ blog kiến thức); Google search bị CAPTCHA chặn bot. → Không đoán giá DIAG. Thay vào đó: (a) bảo Bố xem app DIAG / mục "Book Test" → giá hiện ngay; (b) gọi hotline 1900 1717; hoặc (c) đưa ước lượng thị trường VNĐ gắn tag [LOW] + ghi rõ "KHÔNG phải giá DIAG chính thức, chưa VAT/phí lấy mẫu".
- **Line-by-line khi tra giá / research:** Bố yêu cầu "search line by line" → trình bày từng bước search + từng khoản giá riêng lẻ, không gộp chung thành 1 tổng. Áp dụng mọi task ước lượng chi phí.
- **BP từ Sleep_Log là data thật:** WNK1 gen lệch Na/K nhưng thực tế BP Bố 95-99/70-72 rất đẹp → không scare, chỉ note tracking.

## References
- `references/recency_rules.md` — bảng tần suất chi tiết + cite exact, để nhanh tra mà không mở lại toàn bộ vault.
