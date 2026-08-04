---
name: promo-comparison
description: "So sánh 2 promo/idea L'Usine head-to-head để chọn winner — role-play FBM 30-year veteran, build bảng ≥10 trục từ data thật (09_Hourly), pull W29 live signal, recommend winner + 3 options, update case thắng + mark case thua superseded. Dùng khi Warren nói 'so sánh A vs B' / 'model nào tối ưu' / 'đối đầu'. Tiếng Việt có dấu."
version: 1.0.0
tags: [promo, comparison, marketing, lusine, fbm, decision]
category: mkt
related_skills: [promo-eval, ops-mkt-manager-os, marketing-council, combo-calculation-gp, exec-proposal-email]
---

# promo-comparison — Chọn winner giữa 2 promo

> **Mục đích:** Warren pit 2 promo against nhau → con so sánh khách quan, có data, role-play FBM 30 năm, đề xuất winner + mark loser superseded.
> **KHÁC promo-eval:** promo-eval eval 1 promo. Cái này so 2 promo để CHỌN.

## 1. WHEN TO USE
- Warren: "so sánh A vs B", "model nào tối ưu hơn", "đối đầu 2 promo", "chọn 1 trong 2".
- Có ≥2 case file hoặc 2 ý tưởng promo cùng daypart/store.

## 2. HARD WORKFLOW
1. **Load cả 2 case file** (hoặc 2 mô tả). Đọc frontmatter + concept + ROI.
2. **Pull data thật từ `09_Hourly`** (cùng daypart, ≥4 tuần đủ giờ — WARN nếu <4 tuần, Zone 🟡 hỏi Bố). Re-derive baseline CẢ 2.
3. **Role-play FBM 30-year veteran** (USER.md §3): build HEAD-TO-HEAD table ≥10 trục:
   - Store scope (1 store vs 3 stores)
   - Daypart (sáng vs tối vs cả tuần)
   - Entry price
   - Cấu trúc (fixed vs tự chọn)
   - Margin protection (GP cố định vs add-on auto)
   - Baseline cov/tuần · Target cov/tuần
   - ΔRevenue/tuần · Contribution/tháng
   - Labor increment (sáng cần thêm vs tối đã trả → laborΔ≈0)
   - Execution risk (inventory riêng vs menu có sẵn)
   - Setup cost / ROI
4. **W29 LIVE SIGNAL:** nếu 1 promo đang chạy → so actual W29 vs baseline → 🔴 KILL / 🟢 KEEP / 🟢 PROOF. Dùng làm evidence quyết định.
5. **FBM VERDICT:** winner thắng bao nhiêu trục, tại sao. Gọi tên trục thua.
6. **3 OPTIONS cho Warren pick:**
   - A: Winner toàn bộ (⭐ REC thường)
   - B: Hybrid (winner chỗ này, loser chỗ kia)
   - C: A/B test song song 4 tuần
7. **UPDATE VAULT (Zone 🟡 — chờ Bố duyệt):**
   - Case THẮNG: thêm §Comparison (head-to-head + W29 signal + findings) + §Decision (option Bố chọn, 8 action items có owner/timeline) + LOG entry.
   - Case THUA: frontmatter `status: superseded` + `superseded_by: <winner file>` + `superseded_reason: <1 dòng data>`.
8. **Cross-check:** đảm bảo TODO của winner case reflect decision; loser case không còn active.

## 3. OUTPUT TEMPLATE
```markdown
## 🧑‍🍳 F&B DIRECTOR COMPARISON — <A> vs <B>
### Head-to-Head (≥10 trục)
| Trục | (A) | (B) | Winner |
| ... | ... | ... | **B** |
### W29 Live Data
| Store | Daypart | Baseline | W29 | Signal |
### FBM Verdict
<winner thắng N/M trục — lý do>
### 3 Options
| A | Winner toàn bộ | B | Hybrid | C | A/B test |
→ REC: <option>
```

## 4. PITFALLS
- ❌ Quên mark loser `superseded` → 2 case active conflict (cross-case hygiene).
- ❌ Dùng <4 tuần data mà không hỏi Bố.
- ❌ Không pull W29 live → bỏ evidence thực địa (Standee tối +24% là proof quan trọng).
- ❌ Thiếu source `[src: 09_Hourly W29]` trên mọi số.
- ❌ Tự patch vault không qua Bố duyệt (Zone 🟡).

## 5. BANNED
- ❌ Tiếng Anh trong output (trừ code/YAML/frontmatter).
- ❌ Bịa số không cite.
- ❌ Label "rẻ/cheap" trong tên (SOP_030).
