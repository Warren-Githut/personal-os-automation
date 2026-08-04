---
name: infrastructure-adoption-eval
description: "Use when Warren evaluates cloud or tool adoption."
category: ops
tags: ['infrastructure', 'cloud', 'evaluation', 'adoption', 'non-it']
version: 1.0.0
trigger: Warren says "có nên xài", "có nên move", "should we use", "có nên chuyển qua", or asks to evaluate any infrastructure/tool/cloud/platform decision
related_skills: [explore, doubt-driven-development]
---

# /infrastructure-adoption-eval — Infrastructure & Tool Adoption Evaluation

> Dành cho non-IT ops leader (Warren/Bố). Khi Bố hỏi "có nên xài cloud X không?" — GG làm framework.

Khác với `explore` (ops-data feasibility), skill này tập trung vào **đánh giá hạ tầng/công nghệ**.

---

## Process

### Phase 1: Workload Profile

Trước khi so sánh option mới, phải hiểu những gì đang chạy:

1. **List all running services** — cron jobs, scripts, bot, VPN
2. **Classify workload:**
   - `no_agent` script (0 token) → siêu nhẹ
   - LLM-driven → laptop chỉ relay HTTP
   - Heavy compute → *nếu không có thì ghi rõ*
3. **Measure:** dung lượng code (MB), số scripts, tần suất, phụ thuộc network (VPN SQL, GSheet, Telegram API)
4. **Identify REAL pain point** — không "cloud hay hơn" mà "cái gì đang khó?"

### Phase 2: Constraint Mapping

| Constraint | Why matters |
|------------|-------------|
| **VPN / On-prem access** | SQL IKKO latency nếu cloud xa LAN |
| **Windows path hardcode** | Linux cloud cần sửa |
| **GUI dependency** | Hermes Desktop vs CLI chat |
| **24/7 requirement** | Bot live? Cron đêm? |
| **Maintenance** | Ai update OS? Bố non-IT |

### Phase 3: Option Analysis

| Dimension | Câu hỏi |
|-----------|---------|
| **Chi phí thực** | Renewal price, intro không tính |
| **Migration cost** | Giờ công sửa code + test |
| **Risk** | Lock-in? Security? |
| **Non-IT friendly** | Bố tự debug được? |

### Phase 4: Verdict (non-IT)

```
## 🎯 Kết Luận

**Hiện tại: [giữ/chuyển] là [đúng/sai].**

| Option | Tháng | Lợi | Hại | Verdict |
|--------|-------|-----|-----|---------|
| Local | 0₫ | ... | ... | ✅/❌ |
| Cloud X | ~...₫ | ... | ... | 🟡/✅/❌ |

## Robot Vacuum Test
GG ở cloud, Bố không laptop → mất gì?

## Blocker thật sự
[cái chặn option tốt nhất]
```

---

## Pitfalls

- **Đừng recommend cloud chỉ vì "cloud tốt hơn".** Phải có pain point thật.
- **Non-IT language:** không Docker/K8s/kubectl. GG làm, không giải thích.
- **Migration cost ẩn:** sửa Windows path, debug VPN → 5-10h.
- **VPN on-prem = blocker số 1.** Data center châu Âu ping L'Usine LAN có thể fail.
- **Hybrid trap:** Cloud cho cron+bot, local cho chat → 2 hệ thống lằng nhằng.
- **"Phí điện" rẻ hơn VPS:** laptop ~54.000₫/th.
- **Robot vacuum test:** hình dung GG sống 100% cloud, Bố 0 laptop — còn được gì?
