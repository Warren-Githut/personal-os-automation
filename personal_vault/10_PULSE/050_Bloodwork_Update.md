---
domain: health
type: pulse
status: active
last_updated: 2026-08-05
report_dates: [2026-08-05, 2026-06-11, 2026-03-18, 2026-01-13, 2025-08-25, 2025-07-29, 2025-05-25, 2025-04-19, 2025-04-13, 2025-03-06, 2025-02-07, 2024-01-22]
dashboard: ../30_KNOWLEDGE_BASE/wiki/02_Health/aa_Bloodwork_Health_Baseline/001_Bloodwork_Dashboard.html
---

# 050 — Bloodwork Update

<!-- Bloodwork results from DIAG Lab. Newest on top. -->

> **Quy tắc:** Newest on top — entry mới nhất ở trên cùng.
> Khi thêm entry mới → copy template bên dưới, điền thông tin, prepend sau dòng này.

---

## Template
```
### YYYY-MM-DD — {title}
**Source:** _inbox/{subfolder}/{filename}
**Type:** {file type: text / csv / excel / docx / pdf / image}
**Tool used:** {pandas / python-docx / liteparse / direct-read}

📄 Key results:
- {metric}: {value} ({range}) — {status emoji} {note}
- ...

📌 Insight:
{1-2 dòng — trend / anomaly / actionable. "(no insight needed)" nếu không có gì đặc biệt}

---
```

### 2026-08-05 — DIAG Lab — 05/08/2026 (Panel: Đường huyết + Mỡ máu + Cystatin C)
**Source:** `_inbox/inbox-notes/26020536566_vi_1.pdf`
**Type:** pdf
**Tool used:** direct-read

📄 Key results:
- HbA1c (NGSP): 5.5% (<5.7) ✅ bình thường
- HbA1c (IFCC): 37 mmol/mol (<39) ✅ bình thường
- Ước lượng Glucose Máu Trung Bình (eAG): 6.17 mmol/L (111 mg/dL) ✅ bình thường
- Glucose đói: 5.43 mmol/L (98 mg/dL, ref 3.9-5.5) ✅ bình thường
- Cholesterol TP: 5.99 mmol/L (<5.18 mong muốn) 🟡 ngưỡng cao
- HDL: 1.65 mmol/L (≥1.55) ✅ tốt
- Triglycerides: 0.89 mmol/L (<1.7) ✅ bình thường
- LDL (Friedewald): 3.94 mmol/L (<2.59 tối ưu, mục tiêu <3.35) 🟡 ngưỡng cao
- ApoB: 99.22 mg/dL (lab ref 60-140, mục tiêu <100) 🟡 gần mục tiêu
- ApoA1: 154.40 mg/dL (lab ref 105-175) ✅ bình thường
- Tỷ lệ ApoB/ApoA1: 0.64 (<0.7) ✅ tốt
- Cystatin C: 0.78 mg/L (0.31-0.79) ✅ bình thường

📌 Insight:
HbA1c ổn định 5.5% (giảm nhẹ từ 5.6 cao nhất 04/2025). Glucose đói 5.43 bình thường. Trục mỡ máu: LDL giảm nhẹ từ 4.50 (06/2026) xuống 3.94 nhưng vượt mục tiêu 3.35. ApoB 99.22 gần mục tiêu <100 — xu hướng đẹp (108→90→99). Tỷ lệ ApoB/A1 0.64 tốt. Gen APOA5/PPARG (chuyển hóa béo kém) vẫn đang được xác nhận bởi phenotype LDL cao. Cần cắt béo bão hòa mạnh hơn. Lặp lipid panel sau 3 tháng (mục tiêu: LDL <3.35, ApoB <100).

---

### 2026-06-11 — DIAG Lab — 11/06/2026 (Panel nâng cao: Gan + ApoB + CRP + VitD)
**Source:** `_inbox/inbox-notes/26020371792_vi_1.pdf`
**Type:** pdf
**Tool used:** direct-read

📄 Key results:
- ALT (GPT): 14 U/L (<45) — ✅ bình thường
- AST (GOT): 25 U/L (<37) — ✅ bình thường
- GGT: 20 U/L (<55) — ✅ thấp, gan không tổn thương do rượu (ALDH2)
- ALP: 52 U/L (50-116) — ✅ bình thường
- Bilirubin TP: 13.12 µmol/L (5.1-20.5) — ✅ bình thường
- Bilirubin TT: 4.17 µmol/L (<8.6) — ✅ bình thường
- Bilirubin GT: 8.95 µmol/L (3.4-13.7) — ✅ bình thường
- Albumin: 48 g/L (35-50) — ✅ bình thường
- PT/INR: 13.0s / INR 0.97 — ✅ bình thường
- hs-CRP: 0.51 mg/L (mục tiêu <1.0) — ✅ không viêm, xuất sắc
- Vitamin D (25-OH): 46 ng/mL (đủ 30-100) — ✅ tăng từ 39.9 (2024)
- ApoB: 120.51 mg/dL (lab ref 60-140, mục tiêu phòng ngừa <100) — 🟡 cao hơn tối ưu
- LDL: 4.50 mmol/L (<2.59 tối ưu) — 🔴 cao, TĂNG so với 3.49 (03/2026)
- Cholesterol TP: 6.27 mmol/L (<5.18) — 🔴 nguy cơ cao
- Non-HDL: 4.86 mmol/L (<3.37) — 🔴 cao
- HDL: 1.41 mmol/L (≥1.55) — 🟡 giảm từ 1.74
- Triglycerides: 0.79 mmol/L (<1.7) — ✅ bình thường
- Tỷ lệ Chol/HDL: 4.45 (<5) — ✅ bình thường

📌 Insight:
Loại 3 nỗi lo: gan sạch hoàn toàn (GGT 20 xác nhận sống đúng gen ALDH2), không viêm (CRP 0.51), vit D đủ (46). KHOANH VÙNG 1 việc: trục mỡ máu xấu đi. LDL dao động 4.17→3.49→4.50 (lên-xuống-lên), ApoB 120 > mục tiêu 100. Gen chuyển hóa béo kém (APOA5/PPARG) → cắt béo bão hòa là ưu tiên #1. CRP thấp là yếu tố giảm nhẹ (nhiều hạt nhưng không viêm). Lặp lipid sau 3 tháng (mục tiêu 09/2026: LDL <3.35, ApoB <100); nếu vẫn cao → gặp BS tim mạch.

---

### 2026-03-18 — DIAG Lab — 18/03/2026
**Source:** `_inbox/inbox-notes/26010152213_vi.pdf`
**Type:** pdf
**Tool used:** liteparse OCR

📄 Key results:
- Triglycerides: 0.40 mmol/L (<1.7) — ✅ bình thường
- Cholesterol TP: 5.41 mmol/L (<5.18 mong muốn) — 🟡 ngưỡng cao
- HDL: 1.74 mmol/L (≥1.55) — ✅ tốt
- LDL: 3.49 mmol/L (<2.59 tối ưu) — 🟡 cao
- ApoB: 89.91 mg/dL (60-140, mục tiêu <100) ✅ tốt
- Tỷ lệ Chol/HDL: 3.11 (<5) — ✅ tốt
- hs-CRP: 0.63 mg/L (<5) — ✅ bình thường
- Lipoprotein (a): 24.95 mg/dL (<50) — ✅ bình thường
- HOMA-IR: 1.01 (<2.5) — ✅ không kháng insulin
- Glucose đói: 4.93 mmol/L (3.9-5.5) — ✅ bình thường
- Insulin: 4.62 µU/mL (2-25) — ✅ bình thường

📌 Insight:
Cholesterol cải thiện so với 13/01/2026 (TP 6.13→5.41, LDL 4.17→3.49). ApoB giảm từ 108 xuống 90 — rất tốt. Xu hướng tích cực — có thể nhờ thay đổi chế độ ăn/uống. Lp(a) 24.95 bình thường (gen tim mạch tốt được xác nhận).

---

### 2026-01-13 — DIAG Lab — 13/01/2026
**Source:** `_inbox/inbox-notes/26020025657_vi (1).pdf`
**Type:** pdf
**Tool used:** liteparse OCR

📄 Key results:
- HbA1c: 5.5% (<5.7) — ✅ bình thường
- Cholesterol TP: 6.13 mmol/L (5.18-6.21) — 🟡 ngưỡng nguy cơ
- LDL: 4.17 mmol/L (3.35-4.13) — 🟡 cao
- HDL: 1.73 mmol/L (≥1.55) — ✅ tốt
- Triglycerides: 0.50 mmol/L (<1.7) — ✅ bình thường
- ApoB: 108 mg/dL (60-140, mục tiêu <100) 🟡 cao
- ApoA1: 169 mg/dL (105-175) ✅ tốt
- Non-HDL: 4.40 mmol/L (<3.37) 🔴 cao
- Creatinine: 105.80 µmol/L (53-114.9) — ✅ bình thường
- eGFR (CKD-EPI 2021): 99.29 mL/min (≥90) — ✅ bình thường
- HOMA-IR: 1.03 (<2.5) — ✅ không kháng insulin
- Glucose đói: 4.91 mmol/L (3.9-5.5) — ✅ bình thường
- Sắt: 22.30 µmol/L (11.6-31.3) ✅ bình thường
- Transferrin: 238 mg/dL (174-364) ✅ bình thường
- TIBC: 37.48 µmol/L? ✅ bình thường

📌 Insight:
Full panel — sức khỏe tổng quát tốt. Cholesterol TP gần upper limit, LDL ở ngưỡng cao — cần theo dõi. HOMA-IR 1.03 xuất sắc (gen IGF2BP2 bù đắp tốt).

---

### 2025-08-25 — DIAG Lab — 25/08/2025
**Source:** `_inbox/inbox-notes/25010495267_vi.pdf`
**Type:** pdf
**Tool used:** liteparse OCR

📄 Key results:
- HbA1c: 5.40% (<5.7) — ✅ bình thường
- Creatinine: 117.60 µmol/L (53-114.9) — 🟡 hơi cao
- eGFR (CKD-EPI 2021): 95.09 (≥90) — ✅ bình thường
- Cystatin C: 0.74 mg/L (0.31-0.79) ✅ bình thường
- Microalbumin/Creatinin: 5.76 mg/g (<30) — ✅ bình thường
- Điện giải đồ (Na, K, Cl): bình thường
- Urea: 4.38 mmol/L (3.2-7.4) ✅ bình thường
- Acid Uric: 0.376 mmol/L (0.22-0.45) ✅ bình thường

📌 Insight:
HbA1c ổn định. Creatinine slightly trên ngưỡng — cần theo dõi trend (đã ở upper limit từ 02/2025). eGFR phục hồi tốt.

---

### 2025-07-29 — DIAG Lab — 29/07/2025
**Source:** `_inbox/inbox-notes/25010425268_vi_1.pdf`
**Type:** pdf
**Tool used:** liteparse OCR

📄 Key results:
- Creatinine: 115.30 µmol/L (53-114.9) — 🟡 slightly cao
- eGFR: 70.24 mL/min (≥90) — 🟡 thấp nhất
- Cystatin C: 0.80 mg/L (0.31-0.79) 🟡 hơi cao

📌 Insight:
eGFR 70 thấp hơn các lần khác. Cystatin C hơi cao — cần theo dõi. Có thể do mất nước hoặc biến động tạm thời.

---

### 2025-05-25 — DIAG Lab — 25/05/2025
**Source:** `_inbox/inbox-notes/25010259876_vi_1.pdf`
**Type:** pdf
**Tool used:** liteparse OCR

📄 Key results:
- Creatinine: 105.30 µmol/L (53-114.9) — ✅ bình thường
- eGFR: 78.40 (≥90) — 🟡 thấp
- Cystatin C: 0.79 mg/L (0.31-0.79) ✅ bình thường
- Testosterone: 30.22 nmol/L (8.33-30.19) 🟡 gần upper limit
- Testosterone: 871.54 ng/dL (240.24-870.68) 🟡 gần upper limit

📌 Insight:
Testosterone gần upper limit — bình thường ở tuổi 42. eGFR thấp nhưng Cystatin C bình thường.

---

### 2025-04-19 — DIAG Lab — 19/04/2025
**Source:** `_inbox/inbox-notes/25010187124_vi_1.pdf`
**Type:** pdf
**Tool used:** liteparse OCR

📄 Key results:
- Creatinine: 106.20 µmol/L (53-114.9) — ✅ bình thường
- eGFR: 77.66 (≥90) — 🟡 thấp
- Cystatin C: 0.83 mg/L (0.31-0.79) 🟡 hơi cao

📌 Insight:
eGFR thấp kéo dài từ 02/2025. Cystatin C hơi cao — cần theo dõi chức năng thận.

---

### 2025-04-13 — DIAG Lab — 13/04/2025
**Source:** `_inbox/inbox-notes/25020173074_vi_1.pdf`
**Type:** pdf
**Tool used:** liteparse OCR

📄 Key results:
- HbA1c: 5.60% (<5.7) — 🟡 gần ngưỡng tiền tiểu đường
- eAG: 6.33 mmol/L
- Creatinine: 104.60 µmol/L (53-114.9) — ✅ bình thường
- eGFR: 79.09 (≥90) — 🟡 thấp
- HOMA-IR: 0.55 (<2.5) — ✅ xuất sắc
- Glucose đói: 4.72 mmol/L (3.9-5.5) — ✅ bình thường
- Insulin: 2.60 µU/mL (2-25) — ✅ bình thường
- Urea: 3.35 mmol/L (3.2-7.4) ✅ bình thường
- Microalbumin: 3.50 mg/L ✅ bình thường
- Micro/Cr: 5.68 mg/g (<30) ✅ bình thường
- iPTH: 66.5 pg/mL (15-68.3) ✅ bình thường
- Điện giải: Na 139, K 4.23, Cl 106 — ✅ bình thường
- Canxi: 2.36 mmol/L (2.1-2.55) ✅ bình thường
- Phospho: 1.16 mmol/L (0.81-1.45) ✅ bình thường

📌 Insight:
HbA1c 5.6 là mức cao nhất trong các lần xét nghiệm — sát ngưỡng 5.7. HOMA-IR 0.55 xuất sắc (gen IGF2BP2 bù đắp). Đây có thể là lý do Warren làm thêm xét nghiệm HOMA-IR chi tiết.

---

### 2025-03-06 — DIAG Lab — 06/03/2025
**Source:** `_inbox/inbox-notes/25010087800_vi (1).pdf`
**Type:** pdf
**Tool used:** liteparse OCR

📄 Key results:
- Canxi: 2.44 mmol/L (2.1-2.55) — ✅ bình thường
- Creatinine: 107.80 µmol/L (53-114.9) — ✅ bình thường
- eGFR: 76.33 (≥90) — 🟡 thấp
- Urea: 3.45 mmol/L (3.2-7.4) ✅ bình thường
- iPTH: 64.9 pg/mL (15-68.3) ✅ bình thường
- Điện giải: Na 137, K 3.48, Cl 102 — ✅ bình thường
- Phospho: 0.97 mmol/L (0.74-1.52) ✅ bình thường

📌 Insight:
eGFR thấp kéo dài. Kali 3.48 gần lower limit — cần theo dõi (gen WNK1).

---

### 2025-02-07 — DIAG Lab — 07/02/2025
**Source:** `_inbox/inbox-notes/25010032316_vi (1).pdf`
**Type:** pdf
**Tool used:** liteparse OCR

📄 Key results:
- Canxi: 2.37 mmol/L (2.1-2.55) — ✅ bình thường
- Creatinine: 104.90 µmol/L (53-114.9) — ✅ bình thường
- eGFR: 78.91 (≥90) — 🟡 thấp
- Urea: 3.58 mmol/L (3.2-7.4) ✅ bình thường
- iPTH: 60.6 pg/mL (15-68.3) ✅ bình thường
- Điện giải: Na 139, K 3.88, Cl 104 — ✅ bình thường
- Phospho: 0.99 mmol/L (0.74-1.52) ✅ bình thường

📌 Insight:
eGFR thấp lần đầu xuất hiện (79). Creatinine bình thường. Cần theo dõi trend.

---

### 2024-01-22 — DIAG Lab — 22/01/2024
**Source:** `_inbox/inbox-notes/2410010676_vi (1).pdf`
**Type:** pdf
**Tool used:** liteparse OCR

📄 Key results:
- Creatinine: 114.80 µmol/L (63.6-110.5) — 🟡 slightly cao
- Canxi: 2.35 mmol/L (2.1-2.55) — ✅ bình thường
- Vitamin D (25-OH): 39.9 ng/mL (30-100) — ✅ bình thường

📌 Insight:
Xét nghiệm đầu tiên trong chuỗi — Creatinine đã ở upper limit từ 01/2024. Vitamin D bình thường — không thiếu.

---
