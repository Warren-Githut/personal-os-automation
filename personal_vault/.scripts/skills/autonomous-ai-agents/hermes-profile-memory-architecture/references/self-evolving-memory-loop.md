# Self-Evolving Memory Loop — Reference Protocol

> For profiles using vault-based memory architecture with write governance.

## Architecture Overview

```
Silent tracking during session (3 questions: worked? failed? rule?)
         │
         ▼ Warren runs `git commit`
    Agent checks: any lessons tracked?
         │
         ├─ No lessons → silent, no spam
         │
         └─ Has lessons → propose → Warren approves
                              │
                              ▼ append
    _inbox/warren_memory_raw.md  ◄── raw lessons (append-only, newest on top)
         │
         ▼  /compress-memory
    [consolidate + dedup + sharpen]
         │
         ▼ propose → approve
    vault/00_CORE_LOGIC/<SSOT>.md  ◄── reference (Hermes reads at session start)
         │
         ▼ sync
    ~/.hermes/profiles/<name>/<SYNC>.md  ◄── Kilo Code / Cursor copy (KHÔNG phải built-in memory)
```

> **Important:** Vault SSOT file được đặt tên `<NAME>_MEMORY.md` (VD: `WARREN_MEMORY.md` cho warren-profile, `STOCK_MEMORY.md` cho stock-profile) để tránh lộn với built-in memory file `memories/MEMORY.md`.
>
> **Override rule (session start):** Vault SSOT overrides built-in memory khi conflict.

## File Roles

| File | Role | Write frequency | Who triggers |
|------|------|-----------------|--------------|
| `_inbox/warren_memory_raw.md` | Raw lessons log | Per-session (append) | Git commit proposal → Warren OK |
| `vault/00_CORE_LOGIC/<SSOT>.md` | Distilled reference | Per `/compress-memory` | Compress → Warren OK |
| `vault/00_CORE_LOGIC/USER.md` | User profile | Per preference discovery | Agent detects → proposes → Warren OK |
| `mem0` (Qdrant) | Durable vector facts | Per compress cycle | Compress → Warren OK → push selected entries |

## Raw Log Format (`_inbox/warren_memory_raw.md`)

Single file, append-only, newest on top:

```
## 2026-06-28
- [Preferences] Warren muốn conclusion-first, Hermes show 3-4 options kèm recommended
- [Corrections] Lần X: suggest sai Y → học được Z

## 2026-06-27
- [Patterns] Warren hay quên check review queue → Hermes chủ động check
- [Lessons Learned] CR >30% khi upsell drink → cần script auto-calc
```

Tags: `[Preferences]` / `[Corrections]` / `[Patterns]` / `[Lessons Learned]`
- Language: Tiếng Việt (có dấu)
- 1-2 dòng mỗi entry
- Prepend newest entry
- Không ghi đè, không sửa entry cũ

## Lesson Proposal Trigger (deterministic = git commit)

During session, agent silently tracks lessons (no propose, no interruption).
When Warren runs `git commit`, agent checks tracked lessons:

1. Something worked well → propose **Patterns** or **Lessons Learned**
2. Something failed → propose **Corrections** or **Lessons Learned**
3. New Warren preference discovered → propose **Preferences** (raw) or **USER.md** update
4. Existing rule improved → note for next compress

No lessons tracked → silent. 100% consistent per session — not vague "cuối session".

Proposal format:
```
📝 Memory đề xuất:
→ [Preferences] Warren muốn binary option trước multi-step workflow
→ [USER.md] Warren thích Hermes tự động check queue mà không hỏi

Nếu OK: anh nói "ghi" — tôi append vào _inbox/warren_memory_raw.md hoặc update USER.md
```

## `/compress-memory` Protocol

1. **Archive** → copy SSOT file → `vault/_archives/memory/<SSOT>_YYYY-MM-DD.md`
2. **Read** → đọc `_inbox/warren_memory_raw.md` + SSOT hiện tại
3. **Consolidate** → merge raw lessons, dedup, sharpen rules. Goal: fewer, better rules.
4. **Propose** → show Warren draft SSOT
5. **Apply** → Warren OK → ghi đè `vault/00_CORE_LOGIC/<SSOT>.md`
6. **Clean raw** → clear `_inbox/warren_memory_raw.md` (hoặc archive vào `_archives/memory/raw/`)
7. **Push mem0** → hỏi "có push durable facts lên mem0 không?" → OK → select + write
8. **Sync** → copy SSOT sang `memories/<SSOT>_SYNC.md` (cho Kilo Code/Cursor — KHÔNG phải built-in memory)
9. **Report** — "Đã distill X raw entries → Y rules. Archive tại _archives/memory/."

## Daily Cycle (Every Session)

1. **Session start:** Hermes reads SSOT → applies Preferences/Corrections/Patterns/Lessons Learned (override built-in memory)
2. **Internal check (silent, after each major task):**
   - Điều gì worked? → ghi nhớ, không propose
   - Điều gì failed? → ghi nhớ, không propose
   - Rule nào rút ra? → ghi nhớ, không propose
3. **Trigger = git commit:** Agent checks tracked lessons. Has lessons → propose. No lessons → silent.

## Weekly Cycle (`/compress-memory`)

Warren runs manually any day:

1. **Archive** — copy SSOT → `vault/_archives/memory/<SSOT>_YYYY-MM-DD.md` (archive BEFORE every rewrite)
2. **Read** — đọc `_inbox/warren_memory_raw.md` + SSOT hiện tại
3. **Distill** — "Identify patterns across all logged lessons. Distill into sharper, more general rules. Delete anything superseded. Goal: fewer, better rules."
4. **Propose** — show Warren draft SSOT mới
5. **Apply** — Warren OK → ghi đè `vault/00_CORE_LOGIC/<SSOT>.md`
6. **Clean raw** — clear `_inbox/warren_memory_raw.md` (or archive to `_archives/memory/raw/`)
7. **Push mem0** — hỏi "có muốn push durable facts lên mem0 không?"
8. **Sync** — copy SSOT sang `memories/<SSOT>_SYNC.md`
9. **Report** — "Đã distill X raw → Y rules. Archive tại _archives/memory/."

> **Hard rule:** Never delete before archiving. Archive BEFORE every cleanup — if anything goes wrong during rewrite, the previous version is recoverable.

## Archive Location

- SSOT backups: `vault/_archives/memory/<SSOT>_YYYY-MM-DD.md`
- Raw logs (optional): `vault/_archives/memory/raw/YYYY-MM-DD_raw.md`

## 2-Gate Filter (applies to ALL memory writes)

| # | Gate | Nếu NO → |
|---|------|----------|
| 1 | **7 ngày nữa thông tin này còn đúng và có giá trị không?** | SKIP |
| 2 | **Đây là durable fact (preference/decision/config/lesson), hay task artifact?** | Nếu artifact → SKIP |

> **Additional hard rule:** Never trust LLM output without verification. The 2-gate filter is the first pass; manual cross-check is the second. Hallucinations are silent and confident — always verify before writing into memory.

## Relationship to Other Skills

This pattern complements `mem0-cleanup-workflow.md` — mem0 is a downstream consumer of distilled SSOT entries, not a replacement for the raw→reference pipeline.

## Anti-Patterns

- 🚫 Using SSOT as daily log — it's a reference; raw lessons go to `_inbox/warren_memory_raw.md`
- 🚫 Skipping the 2-gate filter — bloat defeats the purpose of learning
- 🚫 Syncing raw logs to profile — only the distilled SSOT travels
- 🚫 Auto-writing without Warren approval — undermines trust in the memory layer
- 🚫 Writing to SSOT directly via end-of-session — SSOT is for compress output only; raw goes to `_inbox/warren_memory_raw.md` (exception: Warren direct command explicitly says "ghi thẳng vào MEMORY.md")
- 🚫 **Syncing markdown to `memories/MEMORY.md`** — the Hermes `memory` tool's backing file uses **§-delimited format**, not markdown. SSOT file has been renamed from `MEMORY.md` to `<NAME>_MEMORY.md` (e.g., `WARREN_MEMORY.md`) to prevent accidental collision. Sync step goes to `memories/<SSOT>_SYNC.md` — different path, same content, no drift.
