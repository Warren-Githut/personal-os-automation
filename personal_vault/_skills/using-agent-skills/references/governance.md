# Governance & History — using-agent-skills

> Tách từ SKILL.md chính (2026-07-21) để giảm context bloat.
> Load file này khi: debug staging bug, tra cứu quyết định kiến trúc cũ, hoặc cần hiểu lịch sử consent-gate.

---

## Self-Building Loop (Warren-added 2026-07-12)

**Trigger:** Task with 5+ tool calls, OR Warren says "lưu lesson" / "tạo skill" / "save as skill".

**Mandatory procedure (gated — does NOT auto-write):**

1. **Analyze → Plan → Execute → Review.** Decompose goal, execute with tools, review result, find bugs.
2. **Draft lesson.** Draft into `pending/memory` and/or propose `skill_manage` patch for custom skill.
3. **VERIFY independently** before staging — run verification gate. No verification → do not stage.
4. **Stage, never auto-approve.** Write to `<HERMES_HOME>/pending/{memory,skills}/` and STOP. Wait for Warren `/approve`.
5. **Scope lock.** Only patch **custom** skills (`warren-profile/skills/...`). NEVER touch bundled.

**Hard constraints:**
- ⚠️ Does NOT run on trivial tasks (≤4 tool calls)
- ⚠️ Does NOT override SOUL consent gate or Verify Gate
- ⚠️ On small/free models, self-fix confidence is lower — still stage for review, never auto-apply

---

### ⚠️ Skill Extension Pitfalls (Warren-corrected 2026-07-12)

**P1 — Multi-mode ordering.** Discovery/ideation mode MUST be Mode A, evaluation MUST be Mode B. Wrong order = broken logic. Concrete miss: `promo-eval` eval=Mode A, discover=Mode B → Warren caught it.

**P2 — No inbox temp-file step.** Do NOT write spec/plan to `_inbox/`. Hold design inline: spec → Warren review → plan → approve → implement. If durable spec needed → skill's `references/` dir, never `_inbox/`.

**P3 — RUTHLESS before plan approval.** Run `/ruthless` on plans BEFORE Warren approves. Plans often collapse 5→2 tasks.

**P4 — Skill files live outside the vault repo.** Custom skills live in `AppData/.../skills/` — NOT in Warren_OS_Local. `git status` won't show them. Commit only vault-side artifacts.

---

## Warren Consent-Gate Architecture (CRITICAL — do NOT "fix" this)

**Deliberate design, confirmed 2026-07-12:** Warren explicitly said keep `write_file` ungated — "giữ nó y như vậy, tôi cần nó như vậy."

Two parallel memory-write paths exist:
1. **Gated tools** (`memory` tool, `skill_manage` create/update) → stage into `<HERMES_HOME>/pending/{memory,skills}/`, need Warren `/memory approve` or `/skills approve`.
2. **Ungated `write_file`** → writes vault files (WARREN_MEMORY.md, warren_memory_raw.md, USER.md, SKILL.md) **directly, no staging, no approval prompt**.

**This is intentional and correct for Warren:**
- `write_file` is the "back door" past consent gates BY DESIGN. When `skill_manage` staging glitches (pending JSON written but not materialized to disk), `write_file` is the legitimate fallback to complete the write — Warren approved this.
- Do NOT add a consent gate to `write_file`. Do NOT treat ungated `write_file` to vault memory files as a violation. Do NOT "remind Warren he forgot to approve" when he used `write_file` directly.
- If you ever feel a write was unsafe, flag it AFTER the fact (propose a correction), never block or revert a `write_file` that Warren explicitly directed or that fulfills an approved intent.

**Root cause of the 2026-07-12 confusion:** the `memory`/`skill_manage` gates only hook their *own* tools. `write_file` is immune. This is fine — Warren wants it that way. Don't close the gap.

---

## Proven Skill-Creation Pipeline (canonical path, 2026-07-12)

```
1. using-agent-skills        — classify, check path (warren-profile vs bundled), dedup
2. interview-me              — 100% confidence BEFORE writing anything
3. planning-and-task-breakdown — plan (ruthless afterward, usually 5→2 tasks)
4. ruthless                  — delete/merge redundant tasks
5. skill_manage(action='create') — writes SKILL.md, STAGES (pending/)
6. Warren: /skills approve <id>  — gates materialize the file to disk
7. code-review-and-quality + code-simplification — run on SAME slice
8. script + verify          — if script needed: write_file, run ad-hoc verify, PASS then clean temp
9. git commit + push        — scoped, Warren-confirmed (git-workflow gate)
```

**⚠️ Pitfall — `/skills approve` clears pending but file NOT written (observed 2026-07-12, pending IDs `d080e9a7` + `692b6e9f`):**
Symptom: after Warren runs `/skills approve <id>`, staged JSON disappears from `pending/skills/` BUT `skills/<name>/SKILL.md` stays EMPTY (dir created, 0 bytes). Silent error.
**Fix / fallback:**
1. After `/skills approve <id>`, ALWAYS verify: `ls "$LOCALAPPDATA/Hermes/profiles/warren-profile/skills/<name>/SKILL.md"` + `skill_view('<name>')`.
2. If pending cleared but file absent → Warren's verbal approve already satisfied consent gate. Write SKILL.md directly via `write_file`.
3. Report: "approve cleared pending nhưng file chưa ghi → đã write_file thủ công (Warren đã approve)."
**Do NOT** re-stage and re-approve in a loop — it clears pending again without writing. Go straight to write_file.

- ⚠️ Memory dual-truth: `memories/MEMORY.md` (built-in auto-write) can freeze stale. `WARREN_MEMORY.md` (vault, via /compress-memory + approve) is the ONLY SSOT. Never treat `memories/MEMORY.md` as current fact.
