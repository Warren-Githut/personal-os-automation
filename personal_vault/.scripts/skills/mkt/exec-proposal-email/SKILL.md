---
name: exec-proposal-email
description: "Draft boss-facing executive proposal emails for Warren (L'Usine) về quyết định promo/initiative. Hard rules: NO em-dash, simple English, humanized, PROPOSAL (có recommendation + tables) KHÔNG chỉ inform, daypart 'Monday to Sunday' (T2-CN=Monday-Sunday, KHÔNG Tuesday), PHẢI có margin-protection section nếu promo có add-on. Export CSV khi Bố yêu cầu."
version: 1.0.0
tags: [email, proposal, executive, boss, warren, promo, lusine]
category: mkt
related_skills: [promo-eval, combo-calculation-gp, ops-mkt-manager-os, promo-comparison]
---

# exec-proposal-email — Boss-Facing Executive Proposal (Warren)

> **Mục đích:** Khi Warren nhờ draft email gửi sếp (boss) về một quyết định promo/initiative → sinh email dạng PROPOSAL kèm bảng tính, chuẩn format Warren duyệt 2026-07-22.
> **Scope:** Email business proposal (inform + recommend), KHÔNG customer blast, KHÔNG creative copy.

## 1. HARD FORMAT RULES (Warren 2026-07-22)

| # | Rule | Note |
|:--:|:---|:---|
| 1 | ❌ **KHÔNG em-dash (—)** | Warren: "ko em dash". Dùng period / comma / colon. |
| 2 | **Simple English, humanized** | "contribution margin" → "contribution". Không jargon, không consultant-speak. |
| 3 | **PROPOSAL, không inform** | Warren: "cần con propose, cùng với những bảng tính". PHẢI có recommendation rõ + tables. Chỉ inform = sai. |
| 4 | Daypart = **"Monday to Sunday"** | T2-CN = Thứ 2–CN = **Monday–Sunday (7 ngày)**. ❌ "Tuesday to Sunday" (T2 = Monday, con từng ghi sai → Warren bẻ lại). |
| 5 | **PHẢI có margin-protection** | Nếu promo có add-on/combo → bảng cost / GP / action. Warren phải nhắc 2026-07-22 → đừng quên. |
| 6 | Baseline "toàn tuần (T2–CN)" ĐÃ có Monday | Đổi label tiếng Anh KHÔNG đổi số. Verify line-by-line trước recompute. |

## 2. STRUCTURE (template)

1. **Subject:** Proposal: <tên promo/initiative>
2. **The idea** — giá, cấu trúc, daypart, loyalty perk
3. **Why now** — labor đã trả / test data / kill component yếu
4. **The math** — bảng per-store (BaseCov → UplCov → ΔCov → ΔRev) + tổng hệ thống
5. **Margin protection** — add-on table (bắt buộc nếu có) — giải thích ngắn gọn cách bảo vệ margin
6. **What it costs us** — POSM / setup, no extra labor
7. **Timeline** — W30 / W31 / W32 (hoặc tương đương)
8. **Recommendation** — approve + cam kết watch metric
9. **Closing humanized** — "Happy to adjust before we print. Best, Warren"

## 3. EXPORT (khi Bố yêu cầu file)

- Bố nói "export csv / notepad csv" → ghi `_inbox/YYYY-MM-DD_<promo>-proposal.csv` (UTF-8, Notepad/Excel đọc được).
- CSV PHẢI chứa: email body sections + bảng tính + bảng add-on (nếu có).
- Không git commit tự động (zone 🟢 output, Bố duyệt).

## 4. TEMPLATE ĐẦY ĐỦ

> Xem `references/exec_email_boss_template.md` (Golden Hour Dinner example, Warren duyệt 2026-07-22).

## 5. PITFALLS

- **Em-dash leak:** Model thường tự chèn "—" khi viết English. Quét kỹ trước trả kết quả. Dùng ":", ".", ",".
- **Inform-only:** Đừng chỉ tóm tắt. Warren muốn đề xuất + số để sếp duyệt 1 nốt.
- **T2 translation:** Tiếng Việt "T2" = Monday. Model dịch "T2" = Tuesday là sai phổ biến. Luôn "Monday to Sunday".
- **Quên add-on:** Margin protection là phần Warren để ý. Thiếu = Warren phải nhắc (mất điểm).
- **Số đổi khi chỉ đổi label:** Đổi "Tuesday" → "Monday" KHÔNG làm số baseline thay đổi (vì data gốc đã 7 ngày). Đừng tính lại lung tung — verify line-by-line rồi giữ nguyên.

## 6. BANNED

- ❌ Em-dash (—) trong output.
- ❌ Chỉ inform, không propose.
- ❌ "Tuesday to Sunday" (phải Monday to Sunday).
- ❌ Thiếu bảng tính / thiếu margin-protection (nếu promo có add-on).
- ❌ Jargon ("contribution margin", "uplift", "incremental") không paraphrase.
