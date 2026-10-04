# Mem0 Cleanup — Session Recipe (2026-06-26)

## Context

Warren's Mem0 had 37 memories, ~97% full (2,145/2,200 built-in memory). 70%+ were task artifacts: script paths, cron IDs, bug descriptions, test results, duplicate entries.

## The Pagination Pitfall

`mem0_list(page=1, page_size=200)` returned count=20. After deleting 17 noise items from page 1, re-running `mem0_list` showed count=20 again — 17 NEW memories from page 2 surfaced.

**Rule:** Always verify after each deletion pass. The mem0_list pagination can hide items. Keep cleaning until count stabilizes.

## Cleanup Passes

### Pass 1: 20 memories → kept 3, deleted 17
- 14 noise (task artifacts, bug descriptions, vague questions)
- 3 duplicates
- Kept: script path convention, "don't try random requests", LU5 Guest×AC formula

### Pass 2: 20 memories → kept 3 more, deleted 14 + 1 duplicate
- 11 noise (more task artifacts, test results, config details)
- 3 duplicates (LU5 Guest×AC ×2, ops_col JSON parse ×2, workflow question ×2)
- Kept: restart Hermes tip, case dedup pre-check rule, ops_col JSON parse pattern

### Final Pass: 7 → 6 (1 duplicate remaining)
- Deleted: duplicate of "don't try random requests"

## Final State

**6 memories, ~15% usage:**

| # | Memory |
|---|--------|
| 1 | Hermes Desktop resolve script path từ `profile/scripts/` |
| 2 | Đừng thử ngẫu hứng request ở đây nữa |
| 3 | LU5 Guest×AC detection formula |
| 4 | Restart Hermes để model mới có hiệu lực |
| 5 | Hermes tự động pre-check case trước khi tạo mới |
| 6 | Parse `missing_revenue` từ JSON log (không grep text thô) |

## Session 2: 13→5 (2026-06-26 — same day, auto-duplication)

After the initial 37→6 cleanup, Mem0's Ollama LLM backend silently duplicated memories during normal conversation. Within hours, 6 became 13 — 7 were near-identical duplicates of the 5 keepers.

### Discovery

The weekly cron job (`mem0-cleanup-warren`) ran its first manual test and flagged:
- 5 KEEP (same as Session 1)
- 7 DUPLICATE (3 groups: LU5 Guest×AC ×3, ops_col JSON parse ×3, case pre-check ×3)
- 1 NOISE ("đừng thử ngẫu hứng request" — previously kept, now flagged as vague/context-dependent)

### Root Cause

Ollama (`llama3.2:3b`) as Mem0's LLM backend does not perform semantic deduplication before inserting new memories. Every time the agent references a fact, Mem0 may create a new (near-identical) entry rather than updating the existing one.

### Cleanup

Warren replied `ok` → 8 deletions in parallel. Result: 5 clean memories.

### Key Insight

**Weekly cleanup is NOT optional with Ollama-backed Mem0.** Auto-duplication can double memory count in a single active session. The weekly cron pattern (see `references/mem0-weekly-cron-pattern.md`) is the minimum viable defense.

1. **Vault SOUL.md** — added Section 10 (MEM0 GATE) with 2-question pre-save filter
2. **Hermes built-in memory** — updated noise reduction rule, freed 7% by shortening 5 other entries
3. **This skill** — added Mem0 Maintenance section with cleanup workflow
4. **All 3 profile SOUL.md files** — added MEM0 GATE section with profile-specific examples

## Post-Cleanup Discovery: Auto-Duplication

After cleanup (6 memories), Mem0 silently grew to 13 in one session — 7 were automatic duplicates. Root cause: Ollama LLM backend (`llama3.2:3b`) does not perform semantic deduplication before inserting memories. The embedder (`nomic-embed-text`) may produce near-identical vectors for similar text, but the Ollama extractor re-extracts "facts" on every turn without checking if they already exist.

**Implication:** Weekly cleanup is mandatory, not optional. See `references/mem0-weekly-cron-pattern.md` for the automated solution.

## Verdict

| Before | After | Method |
|--------|-------|--------|
| 37 memories, ~97% noise | 6 memories, 100% durable | 2-pass bulk delete + gate update |
| 1 week later | 13 memories (7 auto-duplicates) | Ollama backend auto-extraction |
| Solution | Weekly cron cleanup | 3-profile staggered Sunday cron |

## Key Pattern: Bulk Delete + Clarify

```
1. mem0_list → all memories
2. Categorize: KEEP / DELETE / DELETE-DUPLICATE
3. Present table to user with clarify(choices=[...])
4. On confirm: all mem0_delete calls in parallel (independent)
5. mem0_list → verify + check for hidden pages
6. Repeat until clean
```

## Budget Management Pattern

When built-in memory is full and a new rule is needed:
- Shorten verbose entries (remove parentheticals, abbreviations)
- Remove stale environment facts before durable preferences
- Batch ALL changes in one `memory(operations=[...])` call
- Target: keep usage at 85-90% for headroom
