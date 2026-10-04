# Worked Case: hyperresearch → deep-research (2026-07-20)

## Bối cảnh
Warren trỏ `https://github.com/jordan-gibbs/hyperresearch` (1k★, "Agent-driven research
knowledge base", MIT) và hỏi: "explore cái này, xem có cài/steal cho existing using-agent-skills
được không".

## B1 — Runtime-lock check (KẾT QUẢ: LOCKED ❌)
Từ README:
- **Requirements:** Python 3.11+ **+ Claude Code** (bắt buộc).
- **Subagent roster:** 17 agents chạy trên Sonnet/Opus/Haiku (Anthropic, trả tiền).
- **Tool-locked allowlist:** patcher/polish bị lock `[Read, Edit]` ở mức Claude Code.
- **Skills:** gọi qua Claude Code `Skill` tool — không tồn tại trên Hermes.
→ Kết luận: install/steal code = ❌. Không vào được Hermes.

## B2 — Decision: Steal methodology ✅
Lấy TINH THẦN (không lấy code):
- "Patch, never regenerate" → khớp SOUL §5 Verify Gate (surgical edit).
- Cite-check (verify mỗi trích dẫn đúng nguồn) → khớp `verify-parser-output`.
- Independence audit (5 reprint = 1 source) → tránh ảo tưởng consensus.
- Source ranking (OpenAlex/Semantic Scholar) → hay cho vault research.

## B3 — Adapt cho free model
- Warren chọn **Nemotron free** (`nvidia/nemotron-3-nano-30b-a3b:free`).
- Chunk delegate_task ≤3 concurrent (bản gốc 17 trên Sonnet).
- Auto-fallback Medium (10 bước) nếu bị ban.
- Tradeoff stated: Nemotron yếu → báo cáo nông hơn benchmark gốc; bù bằng cite-check + 2 critic.

## Deliverable
Skill MỚI `deep-research` (Full 16-step port) vào `warren-profile/skills/deep-research/`:
- SKILL.md: pipeline 16 bước mapped sang tool Hermes, token `🔰 DR-STEP n/16`, model pin note,
  output `vault/_inbox/research/<slug>.md`, "Cách Bố dùng" cho non-IT.
- references/source-ranking.md, references/cite-check.md (chưa viết hết trong session).
- Build theo Warren Ops Workflow: spec → plan → incremental per-slice.

## Bài học đóng gói
Quy trình này generalize thành skill `external-repo-eval` — áp dụng mọi lần Warren trỏ repo ngoài.

## Ghi chú path (rút từ test thực tế 2026-07-20 — QUAN TRỌNG)
- Output bài research → `C:\Users\khoans\Documents\Warren_OS_Local\vault\_inbox\research\<slug>\...`
  (KHÔNG ghi vào `skills/deep-research/vault/` — vault thật nằm ngoài thư mục skills).
- Mọi path truyền vào `delegate_task` subagent = **absolute path đầy đủ**
  (`C:\Users\khoans\Documents\Warren_OS_Local\vault\...`). Subagent chạy context riêng,
  resolve `vault/` relative thành `C:\Users\khoans\vault\...` (SAI) → báo File not found.
- `execute_code` bị block trong cron mode → compute nhẹ dùng `terminal` + `python3`.
- 2 lỗi trên đã encode vào SKILL.md §Pitfalls (P1 = skill-folder write, P2 = delegate path).
