---
name: model-router
description: DeepSeek V4 Flash/Pro router — tự động routing giữa Flash (default) và Pro (khi cần), cost quota 10%, daily report, /model-router on/off/override commands.
domain: ops
type: skill
status: active
created: 2026-06-24
last_updated: 2026-06-24
tags: [deepseek, model-routing, cost-optimization, model-router]
scripts:
  router: scripts/router.py
  quota: scripts/quota.py
  commands: scripts/commands.py
commands:
  - command: /model-router on
    description: Bật model router (routing hoạt động bình thường)
  - command: /model-router off
    description: Tắt model router (all Flash, không routing)
  - command: /model-router override
    description: Nới quota limit từ 10% lên 20%
  - command: /model-router status
    description: Xem trạng thái router + quota
  - command: /model-router reset
    description: Reset quota counter về 0
---

# DeepSeek Model Router — Instructions cho Hermes

## Tổng quan

Skill này quyết định khi nào dùng **DeepSeek V4 Flash** (default, rẻ) vs **DeepSeek V4 Pro** (mạnh hơn, đắt hơn) cho mỗi response. Mục tiêu: ≥90% Flash, ≤10% Pro, Warren không cần nghĩ.

## RULES — Hermes PHẢI TUÂN THEO mọi turn

### Rule 1: Luôn bắt đầu với Flash

Config.yaml default là `deepseek-v4-flash`. Mọi request đều bắt đầu với Flash. **Chỉ dùng Pro khi có trigger.**

### Rule 2: Detect trigger để quyết định Pro

Dùng `python3 scripts/router.py decide "<task context>"` để kiểm tra. Pro khi:

1. **Tool-chain ≥ 3**: Task cần nhiều tool calls (search → read → analyze → synthesize)
2. **Factual accuracy cao**: Task query vào ops data (revenue, COL, CPH, P&L, doanh thu, số liệu, báo cáo)
3. **Flash failure fallback**: Flash response bị lỗi, sai số, Warren yêu cầu sửa → retry với Pro

**Cách detect:**
- `python3 scripts/router.py decide "<user_message>"` → đọc `model` field trong kết quả
- Nếu `model: "pro"` → xài Pro cho task này
- Nếu `model: "flash"` → respond bình thường với Flash

### Rule 3: Gọi Pro khi cần

Nếu router quyết định Pro:
1. Gọi Pro API: `echo "<prompt>" | python3 scripts/router.py pro-call`
2. Parse kết quả (field `content`)
3. Respond với nội dung từ Pro
4. **Gọi `python3 scripts/quota.py pro` để track**
5. Append tag `[🧠Pro]` ở cuối response

Nếu Flash: append tag `[⚡Flash]` ở cuối response. Gọi `python3 scripts/quota.py flash`.

### Rule 4: Kiểm tra quota trước khi xài Pro

Trước mỗi lần quyết định Pro:
- `python3 scripts/quota.py check` → đọc `can_use_pro`
- Nếu `can_use_pro: false` → **không được xài Pro**, dùng Flash + append cảnh báo: `[⚡Flash] ⚠️ <reason>`
- Luôn append tag ở cuối response (kể cả khi quota hit)

### Rule 5: Cảnh báo quota

- Khi `near_warning: true` (≥8%) → append: `[⚡Flash] ⚠️Pro:{pct}%/10%`
- Khi `hit_limit: true` → message: `⛔ Pro quota hit ({pct}%). Đã chặn Pro. Gõ /model-router override để tiếp tục.`
- Gọi `python3 scripts/quota.py report` cho 1-line summary

## Command Handlers

Khi Warren gõ:

| Command | Action |
|---------|--------|
| `/model-router on` | `python3 scripts/commands.py on` — bật routing |
| `/model-router off` | `python3 scripts/commands.py off` — tắt (all Flash) |
| `/model-router override` | `python3 scripts/commands.py override` — nới lên 20% |
| `/model-router status` | `python3 scripts/commands.py status` — hiển thị trạng thái |
| `/model-router reset` | `python3 scripts/commands.py reset` — reset counter |

## Daily Report

Inject vào morning brief mỗi ngày:

```python
python3 scripts/quota.py report
# Output: 📊 Model Router: 8% Pro (32/400 calls) | Quota: 10%
```

## Example Flow

```
Warren: "cho tôi số liệu COL của LU3 tuần này"

Hermes:
1. python3 scripts/router.py decide "cho tôi số liệu COL của LU3 tuần này"
   → model: "pro", trigger: "factual_accuracy"
2. Quota check: can_use_pro: true
3. echo "cho tôi số liệu COL của LU3 tuần này" | python3 scripts/router.py pro-call
   → content: "COL LU3 tuần này: ..."
4. python3 scripts/quota.py pro
5. Respond + [🧠Pro]
```

---

**Maintainer:** Hermes (warren-profile) | **Last updated:** 2026-06-24
