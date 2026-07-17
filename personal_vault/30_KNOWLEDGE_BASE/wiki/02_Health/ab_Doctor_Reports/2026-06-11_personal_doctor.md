---
domain: health
type: analysis
status: active
data_status: analysis
last_updated: 2026-06-11
tags:
  - personal_doctor
  - bloodwork
  - lipid
  - genetics
  - longevity
related:
  - ../ac_Warren_Genetics_Report/GPro_Genetic_Database.md
  - ../ac_Warren_Genetics_Report/GPro_Master_Health_Protocol.md
  - ../../../10_PULSE/050_Health_Log.md
  - ../../../10_PULSE/Daily_Pulse.md
  - ../../../00_CORE_LOGIC/PERSONAL_CONTEXT.md
---

# Personal Doctor Report — 2026-06-11

**Ingested from:** `/personal_doctor` full report.
**Warren approval:** Confirmed 2026-06-11 13:07 +07:00.
**Purpose:** Permanent health analysis from latest vault data, genetics, sleep, bloodwork, and guideline-based evidence.

> [!summary] Executive summary
> Ưu tiên số 1 hiện tại là mỡ máu xấu đi: LDL-C 4.50 mmol/L và ApoB 120.51 mg/dL. Gan hiện tại ổn với ALT 14, AST 25, GGT 20. Viêm thấp với hs-CRP 0.51 mg/L. Vitamin D đủ ở 46 ng/mL. Sleep hiện tại tốt: 7h20 và quality 91/100 ngày 2026-06-11.

## 1. Patient Context

- Warren, 42 tuổi, nam, BMI ~21.5 (source: `00_CORE_LOGIC/PERSONAL_CONTEXT.md` → HEALTH BASELINE). [HIGH]
- Nghề nghiệp: Head of Operations tại L'Usine Saigon, stress và giờ làm dài (source: `00_CORE_LOGIC/PERSONAL_CONTEXT.md` → WARREN - Profile). [HIGH]
- IF 16:8, eating window 12:00-20:00 (source: `00_CORE_LOGIC/PERSONAL_CONTEXT.md` → HEALTH BASELINE). [HIGH]
- Sleep gần nhất: 7h20, quality 91/100, weight 63 kg, fasting 17h ngày 2026-06-11 (source: `10_PULSE/Daily_Pulse.md` → 2026-06-11 entry). [HIGH]
- BP gần nhất: 99/69 mmHg ngày 2026-06-11 (source: `10_PULSE/Daily_Pulse.md` → 2026-06-11 entry). [HIGH]

## 2. Red Flag Check

Không trigger “SEE A DOCTOR THIS WEEK” ngay lúc này. [HIGH]

- ALT/AST/GGT không vượt >3x ULN: ALT 14, AST 25, GGT 20 (source: `10_PULSE/050_Health_Log.md` → 2026-06-11 entry). [HIGH]
- eGFR mới nhất 99.29, không <60 sustained (source: `10_PULSE/050_Health_Log.md` → 2026-01-13 entry). [HIGH]
- BP 99/69, không >=180/110 (source: `10_PULSE/Daily_Pulse.md` → 2026-06-11 entry). [HIGH]
- HbA1c cao nhất trong vault 5.60%, chưa >=5.7% và xa ngưỡng >9% (source: `10_PULSE/050_Health_Log.md` → 2025-04-13 entry). [HIGH]
- LDL-C mới nhất 4.50 mmol/L, cao nhưng chưa vượt ~4.92 mmol/L tương đương 190 mg/dL (source: `10_PULSE/050_Health_Log.md` → 2026-06-11 entry). [HIGH]

## 3. Bloodwork Trend

### Lipid / Cardiovascular

- LDL-C: 4.17 mmol/L ngày 2026-01-13 → 3.49 ngày 2026-03-18 → 4.50 ngày 2026-06-11 (source: `10_PULSE/050_Health_Log.md` → 2026-01-13, 2026-03-18, 2026-06-11 entries). [HIGH]
- ApoB: 120.51 mg/dL, cao hơn mục tiêu phòng ngừa <100 mg/dL trong log (source: `10_PULSE/050_Health_Log.md` → 2026-06-11 entry). [HIGH]
- Cholesterol TP: 6.13 → 5.41 → 6.27 mmol/L (source: `10_PULSE/050_Health_Log.md` → 2026-01-13, 2026-03-18, 2026-06-11 entries). [HIGH]
- HDL: 1.73 → 1.74 → 1.41 mmol/L (source: `10_PULSE/050_Health_Log.md` → 2026-01-13, 2026-03-18, 2026-06-11 entries). [HIGH]
- Triglycerides: 0.50 → 0.40 → 0.79 mmol/L, vẫn <1.7 mmol/L (source: `10_PULSE/050_Health_Log.md` → 2026-01-13, 2026-03-18, 2026-06-11 entries). [HIGH]
- Chol/HDL ratio: 4.45 ngày 2026-06-11, dưới ngưỡng 5 trong log (source: `10_PULSE/050_Health_Log.md` → 2026-06-11 entry). [HIGH]

**Interpretation:** Pattern chính là LDL/ApoB xấu đi, không phải triglyceride cao hoặc viêm cao. [HIGH]

### Liver

- ALT 14 U/L, AST 25 U/L, GGT 20 U/L, bilirubin/albumin/PT-INR bình thường (source: `10_PULSE/050_Health_Log.md` → 2026-06-11 entry). [HIGH]

**Interpretation:** Không có bằng chứng bloodwork hiện tại về tổn thương gan. [HIGH]

### Kidney

- Creatinine: 117.60 µmol/L ngày 2025-08-25 → 105.80 ngày 2026-01-13 (source: `10_PULSE/050_Health_Log.md` → 2025-08-25, 2026-01-13 entries). [HIGH]
- eGFR: 70.24 ngày 2025-07-29 → 78.40 ngày 2025-05-25 → 99.29 ngày 2026-01-13 (source: `10_PULSE/050_Health_Log.md` → 2025-07-29, 2025-05-25, 2026-01-13 entries). [HIGH]
- Microalbumin/Creatinin: 5.76 mg/g ngày 2025-08-25, dưới <30 mg/g (source: `10_PULSE/050_Health_Log.md` → 2025-08-25 entry). [HIGH]

**Interpretation:** Không red flag thận hiện tại, nhưng biến động eGFR 70-99 cần lặp lại cùng lab/method hoặc thêm cystatin C. [MOD]

### Metabolic / Pre-diabetes

- HbA1c: 5.60% ngày 2025-04-13 → 5.40% ngày 2025-08-25 → 5.50% ngày 2026-01-13 (source: `10_PULSE/050_Health_Log.md` → 2025-04-13, 2025-08-25, 2026-01-13 entries). [HIGH]
- Fasting glucose: 4.91 mmol/L ngày 2026-01-13, trong range 3.9-5.5 (source: `10_PULSE/050_Health_Log.md` → 2026-01-13 entry). [HIGH]
- HOMA-IR: 1.03 <2.5 ngày 2026-01-13 (source: `10_PULSE/050_Health_Log.md` → 2026-01-13 entry). [HIGH]

**Interpretation:** HbA1c sát ngưỡng nhưng HOMA-IR tốt; IF/lifestyle đang compensating tốt. [HIGH]

### Inflammation / Vitamin D

- hs-CRP: 0.51 mg/L, dưới mục tiêu <1.0 (source: `10_PULSE/050_Health_Log.md` → 2026-06-11 entry). [HIGH]
- Vitamin D 25-OH: 46 ng/mL, tăng từ 39.9 ng/mL năm 2024 (source: `10_PULSE/050_Health_Log.md` → 2026-06-11, 2024-01-22 entries). [HIGH]

## 4. Risk Assessment

### Cardiovascular / Lipid

- LDL/ApoB cao, HDL giảm, cholesterol TP tăng lại (source: `10_PULSE/050_Health_Log.md` → 2026-06-11 entry). [HIGH]
- Fat Metabolism poor, APOA5/PPARG adverse (source: `30_KNOWLEDGE_BASE/wiki/02_Health/ac_Warren_Genetics_Report/GPro_Genetic_Database.md` → Fat Metabolism module). [HIGH]

**Gen × phenotype:** Gen warns + Bloodwork confirms. Đây là rủi ro thật, không chỉ noise di truyền. [HIGH]

### Liver

- LFT bình thường (source: `10_PULSE/050_Health_Log.md` → 2026-06-11 entry). [HIGH]
- ALDH2 rs671 defective, alcohol toxic, acetaldehyde accumulation, esophageal cancer risk tăng (source: `30_KNOWLEDGE_BASE/wiki/02_Health/ac_Warren_Genetics_Report/GPro_Genetic_Database.md` → Alcohol Flush Syndrome module). [HIGH]

**Gen × phenotype:** Bloodwork gan ổn, nhưng môi trường F&B + ALDH2 vẫn là risk cluster. [HIGH]

### Kidney

- eGFR từng thấp 70-78 trong 2025, sau đó 99.29 ngày 2026-01-13 (source: `10_PULSE/050_Health_Log.md` → 2025-07-29, 2025-05-25, 2026-01-13 entries). [HIGH]
- Microalbumin/Creatinin bình thường (source: `10_PULSE/050_Health_Log.md` → 2025-08-25 entry). [HIGH]

**Gen × phenotype:** Không có kidney gene flag chính trong vault; theo dõi bằng bloodwork. [MOD]

### Metabolic / Pre-diabetes

- HbA1c 5.4-5.6%, chưa >=5.7% (source: `10_PULSE/050_Health_Log.md` → 2025-04-13, 2025-08-25, 2026-01-13 entries). [HIGH]
- HOMA-IR 1.03, không insulin resistance (source: `10_PULSE/050_Health_Log.md` → 2026-01-13 entry). [HIGH]
- Diabetes risk top 25%, IGF2BP2/SREBF1 adverse (source: `30_KNOWLEDGE_BASE/wiki/02_Health/ac_Warren_Genetics_Report/GPro_Genetic_Database.md` → Diabetes Risk module). [HIGH]

**Gen × phenotype:** Gen warns + lifestyle compensating. IF là protective factor hiện tại. [HIGH]

### Sleep / Circadian

- Sleep 7h20, quality 91/100 ngày 2026-06-11; 7h20, quality 93 ngày 2026-06-10 (source: `10_PULSE/Daily_Pulse.md` → 2026-06-11, 2026-06-10 entries). [HIGH]
- Caffeine fast metabolizer, low insomnia risk (source: `30_KNOWLEDGE_BASE/wiki/02_Health/ac_Warren_Genetics_Report/GPro_Genetic_Database.md` → Caffeine Metabolism and Insomnia Tendency modules). [HIGH]

**Interpretation:** Sleep hiện tại tốt; nếu sleep giảm, ưu tiên kiểm tra stress, màn hình, caffeine sau 14h. [MOD]

### Genetic-Environment Interaction

- ALDH2 defective + F&B industry + stress-drinking tendency là risk cluster (source: `30_KNOWLEDGE_BASE/wiki/02_Health/ac_Warren_Genetics_Report/GPro_Master_Health_Protocol.md` → Axis 1 Alcohol). [HIGH]
- Detox capacity bottom 10%, CYP1A1/CYP3A adverse (source: `30_KNOWLEDGE_BASE/wiki/02_Health/ac_Warren_Genetics_Report/GPro_Genetic_Database.md` → Detoxification Capacity module). [HIGH]

### Exercise / Injury

- Injury Risk very high, top 8%, IGF2/MMP3 adverse (source: `30_KNOWLEDGE_BASE/wiki/02_Health/ac_Warren_Genetics_Report/GPro_Genetic_Database.md` → Injury Risk module). [HIGH]
- Cardiovascular Health genetic module poor, Endurance good (source: `30_KNOWLEDGE_BASE/wiki/02_Health/ac_Warren_Genetics_Report/GPro_Genetic_Database.md` → Cardiovascular Health and Endurance modules). [HIGH]

## 5. Recommendations

### 90-day lipid priority

1. Cắt saturated fat là ưu tiên số 1: giảm đồ chiên, mỡ động vật, da, bơ động vật, nước cốt dừa béo; ưu tiên cá, đậu, dầu olive, bơ, hạt vừa phải [Strong evidence: AHA/ACC 2018; ESC/EAS 2019].
2. Lặp lipid panel + ApoB sau 3 tháng. Nếu LDL vẫn >=4.0 mmol/L hoặc ApoB vẫn >=100 mg/dL, thảo luận bác sĩ tim mạch về guideline-based treatment, không tự mua thuốc [Strong evidence: ESC/EAS 2019].
3. Duy trì post-meal walking 10-15 phút sau bữa chính [Moderate evidence: ADA 2025].

### Liver / alcohol

1. Zero alcohol là target đúng cho Warren vì ALDH2 defective và F&B exposure [Strong evidence: AASLD/clinical consensus; vault genetics: `GPro_Master_Health_Protocol.md` → Axis 1 Alcohol].
2. LFT nên là annual minimum; nếu có uống rượu hoặc stress uống, làm 6 tháng/lần [Moderate evidence: AASLD 2023 + vault genetics].
3. Tránh vitamin E supplement vì GPro cảnh báo APOA5 pro-inflammatory risk (source: `30_KNOWLEDGE_BASE/wiki/02_Health/ac_Warren_Genetics_Report/GPro_Master_Health_Protocol.md` → Supplement Summary). [MOD]

### Kidney follow-up

1. Lặp Creatinine, eGFR, Urea, Uric Acid, urine ACR trong 6 tháng tới; thêm cystatin C nếu eGFR lại thấp [Strong evidence: KDIGO 2024].
2. Theo dõi BP định kỳ; BP mới nhất 99/69 nhưng mới chỉ có 1 điểm dữ liệu (source: `10_PULSE/Daily_Pulse.md` → 2026-06-11 entry). [MOD]

### Metabolic / pre-diabetes

1. Duy trì IF 16:8 nếu bền vững; break fast bằng protein+fat, không phải carb tinh chế [Moderate evidence: ADA 2025; vault genetics: `GPro_Master_Health_Protocol.md` → Fasting Protocol].
2. HbA1c + fasting glucose mỗi 6 tháng; nếu HbA1c >=5.7%, xem đây là điểm genetics đang thắng lifestyle và cần siết carb ngay [Strong evidence: ADA 2025].
3. Đi bộ 10-15 phút sau bữa ăn, đặc biệt sau bữa nhiều carb [Moderate evidence: ADA 2025].

### Sleep

1. Giữ sleep >=7h, quality >=7/10; hiện tại 7h20 và quality 91/100 là tốt (source: `10_PULSE/Daily_Pulse.md` → 2026-06-11 entry). [HIGH]
2. Caffeine buổi sáng OK; nếu sleep quality giảm, cắt caffeine sau 14h (source: `30_KNOWLEDGE_BASE/wiki/02_Health/ac_Warren_Genetics_Report/GPro_Master_Health_Protocol.md` → Sleep Protocol). [MOD]
3. Nếu sleep <6h x 5 đêm hoặc quality <5/10 trong 2 tuần, đánh giá sleep specialist [Moderate evidence: AASM 2024].

### Exercise

1. Ưu tiên low-impact: bơi, đạp xe nhẹ, đi bộ nhanh, yoga/pilates, resistance nhẹ [Strong evidence: WHO 2020].
2. Tránh crossfit, chạy cường độ cao, contact sports, push through joint pain (source: `30_KNOWLEDGE_BASE/wiki/02_Health/ac_Warren_Genetics_Report/GPro_Master_Health_Protocol.md` → Injury Prevention). [HIGH]

## 6. Egg Guidance Addendum

Warren hỏi: “ăn hột gà có ok cho bloodwork trên của tôi ko?”

**Kết luận:** Ăn trứng được, nhưng không nên ăn nhiều lòng đỏ. Với LDL 4.50 mmol/L và ApoB 120.51 mg/dL, trứng là thực phẩm có kiểm soát, không phải thực phẩm cấm tuyệt đối. [MOD]

- Một quả trứng lớn chứa khoảng 186-200 mg dietary cholesterol [Source: AHA Dietary Cholesterol and Cardiovascular Risk Science Advisory, 2019; AHA 2023].
- Người có LDL cao nên giảm cả saturated fat và dietary cholesterol [Source: AHA 2023].
- Lòng trắng trứng không cao cholesterol và phù hợp hơn khi cần tăng protein [Source: AHA 2023].

**Practical rule cho Warren:**

- Lòng trắng: OK hơn, dùng thường xuyên hơn được. [MOD]
- Lòng đỏ: 2-4 quả/tuần trong giai đoạn LDL/ApoB còn cao. [MOD]
- Tránh trứng chiên bơ, mỡ heo, dầu dừa, ăn kèm bacon/xúc xích/thịt nguội. [Strong evidence: AHA 2023; AHA/ACC 2018]
- Bữa sáng sau fast nên là protein+fat+rau, không phải trứng nhiều lòng đỏ + bánh mì trắng nhiều. [MOD]

## 7. Hardest Question

Lần gần nhất Warren uống rượu là khi nào, uống bao nhiêu, và có áp lực uống vì công việc F&B không?

## 8. Medical References

1. AHA/ACC Guideline on the Management of Blood Cholesterol. 2018.
2. ESC/EAS Guidelines for the Management of Dyslipidaemias. 2019.
3. ADA Standards of Care in Diabetes. 2025.
4. KDIGO 2024 Clinical Practice Guideline for the Evaluation and Management of Chronic Kidney Disease.
5. AASLD Practice Guidance on NAFLD/MASLD. 2023.
6. AASM Consensus Statement on Sleep Duration in Adults. 2024.
7. WHO Guidelines on Physical Activity and Sedentary Behaviour. 2020.
8. Matthews DR et al. Homeostasis Model Assessment: Insulin Resistance and Beta-Cell Function. Diabetologia. 1985.
9. ACC/AHA Guideline for the Prevention, Detection, Evaluation, and Management of High Blood Pressure in Adults. 2017; ACC/AHA updates 2024.
10. AHA Dietary Cholesterol and Cardiovascular Risk: A Science Advisory. Circulation. 2020.
11. AHA. “Here’s the latest on dietary cholesterol and how it fits in with a healthy diet.” 2023.

## 9. Vault Sources

- `10_PULSE/050_Health_Log.md`
- `10_PULSE/Daily_Pulse.md`
- `00_CORE_LOGIC/PERSONAL_CONTEXT.md`
- `30_KNOWLEDGE_BASE/wiki/02_Health/ac_Warren_Genetics_Report/GPro_Genetic_Database.md`
- `30_KNOWLEDGE_BASE/wiki/02_Health/ac_Warren_Genetics_Report/GPro_Master_Health_Protocol.md`
- `30_KNOWLEDGE_BASE/wiki/02_Health/ac_Warren_Genetics_Report/GPro_Strengths_Map.md`
