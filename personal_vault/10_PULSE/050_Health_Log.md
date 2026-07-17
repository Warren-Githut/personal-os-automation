---
domain: health
type: pulse
status: active
last_updated: 2026-06-01
---

# 050 — Health Log

<!-- Health metrics, weekly check-in, body signals -->


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
- Tỷ lệ Chol/HDL: 3.11 (<5) — ✅ tốt

📌 Insight:
Cholesterol cải thiện so với 13/01/2026 (TP 6.13→5.41, LDL 4.17→3.49).
Xu hướng tích cực — có thể nhờ thay đổi chế độ ăn/uống.

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
- Creatinine: 105.80 µmol/L (53-114.9) — ✅ bình thường
- eGFR (CKD-EPI 2021): 99.29 mL/min (≥90) — ✅ bình thường
- HOMA-IR: 1.03 (<2.5) — ✅ không kháng insulin
- Glucose đói: 4.91 mmol/L (3.9-5.5) — ✅ bình thường
- Sắt, Transferrin, TIBC: bình thường

📌 Insight:
Full panel — sức khỏe tổng quát tốt. Cholesterol TP gần upper limit,
LDL ở ngưỡng cao — cần theo dõi.

---

### 2025-08-25 — DIAG Lab — 25/08/2025
**Source:** `_inbox/inbox-notes/25010495267_vi.pdf`
**Type:** pdf
**Tool used:** liteparse OCR

📄 Key results:
- HbA1c: 5.40% (<5.7) — ✅ bình thường
- Creatinine: 117.60 µmol/L (53-114.9) — 🟡 hơi cao
- eGFR (CKD-EPI 2021): 95.09 (≥90) — ✅ bình thường
- Microalbumin/Creatinin: 5.76 mg/g (<30) — ✅ bình thường
- Điện giải đồ (Na, K, Cl): bình thường
- Urea, Acid Uric: bình thường

📌 Insight:
HbA1c ổn định. Creatinine slightly trên ngưỡng — cần theo dõi
trend (đã ở upper limit từ 02/2025).

---

### 2025-07-29 — DIAG Lab — 29/07/2025
**Source:** `_inbox/inbox-notes/25010425268_vi_1.pdf`
**Type:** pdf
**Tool used:** liteparse OCR

📄 Key results:
- Creatinine: 115.30 µmol/L (53-114.9) — 🟡 slightly cao
- eGFR: 70.24 mL/min (≥90) — 🟡 thấp

📌 Insight:
eGFR 70 thấp hơn các lần khác. Có thể do công thức tính khác
(không có Cystatin C) hoặc biến động tạm thời.

---

### 2025-05-25 — DIAG Lab — 25/05/2025
**Source:** `_inbox/inbox-notes/25010259876_vi_1.pdf`
**Type:** pdf
**Tool used:** liteparse OCR

📄 Key results:
- Creatinine: 105.30 µmol/L (53-114.9) — ✅ bình thường
- eGFR: 78.40 (≥90) — 🟡 thấp

📌 Insight:
(no insight needed)

---

### 2025-04-19 — DIAG Lab — 19/04/2025
**Source:** `_inbox/inbox-notes/25010187124_vi_1.pdf`
**Type:** pdf
**Tool used:** liteparse OCR

📄 Key results:
- Creatinine: 106.20 µmol/L (53-114.9) — ✅ bình thường
- eGFR: 77.66 (≥90) — 🟡 thấp

📌 Insight:
(no insight needed)

---

### 2025-04-13 — DIAG Lab — 13/04/2025
**Source:** `_inbox/inbox-notes/25020173074_vi_1.pdf`
**Type:** pdf
**Tool used:** liteparse OCR

📄 Key results:
- HbA1c: 5.60% (<5.7) — 🟡 gần ngưỡng tiền tiểu đường
- eAG: 6.33 mmol/L

📌 Insight:
HbA1c 5.6 là mức cao nhất trong các lần xét nghiệm — sát ngưỡng 5.7.
Đây có thể là lý do Warren làm thêm xét nghiệm HOMA-IR sau đó.

---

### 2025-03-06 — DIAG Lab — 06/03/2025
**Source:** `_inbox/inbox-notes/25010087800_vi (1).pdf`
**Type:** pdf
**Tool used:** liteparse OCR

📄 Key results:
- Canxi: 2.44 mmol/L (2.1-2.55) — ✅ bình thường
- Creatinine: 107.80 µmol/L (53-114.9) — ✅ bình thường
- eGFR: 76.33 (≥90) — 🟡 thấp

📌 Insight:
(no insight needed)

---

### 2025-02-07 — DIAG Lab — 07/02/2025
**Source:** `_inbox/inbox-notes/25010032316_vi (1).pdf`
**Type:** pdf
**Tool used:** liteparse OCR

📄 Key results:
- Canxi: 2.37 mmol/L (2.1-2.55) — ✅ bình thường
- Creatinine: 104.90 µmol/L (53-114.9) — ✅ bình thường
- eGFR: 78.91 (≥90) — 🟡 thấp

📌 Insight:
(no insight needed)

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
Xét nghiệm đầu tiên trong chuỗi — Creatinine đã ở upper limit từ 01/2024.
Vitamin D bình thường — không thiếu.

---




