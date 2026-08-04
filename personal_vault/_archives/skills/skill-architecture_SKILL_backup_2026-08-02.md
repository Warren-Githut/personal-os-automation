---
name: skill-architecture
description: "Decision framework for Hermes skill architecture — single vs loop vs graph vs reviewer node. Bố's 1-câu checklist + 3-câu interview-me. Use when designing a new skill/automation/workflow, or auditing existing ones for structural fit."
version: "0.1.0"
category: devops
tags: ['architecture', 'skill', 'design', 'graph', 'pattern']
related_skills: [deep-research, ops-weekly-report]
---

# Skill Architecture — Single vs Loop vs Graph

> Bố dạy 2026-07-21. Dùng khi thiết kế skill mới hoặc audit skill hiện có.

## Checklist 1 câu (mở đầu)

> **"Task này có cần 2+ người làm CÙNG LÚC không?"**

- **Không** → 1 skill đơn lẻ + reviewer node ✅
- **Có** → graph mode (spawn nhiều subagent song song)

**95% task của Bố rơi vào "Không".** Graph mode chỉ cần khi: parse 3 store cùng lúc, research 5 nguồn song song, hoặc cần 1 người viết + 1 người review chạy đồng thời.

## 3 câu interview-me (30 giây)

Khi Bố thấy 1 quy trình mới, tự hỏi:

| # | Câu hỏi | Nếu YES → | Nếu NO → |
|---|---------|-----------|----------|
| 1 | "Xong task này trong **1 lần chat** với Hermes được không?" | 1 skill đơn lẻ | Tách ra nhiều bước |
| 2 | "Có bước nào **phải đợi** bước khác xong mới làm được không?" | Loop (tuần tự) | Graph (song song) |
| 3 | "Có cần **người thứ 2 kiểm tra** output không?" | Thêm reviewer node | Không cần |

**Luôn bắt đầu từ đơn giản nhất:** 1 skill → nếu chậm thì loop → nếu vẫn chậm thì graph. Đừng graph trước khi loop chạy ổn.

## Quy tắc vàng

```
Skill đơn lẻ (90%) → Loop (8%) → Graph (2%)
     ↑                              ↑
  Hầu hết task               Chỉ khi thực sự cần
  của Bố nằm đây             parallel processing
```

**Nếu nghi ngờ → làm skill đơn lẻ trước. Mọi thứ khác là tối ưu hóa sau.**

## Procedure — Audit 1 skill hiện có

```
1. Checklist 1 câu → xác định form chuẩn
2. 3 câu interview-me → verify từng câu
3. Nếu hiện tại khác form chuẩn → flag "cần đổi?"
4. Kết luận: Keep / Refactor / Add reviewer
```

## Integration với skill khác

- **`subagent-pattern`** — quyết định từng bước dùng `delegate_task` hay inline (SAU KHI đã chọn cấu trúc skill).
- **`using-agent-skills`** — skill discovery + creation pipeline (dùng TRƯỚC KHI thiết kế skill mới).

## Ví dụ áp dụng (2026-07-21)

| Skill | Checklist 1 câu | Kết quả |
|-------|----------------|---------|
| `deep-research` (16-step) | Cần 2+ người cùng lúc? Có — nhưng đã parallel ở các bước cần | ✅ Single skill + internal sub-agent parallel |
| `using-agent-skills` | Cần 2+ người cùng lúc? Không — lookup table | ✅ Single skill |
| `ops-weekly-report` (3 store) | Cần 2+ người cùng lúc? Có — parse 3 store song song | Graph (spawn 3 parser) |
