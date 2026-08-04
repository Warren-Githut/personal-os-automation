# Personal Profile Bootstrap — 2026-07-01

## Context

Stock-profile and personal_profile share `personal_vault`. Task: create personal_profile from scratch (was a registered name with zero files) with complete Hermes identity, while renaming/splitting the shared 00_CORE_LOGIC/ files.

## Steps

### 1. Vault file restructuring (00_CORE_LOGIC/)

**Naming convention:** `{PROFILE}_{TYPE}.md` — prefix over subfolder.

| Before | After |
|---|---|
| `USER.md` (stock) | `STOCK_USER.md` |
| (none) | `PERSONAL_USER.md` |
| `CONTEXT.md` (shared) | `STOCK_CONTEXT.md` + `PERSONAL_CONTEXT.md` |
| `STOCK_MEMORY.md` | `STOCK_MEMORY.md` (kept) |
| (none) | `PERSONAL_MEMORY.md` |

**Split CONTEXT.md:** Extract sections by domain:
- Stock gets: §3 Trading Profile, §6 Financial (stock angle), §10 Vault Architecture, §11 Thinking Patterns (trading parts)
- Personal gets: §1 Warren Profile, §2 Family, §4 Health, §11 Thinking Patterns (full)
- Removed from personal: §5 Relationships, §6 Financial (personal), §7 Active Decisions, §8 Goals, §9 This Week

**Legacy cleanup (same session):** `_kilo/`, `.kilo/`, `.kilocode/`, `docs/`, `tests/`, `_tmp_broker/`, `README.md`, `AGENTS.md` (vault root) — all deleted.

### 2. Broken link repair

After CONTEXT.md split, 28 files referenced the old `00_CORE_LOGIC/CONTEXT.md`:
- **§2 links** (Family) → `PERSONAL_CONTEXT.md`
- **§3 links** (Trading) → `STOCK_CONTEXT.md`
- **§6, §9 links** (removed sections) → delete wikilink entirely
- **Data source citations** (doctor reports) → `PERSONAL_CONTEXT.md`

Used Python script for batch replacement in `weekly_connections_log.md` (12 links).

### 3. Hermes profile bootstrap (personal_profile)

```
~/.hermes/profiles/personal_profile/
├── SOUL.md              — Identity: personal life assistant. NOT stock analyst.
├── PERSONAL_AGENT.md    — Vault access with 🚫 forbidden zones (stock folders)
└── memories/
    └── MEMORY.md        — Built-in memory cache, sync from vault PERSONAL_MEMORY.md
```

**SOUL.md key choices:**
- NOT a stock analyst — redirect to stock-profile
- 8 HARD RULES including: Memory write protection, Stock domain cấm tuyệt đối
- Session start: PERSONAL_MEMORY.md → PERSONAL_USER.md → PERSONAL_CONTEXT.md

**PERSONAL_AGENT.md key choices:**
- Named `PERSONAL_AGENT.md` (not `AGENTS.md`) to avoid collision
- `🚫 TUYỆT ĐỐI CẤM` section: forbidden to read/grep/search stock folders
- Read+write: health pulse, family wiki, cases, growth, PERSONAL_* files

### 4. Raw memory log

Created `_inbox/_personal_memory_raw.md` — append-only, same mechanism as stock's `_stock_profile_memory_raw.md`.

## Key Decisions

| Decision | Rationale |
|---|---|
| Prefix naming (`STOCK_USER.md`) not subfolder (`stock/USER.md`) | Flatter, search faster, simpler with few files |
| Full paths in SOUL.md/AGENTS.md (`stock_vault/00_CORE_LOGIC/...`) | Prevents path confusion across profiles |
| 🚫 Forbidden zones in AGENTS.md | Stronger than read-only — blocks read/grep/search entirely |
| PERSONAL_AGENT.md not AGENTS.md | Avoids filename collision in Hermes profiles dir |
| CONTEXT.md sections removed from personal | Keeps PERSONAL_CONTEXT.md lean; removed sections were stale |
