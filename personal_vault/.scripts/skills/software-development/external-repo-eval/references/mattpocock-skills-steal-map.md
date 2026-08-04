---
name: mattpocock-skills-steal-map
type: reference
source: https://github.com/mattpocock/skills (182k★, MIT, Claude Code/Codex plugin — runtime-locked, steal methodology only)
date: 2026-07-22
---

# Steal-map: mattpocock/skills → warren-profile

Condensed from repo research + independent critic review (reviewer-node). Dùng bởi `external-repo-eval` B2 decision.

## Runtime verdict
Claude Code / Codex plugin (`.claude-plugin`, `CLAUDE.md`, `agents/openai.yaml`). NO MCP, NO pip. → Code gốc KHÔNG chạy trên Hermes. Steal methodology, viết lại bằng tool Hermes.

## 4 failure modes → skill fix (core)
| Failure | Repo skill | Steal? |
|---|---|---|
| Misalignment | `grilling`/`grill-me` | ✅ 1-Q-at-a-time + recommended answer + tự-tra-fact + chỉ hỏi decision + không act tới shared understanding |
| Verbosity | `CONTEXT.md` glossary | ⚠️ Warren đã có USER/WARREN_MEMORY/ANCHORS → skip |
| Code broken | `tdd` | ✅ red-green, test tại seam, anti-patterns (implementation-coupled/tautological/horizontal-slicing) → khớp `verify-parser-output` |
| Ball of mud | `to-spec`→`to-tickets` + `improve-codebase-architecture` | ✅ vertical tracer-bullet slices + blocking edges; wide-refactor = expand-contract |

## Viên ngọc: `writing-great-skills` (standalone reference skill, `disable-model-invocation: true`)
- Predictability = root virtue (process giống nhau mỗi run, không phải output).
- Information hierarchy ladder: in-skill step (completion criterion — checkable+exhaustive, chống premature completion) > in-skill ref > external ref (progressive disclosure).
- Split by invocation (leading word) / by sequence (ẩn post-completion steps chống vội).
- Leading words: recruit pretrained priors, ít token.
- Pruning: SSOT; no-op test (xóa câu model đã obey by default).
- 6 failure modes: premature completion, duplication, sediment, sprawl, no-op, **negation** (state positive; KEEP prohibition chỉ khi là hard guardrail không thể nói positive).
- → TẠO RIÊNG `writing-great-skills`, KHÔNG absorb vào `hermes-agent-skill-authoring` (khác concern: design-quality vs mechanical packaging).

## 3 high-ROI steals thường BỊ BỎ SÓT
1. **Router section** (trong `using-agent-skills` — mục "Ask Hermes — Warren Router") — khi user-invoked skills (>9) quá tải cognitive load. Liệt kê + route. Steal giá trị NHẤT. (Đã gộp từ `ask-hermes` cũ 2026-07-24.)
2. **`improve-codebase-architecture`** — deletion-test + scope-before-scan (YAGNI) + git-log hotspots → áp THẲNG vào vault parser pipeline (`vault-parser-hygiene`).
3. **`diagnosing-bugs`** — root-cause (reproduce→bisect→hypothesis→fix at seam). Port được vào debug parser.

## Negation rule (QUAN TRỌNG — áp cho ANCHORS/SOUL)
Chuyển "KHÔNG được/NEVER" → positive CHỈ với guidance prose thường. VỚI frozen guardrail (vd `raw/` READ-ONLY): GIỮ cấm + **pair** với câu positive + trigger. Trên hy3:free, câu cấm chặn chắc hơn câu tích cực. → REJECT sweep toàn bộ ANCHORS/SOUL.

## Free-model fit
Nguyên tắc phải encode thành **structural artifact** (checklist/gate), KHÔNG đoạn văn dài. Absorb-everything → skill dài → context nặng → truncation. Dùng progressive disclosure.
