# 00_CORE_LOGIC Restructure — 2026-07-01

## What Happened

Split the shared `00_CORE_LOGIC/CONTEXT.md` and `00_CORE_LOGIC/USER.md` into profile-specific files using `{PROFILE}_{TYPE}.md` prefix naming. Created a parallel Hermes profile (`personal_profile`) mirroring the existing `stock-profile`.

## File Mapping

| Before | After | Profile |
|--------|-------|---------|
| `USER.md` | `STOCK_USER.md` | stock-profile |
| (none) | `PERSONAL_USER.md` | personal_profile |
| `CONTEXT.md` | `STOCK_CONTEXT.md` (trading sections) | stock-profile |
| (none) | `PERSONAL_CONTEXT.md` (personal sections) | personal_profile |
| `STOCK_MEMORY.md` | kept as-is | stock-profile |
| (none) | `PERSONAL_MEMORY.md` | personal_profile |
| (none) | `PERSONAL_AGENT.md` | personal_profile |
| `AGENTS.md` | `STOCK_AGENT.md` | stock-profile |

## Naming Convention

`{PROFILE}_{TYPE}.md` — prefix sorts by profile in flat folder. Both profiles' files visible at root level. Example: `STOCK_USER.md`, `PERSONAL_USER.md`.

## Key Learnings

### 1. Full Path Enforcement is Manual
After the restructure, 12+ abbreviated paths (`00_CORE_LOGIC/` instead of `stock_vault/00_CORE_LOGIC/`) had to be retroactively fixed across 6 files. **Fix:** After any profile file rename/move, grep for bare `00_CORE_LOGIC/` and `_inbox/` in SOUL.md, AGENTS.md, MEMORY.md files.

### 2. Plain `rm` Doesn't Work for Tracked Files
Deleting tracked files with `rm -rf` removes them from disk but git restores them on next commit. **Fix:** Always use `git rm <path>` (files) or `git rm -rf <path>` (directories) for git-tracked files. Empty directory shells left after `git rm` need a separate `rm -rf` pass.

### 3. Bidirectional Forbidden Zones
Both profiles must have `🚫 TUYỆT ĐỐI CẤM` sections — not just personal forbidding stock, but stock also forbidding personal. Implemented in both AGENT.md Access sections and SOUL.md Hard Rules.

### 4. Obsidian Wikilink Fragility
After CONTEXT.md → STOCK_CONTEXT.md + PERSONAL_CONTEXT.md, 28 broken wikilinks across 6 vault files pointed to the deleted file. **Fix:** Scripted replacement — existing sections (§2, §3, §4) remapped to their new file; removed sections (§6, §7, §9) had their wikilinks deleted.

### 5. AGENT.md Naming
Profile-level agent files follow `{PROFILE}_AGENT.md`: `STOCK_AGENT.md`, `PERSONAL_AGENT.md`. The stock-profile file was originally `AGENTS.md` (bare name, no prefix) and had to be renamed for consistency. New profiles should use the prefix from creation.

## Session Start Protocol Template

```
1. SOUL.md
2. stock_vault/00_CORE_LOGIC/{PROFILE}_MEMORY.md
3. stock_vault/00_CORE_LOGIC/{PROFILE}_USER.md
4. stock_vault/00_CORE_LOGIC/{PROFILE}_CONTEXT.md
```

## Memory Write Protection (Hard Rule)

Both profiles enforce: never auto-write MEMORY.md (Hermes built-in memory) unless Warren explicitly says "ghi". Raw lessons append to `stock_vault/_inbox/_{profile}_memory_raw.md` only on direct command.
