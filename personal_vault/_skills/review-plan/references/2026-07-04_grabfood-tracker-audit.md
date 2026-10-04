# GrabFood Tracker Audit — 2026-07-04

**Skill context:** Operational File Completeness Audit (§3 of review-plan SKILL.md)
**File reviewed:** `30_KNOWLEDGE_BASE/wiki/06_lusine_operations/GrabFood_Rolling_Tracker.md`
**Prompt:** "bạn là 1 fbm có 30 năm kinh nghiệm. HÃY xem file này... bạn nghĩ đã đủ thông tin cho hermes grep-able/searchable, đầy đủ thông tin để herme có thể đưa ra giải pháp/phân tích/actionables để tăng doanh thu chưa, và thân thiện cho Warren nhìn vô thấy số là hiểu, và dễ dàng ra quyết định chưa?"

## Raw Output (first pass)

| Dimension | Score | Finding |
|-----------|:-----:|---------|
| Hermes grep-able/searchable | 7/10 | Missing product mix, margin fields |
| Hermes phân tích/actionable | 5/10 | Only "resume ads" — not specific enough |
| Warren nhìn hiểu ngay | 7/10 | VND numbers too long; missing % WoW |
| Dễ ra quyết định | 5/10 | Knows *what* to do, not *how* |

## 7 Gaps Identified

1. **Margin depth** — no food cost/packaging/labor per order
2. **Product mix** — no best sellers, category split
3. **Delivery ops** — no prep time, cancellations, ratings trend
4. **Competitive context** — no ranking, competitor pricing
5. **LU7 coverage** — file said "excluded" but actually active
6. **Data recency** — last updated June 5, June data missing
7. **Format** — long VND, no % WoW, English-only

## Warren's Corrections Applied

| Gap | Warren said | Action |
|-----|-------------|--------|
| 1 (margin) | "Chưa cần lúc này" | Left out; noted COGS available in 10_OPERATION_DATA |
| 2 (product mix) | "Tôi gửi best seller CSV" | Parsed CSV → added Best Seller section |
| 3 (delivery ops) | "Ignore cái này" | Removed from scope |
| 4 (competitive) | "Để trống, tương lai sẽ fill" | Noted as future gap |
| 5 (LU7) | "Đã mở Grabfood được 2 tuần" | Updated status + commission 24.5% |
| 6 (recency) | "Tôi sẽ gửi trong hôm nay" | Used weekly log for June data |
| 7 (format) | "Approved; chuyển qua tiếng Việt" | Applied M format, % WoW, full Vietnamese |

## Key Data Discovered from CSV

**LU3 (662 đơn):** Beef Kimchi Fried Rice #1 (57đ, 8.6%), Food 54%/Drinks 20%/Sides 26%
**LU5 (518 đơn):** Grilled Chicken Wrap áp đảo (80đ, 15.4%), Food 61%/Drinks 17%/Sides 21%
**LU7 (6 đơn):** Quá mới, Crispy Buttermilk Chicken Burger (3đ)

## File Rewrite Applied

- Title expanded to "Tháng 5 & 6/2026"
- June KPI table added (180 orders system, 66.0M gross)
- Best Seller section with top 10 per store
- Weekly trend table: WoW column, M format, LU7 column
- All Vietnamese with diacritics
- Updated actions specific to budget per store
