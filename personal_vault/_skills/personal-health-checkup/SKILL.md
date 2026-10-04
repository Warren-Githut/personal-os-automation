---
name: personal-health-checkup
description: "Plan Warren blood tests from vault; recency + vitals gate."
version: 2.2.0
author: Hermes
trigger: "Warren hỏi nên xét nghiệm gì / test máu chỉ số nào / đóng vai personal doctor."
category: personal-commands
tags: ['health', 'bloodwork', 'checkup', 'personal-doctor']
related_skills: []
---

# Personal Health Checkup — lập / review toa xét nghiệm từ vault

> Mục đích: Từ data sức khỏe trong vault, đề xuất panel xét nghiệm máu CHÍNH XÁC, không bịa, KHÔNG lặp test vừa làm.
> Phiên bản 2.2: Thêm READ & CONFIRM GATE — con phải gửi read receipt cho Bố trước khi advise.

---

## 🔴 HARD GATE — BẮT BUỘC ĐỌC TRƯỚC KHI ADVISE

> **Quy tắc cứng:** Khi Bố yêu cầu tư vấn sức khỏe / personal doctor / đọc xét nghiệm → BẮT BUỘC đọc ĐỦ 4 file genetics dưới đây TRƯỚC KHI viết bất kỳ lời khuyên nào. Không đọc = không advise.

### 4 file BẮT BUỘC đọc (theo thứ tự):

| # | File | Vai trò | Bỏ qua = lỗi |
|---|------|---------|-------------|
| 1 | `30_KNOWLEDGE_BASE/wiki/02_Health/ac_Warren_Genetics_Report/GPro_Index.md` | Entry point — biết có file gì, Five Core Facts | ❌ |
| 2 | `30_KNOWLEDGE_BASE/wiki/02_Health/ac_Warren_Genetics_Report/GPro_Genetic_Database.md` | Source of truth — 60 modules / 84 genes | ❌ |
| 3 | `30_KNOWLEDGE_BASE/wiki/02_Health/ac_Warren_Genetics_Report/GPro_Master_Health_Protocol.md` | Protocols + tần suất xét nghiệm theo gen | ❌ |
| 4 | `30_KNOWLEDGE_BASE/wiki/02_Health/ac_Warren_Genetics_Report/GPro_Strengths_Map.md` | Strengths + behavioral + learning profile | ❌ |

> **Tại sao phải đủ 4 file:** Mỗi file chứa 1 lớp thông tin khác nhau. Index = map, Database = raw data, Protocol = hành động, Strengths = behavioral context. Thiếu 1 = advise thiếu chiều, có thể sai.

---

## 🟢 READ & CONFIRM GATE — GỬI BỐ TRƯỚC KHI ADVISE

> **Quy tắc:** Sau khi đọc đủ 4 file genetics, con BẮT BUỘC phải gửi một "read confirmation" cho Bố. Chỉ khi Bố xác nhận đã thấy read confirmation, con mới được phép phân tích/advise.

### Read Confirmation format:
```
📋 READ CONFIRMATION — Genetics Files Loaded

[1] GPro_Index.md         — ✅ ĐỌC XONG (N dòng) | Key: [1 fact nổi bật]
[2] GPro_Genetic_Database.md — ✅ ĐỌC XONG (N dòng) | Key: [1 fact nổi bật]
[3] GPro_Master_Health_Protocol.md — ✅ ĐỌC XONG (N dòng) | Key: [1 fact nổi bật]
[4] GPro_Strengths_Map.md — ✅ ĐỌC XONG (N dòng) | Key: [1 fact nổi bật]

→ Đủ data. Sẵn sàng advise khi Bố yêu cầu.
```

### Quy tắc:
- **Mỗi dòng phải có số dòng thực tế** (đếm bằng tool, không đoán)
- **Key fact phải là 1 chiếc thông tin cụ thể** từ file đó (không copy nguyên đoạn, phải tóm tắt 1 dòng)
- **Gửi read confirmation TRƯỚC KHI advise** — nếu con viết advice mà chưa gửi read confirmation = vi phạm
- **Bố không cần reply OK** — chỉ cần thấy read confirmation là con được phép advise tiếp. Nếu Bố thấy số dòng sai hoặc key fact sai → Bố challenge.

---

## Quy trình (bắt buộc, theo thứ tự)

### Bước 1: Đọc vault trước khi chẩn đoán

**File cần đọc (index-first):**
- `10_PULSE/050_Bloodwork_Update.md` — lịch sử bloodwork (mới nhất ở trên top)
- `10_PULSE/051_Sleep_Log.md` + `.csv` — sinh hiệu HÀNG NGÀY (BP, weight, HR)
- `30_KNOWLEDGE_BASE/wiki/02_Health/aa_Bloodwork_Health_Baseline/` — baseline + biomarker interpretation
- `.../ab_Doctor_Reports/` — phân tích bác sĩ prior (tần suất lặp)
- **4 file genetics (xem HARD GATE bên trên)** — bắt buộc

### Bước 2: Gửi Read Confirmation

Sau khi đọc đủ 4 file genetics → gửi read confirmation cho Bố (xem format ở trên). **KHÔNG được advise trước khi gửi.**

### Bước 3: PDF PARSE + DEDUP + TÍNH TOÁN

Khi Bố gửi PDF DIAG:
- Parse toàn bộ field kết quả từ PDF.
- **Dedup theo mã hồ sơ:** Field "Mã hồ sơ" trong PDF DIAG = unique identifier. Cùng mã = trùng → xoá bản trùng, ghi rõ tên file đã xoá.
- **Tính LDL Friedewald** khi lab không cấp LDL trực tiếp: `LDL = Cholesterol Total - HDL - (Triglycerides / 2.2)` với mmol/L. Ghi rõ công thức đã dùng (xem `references/friedewald_calc.md`).
- So sánh số mới nhất với baseline để xác định trend (↑/↓/→).

### Bước 4: Xây dựng candidate list

Từ: red flags trong baseline + gen flags + mục tiêu (targets trong baseline).

### Bước 5: 🔴 RECENCY GATE

Với MỖI candidate, tra ngày làm gần nhất trong Bloodwork_Update:
- Nếu nằm trong tần suất protocol → **BỎ**, ghi rõ "đã làm ngày X, lùi tới Y".
- Tần suất chuẩn (từ GPro Protocol + doctor reports trong vault): xem `references/recency_rules.md`.

### Bước 6: 🔴 VITALS CROSS-CHECK

Trước khi đề xuất đo BP / HR / mạch tại lab:
- Check `051_Sleep_Log`: Bố track BP HÀNG NGÀY (systolic 95-99, diastolic 70-72, ổn định).
- Nếu đã có data dày → **KHÔNG** đề xuất đo tại lab, ghi "đã track hàng ngày, đủ, không cần đo ở lab".

### Bước 7: Output theo nhóm ưu tiên

- 🔴 Bắt buộc (core, lặp trend) | 🟡 Nên làm (follow-up / theo gen) | 🟢 Tùy chọn (chưa có data)
- Mỗi dòng: chỉ số + lý do (cite vault) + ngày làm gần nhất (nếu có).
- **Bảng Genotype ↔ Phenotype cross-reference** (bắt buộc): Gene | Genotype | Phenotype hiện tại | Đúng gen? | Hành động.
- Nếu Bố yêu cầu dashboard → tạo HTML/Chart.js với traffic-light colors, target lines, tab filter (xem `references/dashboard_format.md`).

---

## Tone

- Khi Bố nói "vai trò bác sĩ tư / consultant 30 năm kinh nghiệm" → conclusion-first, thêm clinical judgment kiểu lão làng, vẫn Tiếng Việt có dấu, blunt khi cần.
- Luôn cite nguồn vault (Bloodwork_Update / doctor report / GPro).

---

## Pitfalls

- **Đừng re-recommend test gần đây.** Luôn chạy Recency Gate (bước 5) trước khi đưa vào toa.
- **Đừng bịa giá lab.** Không đoán giá DIAG. Thay vào đó: (a) báo Bố xem app DIAG; (b) gọi hotline 1900 1717; (c) ước lượng thị trường VNĐ gắn tag [LOW].
- **Line-by-line khi tra giá / research:** Trình bày từng bước search + từng khoản giá riêng lẻ.
- **BP từ Sleep_Log là data thật:** WNK1 gen lệch Na/K nhưng thực tế BP Bố 95-99/70-72 rất đẹp → không scare.
- **Tính LDL Friedewald khi lab không cấp:** DIAG thường không trả LDL trực tiếp → tính LDL = Cholesterol Total - HDL - (Triglycerides/2.2) với mmol/L. Ghi rõ công thức đã dùng.
- **Dedup PDF theo mã hồ sơ:** Field "Mã hồ sơ" trong PDF DIAG = unique identifier. Cùng mã = trùng → xoá, ghi rõ tên file đã xoá.
- **Genotype-phenotype cross-reference:** Khi tư vấn, luôn so sánh kết quả lab thực tế với genetic prediction (ALDH2, APOA5, IGF2BP2, CYP1A1, CYP1A2, MMP3).
- **Dashboard format:** Bố muốn HTML/Chart.js với traffic-light colors, target reference lines, tab filter.
- **THIẾU 1 GENETICS FILE = ADVISE SAI:** Nếu không đọc đủ 4 file genetics, không được phép đưa ra bất kỳ khuyến nghị y tế nào.
- **GỬI READ CONFIRMATION TRƯỚC KHI ADVISE:** Nếu con viết advice mà chưa gửi read confirmation = vi phạm. Read confirmation phải có số dòng thực tế + key fact cụ thể.

---

## References
- `references/recency_rules.md` — bảng tần suất chi tiết + cite exact.
- `references/friedewald_calc.md` — công thức Friedewald, khi nào dùng, giới hạn, ví dụ tính.
- `references/dashboard_format.md` — HTML/Chart.js dashboard spec cho bloodwork trend.
