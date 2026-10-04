# Personal Profile Bootstrap Session — 2026-07-01

## What was done

1. **Split `00_CORE_LOGIC/CONTEXT.md`** → `STOCK_CONTEXT.md` (trading) + `PERSONAL_CONTEXT.md` (personal)
2. **Named vault files** with `{PROFILE}_{TYPE}` prefix: `STOCK_USER.md`, `PERSONAL_USER.md`, `STOCK_CONTEXT.md`, `PERSONAL_CONTEXT.md`, `PERSONAL_MEMORY.md`
3. **Kept `STOCK_MEMORY.md`** as-is (no rename needed — Warren confirmed)
4. **Created personal_profile Hermes profile** from scratch:
   - `personal_profile/SOUL.md` — 10-section numbered format
   - `personal_profile/PERSONAL_AGENT.md` — `{PROFILE}_AGENT.md` naming
   - `personal_profile/memories/MEMORY.md` — built-in memory cache
5. **Updated stock-profile SOUL.md** to match the new 10-section format with full paths
6. **Bidirectional forbidden zones** — both profiles now forbid each other's domains from read/grep/search

## Key decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Naming convention | `{PROFILE}_{TYPE}.md` (e.g., `STOCK_USER.md`) | Consistent, searchable, flat folder |
| Full paths | `stock_vault/00_CORE_LOGIC/...` everywhere | Prevents cross-profile path confusion |
| AGENT naming | `PERSONAL_AGENT.md` (not `AGENTS.md`) | Consistent with other files |
| Forbidden zones | Bidirectional — both profiles forbid each other | One-direction caused memory pollution |
| Memory write | Only on "ghi" command, never auto-write | Warren's explicit HARD RULE |
| SOUL.md format | 10 numbered sections | Ensures complete coverage across profiles |

## Files created

| Path | Purpose |
|------|---------|
| `~/.hermes/profiles/personal_profile/SOUL.md` | Identity + rules |
| `~/.hermes/profiles/personal_profile/PERSONAL_AGENT.md` | Vault access + boundaries |
| `~/.hermes/profiles/personal_profile/memories/MEMORY.md` | Built-in memory cache |
| `stock_vault/00_CORE_LOGIC/PERSONAL_USER.md` | Warren personal profile |
| `stock_vault/00_CORE_LOGIC/PERSONAL_CONTEXT.md` | Personal context slice |
| `stock_vault/00_CORE_LOGIC/PERSONAL_MEMORY.md` | Personal memory SSOT |
| `stock_vault/00_CORE_LOGIC/README.md` | File mapping |
| `stock_vault/_inbox/_personal_memory_raw.md` | Raw lessons log |
| `stock_vault/00_CORE_LOGIC/STOCK_CONTEXT.md` | Stock context slice |
| `stock_vault/00_CORE_LOGIC/STOCK_USER.md` | (renamed from USER.md) |

## Legacy cleanup

Deleted during session: `_kilo/`, `.kilo/`, `.kilocode/`, `docs/`, `tests/`, `AGENTS.md` (vault root), `README.md` (vault root), `00_INDEX.md`, `wiki/investing/` (duplicate), `_tmp_broker/`, `_inbox/inbox-notes/`, `_inbox/inbox-data/`.

Updated broken wikilinks in: `weekly_connections_log.md` (13 links), `DECISION_LOG.md`, doctor reports, `Warren_Generic_Profile.md`, vault `AGENTS.md`.
