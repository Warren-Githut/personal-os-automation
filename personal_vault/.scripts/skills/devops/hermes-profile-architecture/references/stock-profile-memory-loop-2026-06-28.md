# Stock-Profile Memory Loop Setup (2026-06-28)

## Context
Set up self-evolving memory loop for stock-profile, mirroring warren-profile architecture. Key difference: stock-profile shares personal_vault with personal_profile → needed prefixed filenames to avoid collision.

## Architecture Decisions

### SSOT Location (shared vault)
- Since stock-profile shares `personal_vault` with personal_profile, vault SSOT uses prefixed names:
  - `00_CORE_LOGIC/STOCK_MEMORY.md` (not `MEMORY.md`)
  - `_inbox/_stock_profile_memory_raw.md` (prefix for Obsidian clarity)
- Profile cache: `AppData/Local/hermes/profiles/stock-profile/memories/MEMORY.md`
- Direction: vault SSOT → profile cache (1-way)

### Cycle Cadence
- Per-session (not daily): read→apply→propose→log
- Monthly compress (not weekly): `/compress-stock-memory`

### Language
- Toàn bộ Tiếng Việt có dấu (override SOUL.md English declaration)

### Git Commit Trigger
- Warren prefers memory proposals only on git commit, NOT end-of-session
- Git commit is the sole deterministic trigger

## Path Pitfall (cost 45 min debugging)
Hermes Desktop reads from `AppData/Local/hermes/profiles/` but earlier sync commands wrote to `~/.hermes/profiles/`. Result: stock-profile Hermes said "no MEMORY.md" because the file was at the wrong path. **Fix:** Always use `AppData/Local/hermes/profiles/` for profile cache files.

## Files Created/Modified

| File | Action |
|------|--------|
| `stock_vault/00_CORE_LOGIC/STOCK_MEMORY.md` | Created (SSOT) |
| `stock_vault/_inbox/_stock_profile_memory_raw.md` | Created (raw log) |
| `stock_vault/_archives/memory/` | Created |
| `stock-profile/memories/MEMORY.md` | Synced from SSOT |
| `stock-profile/SOUL.md` | Added Self-Evolving Memory Loop section |
| `stock-profile/AGENTS.md` | Updated profile map |
| `stock-profile/memories/USER.md` | Added governance note |
