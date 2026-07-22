---
name: reviewer-node
description: "Independent reviewer subagent cho Hermes output — spawn bằng delegate_task với context sạch, checklist chuẩn, trả PASS/FAIL + list lỗi. Dùng sau mọi major output personal (health summary, finance review, legal timeline, dashboard)."
version: 1.0.0
author: Hermes
trigger: "manual — gọi sau major output"
category: core
tags: ['review', 'subagent', 'quality', 'gate']
related_skills: [personal-morning-brief, personal-weekly-connections]
---

# Reviewer Node — Independent Audit Subagent

> **Purpose:** Spawn 1 subagent với FRESH EYES để review Hermes output. Reviewer KHÔNG thấy raw data/context của Hermes → review thật, không rubber-stamp.
>
> **Model:** KHÔNG pin ở đây. Khi gọi qua `auto-reviewer`, model được inherit từ chat (free model, theo directive Warren 2026-07-22). Nếu gọi tay độc lập, vẫn DÙNG free model — KHÔNG set `model`/`provider` trong frontmatter này.

---

## Khi nào gọi

Sau MỌI major output của Hermes:
- Health summary (sleep/weight/BP trend)
- Finance review cá nhân (budget, burn, emergency fund)
- Legal timeline (ly hôn, access GG)
- Weekly personal digest / dashboard
- Parser output (verify-parser-output làm trước → reviewer-node review tổng thể)

**Không gọi cho:** task nhỏ (≤2 tool calls), chat thông thường, câu hỏi đơn giản.

---

## Cách gọi (orchestrator pattern)

Hermes spawn reviewer qua `delegate_task`:

```
delegate_task(
    goal="Review output bên dưới. Trả PASS hoặc FAIL + list lỗi cụ thể.",
    context="""### OUTPUT CẦN REVIEW:
{output}

### CHECKLIST (chi tiết tại bảng 5 trục bên dưới — áp dụng từng trục)
1. SỐ LIỆU: Tất cả số có cite source/log không? (sleep hours, weight, money)
2. FORMAT: Đơn vị rõ (kg, giờ, VND)? So sánh trend > snapshot?
3. LOGIC: Kết luận có supported bởi data? Có nhảy quá xa không?
4. CONSISTENCY: Có vi phạm ANCHORS.md? (vd: tự chuẩn đoán y tế, đưa stock vào personal, spam)
5. COMPLETENESS: Đủ góc? (Health/Finance/Family/Legal). Thiếu tradeoff nếu khuyên tài chính?

### ANCHORS (FROZEN - đọc kỹ):
{anchors_summary}

### FORMAT TRẢ LỜI (reviewer subagent CHỈ trả nội dung review, KHÔNG tự in token):
PASS hoặc FAIL
Nếu FAIL → list từng lỗi: [LOẠI] Mô tả + vị trí cụ thể
Nếu PASS → ghi "PASS — [lý do ngắn]"
"""
)
```

---

## Checklist chuẩn (5 trục — PERSONAL domain)

| # | Trục | Câu hỏi |
|---|------|---------|
| 1 | **Số liệu / Source** | Tất cả số (sleep hrs, weight, money, %) cite source/log? `[HIGH]`/`[MOD]`/`[LOW]` đúng? Số nào không cite → flag. |
| 2 | **Format / Unit** | Đơn vị rõ (kg, giờ, VND triệu)? Trend ≥2 tuần (A9) hay snapshot 1 ngày? |
| 3 | **Logic / Advice** | Khuyến nghị có tradeoff (A4 finance)? Có tự chuẩn đoán y tế (A2)? Có evidence hay chỉ opinion? |
| 4 | **Consistency / ANCHORS** | Vi phạm ANCHORS.md? (vd: chẩn đoán bệnh = A2; đưa ticker P/E vào health = A7; spam nhắc = A6; thiếu tradeoff tài chính = A4) |
| 5 | **Completeness** | Đủ góc relevant? (Health/Finance/Family/Legal). Legal có BATNA/timeline (A8)? Family (GG) chỉ khi Bố đề cập (A3)? |

---

## Output format

> ⚠️ **Reviewer subagent KHÔNG tự in token `🔍 REVIEWER:`** — chỉ trả nội dung review (PASS/FAIL + findings). Token `🔍 REVIEWER: ...` do Hermes (orchestrator) in DUY NHẤT sau khi có verdict, theo định dạng chuẩn của `auto-reviewer`. Đây là để tránh mismatch token format (C1).

```
[Danh sách findings nếu FAIL]:
- [SỐ LIỆU] Dòng X không cite source/log
- [LOGIC] Khuyên thuốc/statin mà không bảo "xem bác sĩ" (vi phạm A2)
- [CONSISTENCY] Mâu thuẫn A7: đưa phân tích cổ phiếu vào health summary
- [CONSISTENCY] Mâu thuẫn A4: khuyên chi lớn không tính emergency fund = 0

[PASS reason nếu PASS]:
PASS — Số cite đủ, không chẩn đoán, tradeoff có, domain đúng.
```

---

## Rules

1. **Context sạch:** Reviewer CHỈ thấy output + checklist + anchors. KHÔNG thấy raw data, transcript, hay context của Hermes.
2. **Không sửa:** Reviewer chỉ flag lỗi — không tự sửa. Hermes (orchestrator) sửa.
3. **Max 2 vòng + HARD BLOCK:** Nếu FAIL → Hermes sửa → gọi reviewer lại. Nếu FAIL lần 2 → **KHÔNG deliver artifact**, chỉ gửi 2 reviews + `🔰 SAFENET: 🔴 BLOCKED` + `🔍 REVIEWER: 🔴 FAIL [2] — escalated, BLOCKED pending Bố`. Cần Bố override tường minh mới deliver.
4. **PASS không có nghĩa perfect:** PASS = không lỗi checklist. Có thể có improvement suggestions (note riêng).
5. **Model:** KHÔNG pin. Dùng free model kế thừa từ chat (qua auto-reviewer). Nếu quality kém → báo Bố, KHÔNG tự set model cứng.

---

## Integration points

- `personal-morning-brief` → gọi sau khi viết brief
- `personal-weekly-connections` → gọi sau khi viết synthesis
- parser output → gọi sau verify-parser-output (layer 2)
- Bất kỳ report cá nhân gửi Bố → gọi trước khi gửi

---

## Pitfalls

- **Reviewer quá dễ tính:** Nếu reviewer PASS 100% các lần → checklist quá yếu hoặc model quá yếu. Flag để điều chỉnh.
- **Reviewer quá khó:** Nếu reviewer FAIL mọi thứ với lỗi nhỏ → checklist quá strict. Điều chỉnh threshold.
- **Context quá dài:** Output >5000 từ → tóm tắt trước khi gửi reviewer (reviewer model rẻ, context nhỏ).
