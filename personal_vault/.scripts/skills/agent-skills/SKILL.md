---
name: apply-agent-skills
description: "Lightweight gateway skill: load Agent Skills discipline ONLY for engineering artifacts (parsers, scripts, schema). Keep ops workflow untouched."
category: devops
tags: [agent, gateway, discipline, skill]
related_skills: [using-agent-skills]
---

# apply-agent-skills

## Purpose
Apply Agent Skills discipline only on engineering artifacts:
- parsers
- scripts
- schema changes

Do NOT apply this to ops workflow under any circumstances.

## Rules
1. Scope = engineering artifacts ONLY.
2. Ops workflow = untouched and final.
3. Use this skill only when authoring or revising parser code, automation scripts, schemas, or related tests.
4. Disable / do not invoke for routine ops tasks: COL, CPH, case handling, briefings, daily reports.

## Pitfalls (learned 2026-07-27)

- **P-AUTOGEN-OVERWRITE:** When debugging a parser/auto-gen pipeline, luôn check xem file output có bị 1 cron/process KHÁC overwrite không. Nếu có → **sửa source generator, KHÔNG patch output thủ công**. Bài học: `TODAY.md` bị `gen_today.py` ghi đè mỗi 09:00; sửa tay section COL 26/07 → mất sau 1 lần chạy. Fix đúng = thêm `_build_col_latest_section()` vào `gen_today.py`. Quy tắc: output bị overwrite định kỳ = tìm generator, sửa ở đó.
- **P-DOUBLE-CONSUMER:** 2 process cùng poll 1 Telegram bot token (aiogram live bot + getUpdates cron) → Telegram giao mỗi msg cho 1 consumer → queue entry dễ bị ghi đè mất. Fix = `filelock` bao quanh load→append→save + id dùng microsecond. Khi debug "mất message/tin nhắn không vào queue" → check có 2 consumer cùng token không.
- **P-COL-COLUMN-INDEX:** `07_COL_Weekly_Log` GSheet có column index CỐ ĐỊNH (date=A, store=C, rev_net=D, COL%=Z(26), Status=AL(38), Cover=AR(44)). Đọc/sửa bằng index, KHÔNG quét heuristic → sai index = covers/COL% lệch (vd 19.5M thay 169).
