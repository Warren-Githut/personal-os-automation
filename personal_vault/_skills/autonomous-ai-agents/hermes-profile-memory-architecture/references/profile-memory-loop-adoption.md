# Adopting Memory Loop Across Profiles

> **Pattern:** Clone/adjust the self-evolving memory loop from an existing profile (e.g., warren-profile) to a new profile (e.g., stock-profile).
> Source session: 2026-06-28 stock-profile adoption.

## When to Adopt (vs Build from Scratch)

Adopt when:
- A profile already exists but has a flat/functional MEMORY.md (tool commands + YAML schema only)
- The source profile's memory loop is proven + battle-tested
- User wants governance consistency across profiles

Build from scratch when:
- First profile on a new system
- Profile domain is fundamentally different (e.g., coding assistant vs analyst)
- Source profile has known anti-patterns you don't want to replicate

## Decision Parameters (Interview Questions)

Every adoption requires these decisions, surfaced via `interview-me`:

| Parameter | Warren Default | Stock Profile Decision |
|-----------|---------------|----------------------|
| **Usage frequency** | Daily ops | Ad-hoc, 2-4x/month → lighter cycle |
| **Components** | Full 4: daily cycle + compress + governance + 4 sections | Full 4, but **per-session** (not daily), **monthly** compress |
| **Language** | Tiếng Việt có dấu | Override profile default — use Tiếng Việt for memory files |
| **SSOT location** | `vault/00_CORE_LOGIC/MEMORY.md` | Same pattern: `vault/00_CORE_LOGIC/STOCK_MEMORY.md` |
| **Raw log location** | (abolished 2026-08-30) | Same pattern but with **profile prefix** to avoid collision |
| **Profile cache** | `profile/MEMORY.md` (sync from vault) | Same: `profiles/stock-profile/memories/MEMORY.md` |
| **Sync direction** | Vault → Profile | Same (SSOT is vault, cache is profile) |
| **Observation** | Within vault (Obsidian visible) | YES — raw log in vault so user sees it |

## Shared Vault Collision

When two profiles share a vault (e.g., stock-profile + personal-profile both use `personal_vault`):

- (raw logs abolished 2026-08-30)
- **MEMORY.md must be named distinctly**: `STOCK_MEMORY.md` vs `MEMORY.md`
- **Archive**: `_archives/memory/` is shared — use distinct filenames (e.g., `STOCK_MEMORY_2026-06-28.md`)

## Adapt Cadence

| Component | Daily Profile (Ops) | Ad-hoc Profile (Stock) |
|-----------|-------------------|----------------------|
| Session cycle | Check 3 questions (worked? failed? rule?) per major task | Same — but may only have 1 task per session |
| Write frequency | Multiple times/week | 1-2 times/month |
| Compress cycle | Weekly | Monthly, or after 3-4 sessions |

## Template: STOCK_MEMORY.md Structure

```
YAML frontmatter (name, type, status, version, tags, domain)
→ Per-Session Memory Cycle
→ Monthly Cycle (/compress-stock-memory)
→ Nguyên tắc chung (general principles)
→ Write Governance (2 gates + 4 write paths)
→ Preferences (empty initially, accumulate over sessions)
→ Corrections (empty initially)
→ Patterns (empty initially)
→ Lessons Learned (empty initially)
```

Key differences from warpen MEMORY.md:
- Domain tag = `stock` instead of `ops`
- Compress command = `/compress-stock-memory` instead of `/compress-memory`
- Sync target = `profiles/stock-profile/memories/MEMORY.md`
- Content = stock-domain rules (valuation, BCTC, thesis) vs ops rules
