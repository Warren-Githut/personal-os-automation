# QA Swarm Pattern (build → verify → fix → re-verify), 2026-07-22

Dùng khi ship một skill/artifact và Warren muốn full QA trước push. Đã chạy thành công trên review-gate build.

## Cấu trúc: 2 batch song song (max 3/subagent), read-only analysis, main agent giữ quyền fix.

```
BUILD (inline): tạo/sửa skill(s) + safenet route.

BATCH A (3 subagents, parallel) — read-only QA:
  1. battle-test    — 5 adversarial situations, chấm 0-100
  2. code-review    — 5-axis (correctness/readability/arch/security/perf) + severity labels
  3. debugging      — triage latent instruction bugs, root-cause + guard recs

BATCH B (2 subagents, parallel) — read-only QA:
  4. ab-test        — variant A (built) vs variant B (simpler alt), recommend winner
  5. code-simplify  — behavior-preserving opportunities

MAIN AGENT (sau cả 2 batch):
  - VERIFY MỌI FINDING TRÊN DISK (read_file / grep) — subagent output là suggestion, KHÔNG phải truth
  - Aggregate → trình Critical/Major cho Warren → Warren duyệt fix batch
  - PATCH incremental, verify từng file sau patch (drift grep, structural checks)
  - RE-RUN battle-test subagent trên bản FIXED → confirm score ≥ target (vd 85/100)
  - Chỉ sau đó: backup _archives/skills/ + Commit-Push Self-Gate
```

## Tại sao 2 batch không 1 batch 5
`delegate_task` giới hạn 3/subagent. Chia 2 batch giữ mỗi batch trong limit và cho Batch B chạy song song với Batch A.

## Verify-on-disk rule (HARD)
Subagents amnesiac, hay over-claim. Trước khi apply BẤT KỲ fix nào: `read_file`/`grep` exact file:line họ cite.
- Session example: subagent claim `insight-checklist` skill missing → main agent grep CONFIRM là dead ref.
- Khác: claim model-hardcode → `read_file` reviewer-node L9-10 CONFIRM.
→ Trust disk, not transcript.

## Re-run không optional
Sau fix, dispatch battle-test (hoặc full QA) subagent MỚI trên file đã patch. Pre-fix score (60) vs post-fix (92) là evidence gate hoạt động. Warren hay hỏi "re-run to confirm?" → say yes, rẻ mà chắc.

## Drift grep template (dùng sau adapt cross-profile)
```
grep -rn "LU3\|LU5\|LU7\|triệu VND\|Saigon Centre\|mall regulation\|<old ANCHORS path>\|<source-specific skill>\|warren-profile" <target>/skills/...
```
→ MUST return ZERO source-domain hits.
