---
name: audit-token
description: "Token cost audit cho Warren — đọc runtime/cron/skills, trả top waste + savings."
type: skill
status: active
created: 2026-07-29
last_updated: 2026-07-29
tags: [ops, cost, token, audit, warren]
---

# audit-token — Token Cost Audit (Warren-friendly)

> **Mục tiêu:** Đọc data thực tế về skills, cron jobs, config → ra kết luận ngắn mà Warren đọc hiểu ngay: đâu tốn nhiều nhất, tiết kiệm được bao nhiêu, cần sửa gì.
> **Ngôn ngữ:** Tiếng Việt có dấu. Conclusion-first, bullet ngắn, không jargon.
> **SSOT:** `vault/.scripts/skills/audit-token/SKILL.md` (git-backed). Copy 1 chiều vào runtime khi deploy.

---

## Trigger

- Bố nói: `audit token`, `chạy token audit`, `token cost audit`, `kiểm tra token`, `tối ưu token`
- Hoặc GG tự động trong session khi cần đánh giá cost trước khi quyết định cron/skill change

---

## Input / Data đọc được

1. **Runtime config:** `config.yaml` + `.env` (đọc bằng `read_file`, KHÔNG dùng `search_files` dotfolder)
2. **Cron jobs:** `cronjob(action='list')` — đọc `model`, `provider`, `schedule`, `last_status`, `no_agent`
3. **Skills list:** `skills_list()` + `skill_view(name)` nếu cần infer kích thước/frequency
4. **Vault audit log:** `vault/10_OPERATION_DATA/token_audit_<YYYY-MM>.md` (nếu có) để compare month-over-month

> **Note:** Hermes hiện KHÔNG expose exact token count-by-skill API. Audit này dựa trên **inferred cost từ schedule + model** + kiểm tra config. Nếu Bố cần exact usage, export từ Hermes admin/insights page.

---

## Output Format (BẮT BUỘC)

### 1. Telegram-style report (đầu tiên, ngắn nhất)

```
🔶 TOKEN AUDIT | 2026-07
Tháng này: ~$X (ước tính) · so với tháng trước: ±Y%
1. Tiêu nhất: <tên cron/skill> (~$A) → giải pháp: ...
2. Tiêu hai: ...
3. Tiêu ba: ...

→ Tổng savings nếu apply hết: ~$Z/tháng (-P%)
→ Action: reply 'ok token' để GG apply safe changes
```

### 2. Vault file (lưu lại để reuse)

Ghi vào: `vault/10_OPERATION_DATA/token_audit_<YYYY-MM>.md`

```markdown
---
name: "Token Audit 2026-07"
type: "token_audit"
status: "active"
created: "2026-07-29"
last_updated: "2026-07-29"
---

# Token Audit — 2026-07

> **Source:** runtime config + cron list + skills list + Hermes insights inferred.
> **Disclaimer:** Exact token count cần export từ Hermes admin panel. Số liệu đây là ước tính受压at trên frequency/model, ±20%.

## Findings

| Rank | Target | Type | Est. monthly cost | Savings potential | Action |
|------|--------|------|-------------------|-------------------|--------|
| 1 | review-queue-watcher | cron LLM | ~$X | ~$Y (guard skip) | ... |
| 2 | col-weekly-mon | cron LLM | ~$X | ~$Y (reduce freq) | ... |
| 3 | weekly-ops-report-mon | cron LLM | ~$X | ~$Y (no_agent?) | ... |

## Recommendations

1. ...
2. ...

## Config Changes Proposed

| # | Change | Est. savings | Risk |
|---|--------|--------------|------|
| 1 | ... | ... | ... |

## Month-over-Month Compare

- 2026-07: ~$X
- 2026-06: ~$Y (nếu có file trước đó)
```

---

## Workflow

### Step 1 — Đọc runtime + cron + skills

- Đọc `config.yaml` để xem default model + providers.
- Chạy `cronjob(action='list')` để lấy tất cả jobs + model/provider/schedule.
- Chạy `skills_list()` để xem skills đang load.
- Đọc vault token audit tháng trước nếu có để compare.

### Step 2 — Phân loại cost

Phân loại jobs thành 3 nhóm:

| Group | Cost level | Xử lý |
|-------|------------|-------|
| **Agent cron LLM** (`no_agent=false`) | Cao | Ước tính theo frequency × model cost |
| **no_agent script** | 0 token | Bỏ qua, không tính |
| **Skills loaded mỗi turn** | Trung | Đếm số skills, infer context token cost |

### Step 3 — Tìm top 3 expensive skills

- Ước tính dựa trên: skills nào load mỗi turn × prompt length × frequency.
- Không có exact API → dùng heuristic: skills có linked references/scripts nhiều = lớn.
- Ghi rõ **ước tính**, không claim chính xác.

### Step 4 — Tìm top 3 expensive cron jobs

- Sort agent cron theo: `schedule frequency × model cost`.
- Ước tính:
  - `deepseek-v4-flash` ≈ $0.001/1K input, $0.002/1K output
  - 1 agent cron run ≈ 1K-5K tokens input + 1K-3K output
  - `*/30 7-17 * * 1` = ~20 runs/T2 ≈ ~$0.04-0.20/T2 ≈ ~$0.16-0.80/month
  - `15,45 6-17 * * *` = 24 runs/day × 7 = ~168 runs/week ≈ ~$0.67-3.36/week ≈ ~$2.7-13.4/month

### Step 5 — Kiểm tra auxiliary models + tool_search

- **Auxiliary models:** Kiểm tra xem có config nào set auxiliary model riêng không. Nếu có → kiểm tra có đang default về main model không.
- **tool_search:** Kiểm tra Hermes config xem `tool_search.auto` đang on/off. Nếu on → đề xuất tắt.

### Step 6 — Đề xuất cost reduction plan

Format:

```
1. <Action> → <Target> → <Est. savings> → <Risk>
2. ...
```

**Safe changes** (Warren có thể approve ngay):
- Thêm guard skip vào agent cron khi input không đổi
- Pin model rõ ràng cho từng cron
- Chuyển cron agent → no_agent nếu có script tương đương

**Cần đánh giá:**
- Giảm frequency cron
- Tắt skills không dùng

### Step 7 — Lưu audit + hỏi Warren

- Lưu report vào vault `token_audit_<YYYY-MM>.md`
- Dừng lại, hỏi Warren có muốn apply safe changes không.

---

## Constraints

- **KHÔNG tự động apply config change** — chỉ propose, chờ Bố approve.
- **KHÔNG claim exact token count** nếu không có data — dùng "ước tính" + "inferred".
- **KHÔNG đụng config.yaml trực tiếp** — dùng `hermes config set` nếu Bố approve.
- **KHÔNG đụng cron jobs.json trực tiếp** — dùng `cronjob(action='update')`.

---

## Skill Admin

- **Author:** Hermes (warren-profile)
- **Created:** 2026-07-29
- **Last updated:** 2026-07-29
