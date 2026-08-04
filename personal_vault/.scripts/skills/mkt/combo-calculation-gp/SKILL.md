---
name: combo-calculation-gp
description: "Evening Dinner Combo (entry 199k) cho L'Usine — starter + main khách tự chọn, add-on cân bằng GP theo công thức Warren 2026-07-19. Dùng khi Bố hỏi tính GP combo / add-on / review menu evening. SSOT cost = Recipe_Index.json."
version: 1.0.0
tags: [lusine, combo, evening, pricing, gp, add-on, mkt]
related_skills: [ops-mkt-manager-os, promo-eval]
---

# combo-calculation-gp — Evening Dinner Combo Pricing Rule

> **Mục đích:** Tính GP + quyết định add-on cho Evening Dinner Combo L'Usine.
> **Scope:** 3 stores (LU3/LU5/LU7) × T2–CN, 17–21h. Entry price **199k** (confirmed Warren 2026-07-19).
> **SSOT cost:** `30_KNOWLEDGE_BASE/wiki/08_menu_cogs/Recipe_Index.json` (cost_total thật, compute bằng Python).

## 1. Cấu trúc combo (khách tự chọn)
- **Starter (chọn 1):** ½ Crispy Chicken Salad | ½ Vegan Buddha Bowl | Pumpkin Soup (full)
  - Mix cost starter ≈ **23k** (½ salad ~22.5–23k; Pumpkin Soup full 24k). Dùng 23k làm chuẩn.
- **Main (chọn 1 từ 6 món duyệt):**
  1. Carbonara Pasta (pasta)
  2. Squid Ink Pasta with Crab (pasta)
  3. Crispy Butter Milk Chicken Burger (burger)
  4. Cheese Bomb Sandwich (burger/sandwich)
  5. Beef Kimchi Fried Rice (kimchi rice)
  6. Crispy Skin Salmon (protein/cá hồi)

## 2. Công thức (Warren teach 2026-07-19)
```
BASE = 199000
starter_cost = 23000   # mix, dùng khi không parse exact
combo_cost = starter_cost + main_cost
GP@199k = (BASE - combo_cost) / BASE * 100

if GP@199k >= 60:   PASS  → KHÔNG bắt add-on (cover fixed cost OK)
else:               # GP < 60
    P_target = combo_cost / 0.4        # giá để GP = 60%
    add_on   = P_target - BASE         # khách đã trả 199k → trả thêm
```

## 3. Ma trận thực tế (cost từ Recipe_Index.json, 2026-07-19)
| Main | combo cost | GP@199k | Action |
|------|:---:|:---:|--------|
| Carbonara Pasta | 70.4k | 64.6% | PASS |
| Beef Kimchi Fried Rice | 78.8k | 60.4% | PASS |
| Crispy Butter Milk Chicken Burger | 81.7k | 58.9% | ADD-ON +5.3k |
| Squid Ink Pasta w/ Crab | 86.4k | 56.6% | ADD-ON +16.9k |
| Cheese Bomb Sandwich | 90.7k | 54.4% | ADD-ON +27.9k |
| Crispy Skin Salmon | 144.1k | 27.6% | ADD-ON +161.1k |

> Starter exact: ½CrispyChickenSalad=22.5k, ½VeganBuddha=22.9k, PumpkinSoup=24k. Nếu khách chọn starter khác 23k chuẩn → recompute combo_cost = starter_exact + main_cost.

## 4. Quy tắc vận hành (bắt buộc)
- **Ngưỡng duy nhất = 60% GP.** KHÔNG ép 70%. Mục tiêu = volume cover fixed cost (tối trống labor đã trả, COL T2–T6 🔴 21–28%).
- **Add-on chỉ kích hoạt khi GP@199k < 60%.** FOH gợi ý (không ép) khách trả thêm để GP=60%.
- **Add-on là công cụ cân bằng margin, KHÔNG phải upsell tự do.** Beverage (GP 83%+) kéo GP yếu vs đồ ăn đắt — ưu tiên add-on = main đắt (salmon) thay beverage.
- **Không giới hạn main cứng** — khách tự do chọn, add-on tự động bảo vệ. 6 main trên = gợi ý menu board.
- **Tracking:** đo food GP thực tế mỗi tuần → nếu avg <55% quá sâu → thu hẹp main list.

## 5. Khi Bố hỏi "tính GP combo X" / "add-on món Y bao nhiêu"
1. Load Recipe_Index.json → lấy cost_total main + starter.
2. Chạy công thức §2.
3. Trả bảng: combo_cost, GP@199k, PASS hoặc ADD-ON +Xk (P_target).
4. Cite `[src: Recipe_Index.json]`.

## 7. ROI-B (Contribution) — tính step-by-step
Mục tiêu: đo tiền LÃI THỰC TẾ promo mang về (sau giá vốn + labor thêm).
- CM (Contribution Margin) food L'Usine ~73% (từ `14_Menu_GP`).
- Labor tối T2–T6 ĐÃ trả (COL 🔴 21–28% W28) → thêm covers tối = **laborΔ = 0**.
- Công thức: `NetContrib = ΔRev × 73% − 0`.
- Script: `scripts/combo_gp_calc.py` (parse 09_Hourly 17-21h toàn tuần, output base/uplift/Δ cov + rev + AC + NetContrib).

## 8. Terminology (Bố quy định 2026-07-19)
- **AC = Average Check** (KHÔNG dùng "RC" = Rev/Cover). Mọi báo cáo dùng AC.
- Baseline tính **TOÀN TUẦN (T2–CN)**, không chỉ weekday.
- Revenue列: BaseRev / UplRev / ΔRev (tương đối) — KHÔNG chỉ covers.

## 9. BANNED
- ❌ Dùng giá 195k (đã đổi 199k).
- ❌ Ép GP 70% (ngưỡng 60%).
- ❌ Dùng "RC" (dùng "AC").
- ❌ Baseline chỉ weekday (phải T2–CN).
- ❌ Bịa cost (parse Recipe_Index.json).
- ❌ Framing "rẻ" (SOP_030: "Bắt đầu tối từ 199k").
