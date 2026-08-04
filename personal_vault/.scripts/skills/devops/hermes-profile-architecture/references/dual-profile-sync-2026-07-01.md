# Dual Profile Sync — stock-profile + personal_profile (2026-07-01)

## What Was Done

### Vault Cleanup (pre-work)
- Deleted `wiki/investing/` (stale duplicate of `03_Investing/`) — 25 files, diff confirmed
- Deleted `wiki/00_INDEX.md` (stale duplicate of `00_WIKI_INDEX.md`)
- Deleted `_kilo/`, `.kilo/`, `.kilocode/` (legacy Kilo Code — 3,471 files, 57MB)
- Deleted `_tmp_broker/` (empty), `docs/` (2 stale plans), `tests/` (1 file)
- Deleted vault `README.md` (outdated), `AGENTS.md` (Kilo Code rules, now in Hermes profile)
- Deleted `_inbox/inbox-notes/` + `_inbox/inbox-data/` (empty, updated README.md routing)

### CONTEXT.md Split
Original `00_CORE_LOGIC/CONTEXT.md` (shared between profiles) → two domain-specific files:

| New file | Sections from original | Profile |
|---|---|---|
| `STOCK_CONTEXT.md` | §3 Trading Profile, §6 Financial (stock angle), §10 Vault Architecture, §11 Thinking Patterns (stock parts) | stock-profile |
| `PERSONAL_CONTEXT.md` | §1 Warren Profile, §2 Family Status, §4 Health Baseline, §11 Thinking Patterns (full) | personal_profile |

Removed from PERSONAL_CONTEXT: §5 Relationships, §6 Financial (personal), §7 Active Decisions, §8 Goals, §9 This Week.

### File Renaming (Prefix Convention)
All files in `00_CORE_LOGIC/` follow `{PROFILE}_{TYPE}.md`:

| Old name | New name | Profile |
|---|---|---|
| `USER.md` | `STOCK_USER.md` | stock-profile |
| (new) | `PERSONAL_USER.md` | personal_profile |
| `CONTEXT.md` (deleted) | `STOCK_CONTEXT.md` + `PERSONAL_CONTEXT.md` | both |
| `STOCK_MEMORY.md` | kept (already correct) | stock-profile |
| (new) | `PERSONAL_MEMORY.md` | personal_profile |

### personal_profile Hermes Setup (from scratch)
Created `~/.hermes/profiles/personal_profile/` with:

| File | Key content |
|---|---|
| `SOUL.md` | Identity (personal assistant), 8 hard rules, session protocol, profile map |
| `PERSONAL_AGENT.md` | Vault access (READ+WRITE health/family), 🚫 TUYỆT ĐỐI CẤM stock folders, boundaries |
| `memories/MEMORY.md` | Per-session cycle, monthly `/compress-personal-memory`, write governance, 2 HARD RULES |
| Raw log | `stock_vault/_inbox/_personal_memory_raw.md` (created) |

### stock-profile Updates (sync with personal format)

| File | Changes |
|---|---|
| `SOUL.md` | Added YAML frontmatter, 10-section format, 5 hard rules (memory write protection + personal domain forbidden), profile map, session protocol |
| `memories/MEMORY.md` | Full path `stock_vault/`, HARD RULES table in Write Governance |
| `STOCK_MEMORY.md` | Full path `stock_vault/`, HARD RULES table |
| `STOCK_USER.md` | Added "Kết nối với personal_profile" + 2 hard rules |
| `AGENTS.md` | Added 🚫 TUYỆT ĐỐI CẤM section for personal folders, updated boundaries, full paths in profile map |

### Broken Link Repairs
- `vault/AGENTS.md` — session start path → STOCK_CONTEXT.md + PERSONAL_CONTEXT.md
- `weekly_connections_log.md` — 12 wikilinks: §2→PERSONAL_CONTEXT, §3→STOCK_CONTEXT, §6+§9 deleted
- `DECISION_LOG.md` — removed CONTEXT.md §7 reference
- Doctor reports (x2): paths → PERSONAL_CONTEXT.md
- `Warren_Generic_Profile.md`: path → PERSONAL_CONTEXT.md

## Cross-Profile Forbidden Zones (Bidirectional)

Both profiles must forbid each other's folders:

| Profile | 🚫 CẤM TUYỆT ĐỐI (no read/grep/search) |
|---|---|
| **stock-profile** | `02_Health/`, `Daily_Pulse.md`, `050_Health_Log.md`, `051_Sleep_Log.md`, `PERSONAL_*`, `_cases/` |
| **personal_profile** | `03_Investing/`, `020_VNStock_*`, `STOCK_*` |

Implemented in both `SOUL.md` (HARD RULES section) and `AGENT.md` (Access section).

## Hard Rules Added to Both Profiles

| Rule | stock-profile | personal_profile |
|---|---|---|
| **Memory write protection** | ✅ Don't auto-write MEMORY.md without "ghi" | ✅ Same |
| **Cross-domain forbidden** | ✅ Personal domain cấm | ✅ Stock domain cấm |

## File Structure (final, 2026-07-01)

```
stock_vault/00_CORE_LOGIC/
├── STOCK_USER.md              (stock-profile)
├── PERSONAL_USER.md           (personal_profile)
├── STOCK_CONTEXT.md           (stock-profile)
├── PERSONAL_CONTEXT.md        (personal_profile)
├── STOCK_MEMORY.md            (stock-profile)
├── PERSONAL_MEMORY.md         (personal_profile)
├── stock-profile_pre_edit_checklist.md
├── personal_profile_pre_edit_checklist.md
└── README.md                  (file mapping guide)

~/.hermes/profiles/
├── stock-profile/
│   ├── SOUL.md
│   ├── AGENTS.md
│   └── memories/MEMORY.md
└── personal_profile/
    ├── SOUL.md
    ├── PERSONAL_AGENT.md
    └── memories/MEMORY.md
```
