# Profile Memory: Audit & Consolidation

> Workflow for detecting contradictions between SOUL.md, STOCK_MEMORY.md/MEMORY.md, built-in memory, and USER.md after initial profile setup. Based on stock-profile session 2026-06-28.

## Signal: When to Run

- User says "check lại mâu thuẫn" or "có gì conflict ko"
- You just created/updated one of the files (SOUL.md, STOCK_MEMORY.md, USER.md)
- Built-in memory is near capacity (90%+)
- A previous search or action failed because of wrong path/assumption in memory

## Step 1: Gather All Sources

Read all 4 sources in parallel:

| Source | Location | Format |
|--------|----------|--------|
| SOUL.md | `profiles/<name>/SOUL.md` | Markdown |
| STOCK_MEMORY.md / MEMORY.md | `vault/00_CORE_LOGIC/STOCK_MEMORY.md` | Markdown (SSOT) |
| Built-in memory | Hermes `memory` tool state (shown at session start) | §-delimited, shown in MEMORY section |
| USER.md | `vault/00_CORE_LOGIC/USER.md` | Markdown |

If the built-in memory is inaccessible via the tool (e.g., drift), read the backing file directly:
`profiles/<name>/memories/MEMORY.md` (also §-delimited — no YAML frontmatter).

## Step 2: Contradiction Matrix

Cross-reference these dimensions:

| Dimension | What to check |
|-----------|---------------|
| **SSOT declaration** | SOUL.md vs STOCK_MEMORY.md — both agree on which file is SSOT? |
| **Sync mechanism** | SOUL.md mentions manual sync? Auto-sync? Both must agree. |
| **Vault root path** | All files reference the same absolute path? |
| **Confidence tags** | HIGH/MOD/LOW definitions match? |
| **Write governance** | When is auto-write allowed? Same rules? |
| **Workflow patterns** | e.g. stock-deploy-capital paths match actual vault structure |
| **Data contracts** | Integrity gate triggers, DATA_CONTRACT rules |
| **Profile boundaries** | What's in SOUL.md that belongs to another profile? |

**PITFALL:** The vault MEMORY.md (Warren_OS_Local) and STOCK_MEMORY.md (Personal_OS) are DIFFERENT profiles' files. SOUL.md references its own profile's SSOT; don't cross-check against another profile's MEMORY.md unless they share a vault.

## Step 3: Fix Order

Always fix SSOT first, then sync downstream:

```
1. Fix STOCK_MEMORY.md (vault) — this is the source of truth
2. Sync to built-in memory via memory(operations=[...]) — compact § format
3. Update USER.md if the correction changes user profile info
4. Optionally fix vault MEMORY.md (other profile) if shared path was wrong
```

**PITFALL — markdown contamination:** Do NOT copy vault STOCK_MEMORY.md (markdown with YAML frontmatter) directly to `memories/MEMORY.md`. The memory tool expects §-delimited format. If this happens:
- Read the backup (`.bak` file created by the tool on failure)
- Rewrite `memories/MEMORY.md` as clean § entries
- Then use memory tool normally for ongoing ops

## Step 4: Memory Consolidation (When Full)

When built-in memory is near 2,200 chars and you need to add new entries:

### Consolidation technique
1. **Identify overlapping entries** — e.g., "Vault root" + "stock-deploy-capital" both reference paths
2. **Merge into one** — combine related facts into a single, denser entry
   ```
   Before:
   Vault root: C:/.../Stock_OS/stock_vault.
   stock-deploy-capital: ... Scan: pulse + wiki/investing/VN_Equities ...
   
   After (merged):
   Vault root: C:/.../Stock_OS/stock_vault. stock-deploy-capital: ...
   ```
3. **Shorten verbose wording** — remove filler ("always", "never", "please", "make sure")
   - "HARD RULE: search_files/grep chỉ chạy trong path được chỉ định. TUYỆT ĐỐỐI ignore file ngoài path trừ khi Warren yêu cầu mở rộng. search_files mặc định path="" (cwd) chỉ được dùng khi Warren nói rõ."
   - → "HARD RULE: search_files/grep chỉ trong path chỉ định. TUYỆT ĐỐI ko search ngoài path trừ Warren yêu cầu. Mặc định path="" chỉ khi Warren nói rõ."
4. **Remove entries documented elsewhere** — if a fact is in STOCK_MEMORY.md (SSOT) and not needed for quick lookup, drop it from built-in memory
5. **Batch all changes** in one `memory(operations=[...])` call — all-or-nothing guarantee

### Target
- After consolidation: aim for ≤85% capacity (≤1,870 chars) to leave room for 1-2 new entries
- Minimum acceptable: ≤95% capacity

## Step 5: USER.md Creation from Existing Sources

When USER.md doesn't exist and you need to create it from scratch:

### Sources to extract from
| Source | What to pull |
|--------|-------------|
| **SOUL.md** | Communication style, hard rules, data contracts, integrity gates |
| **STOCK_MEMORY.md / MEMORY.md Preferences** | Warren's stock-specific preferences, valuation rules |
| **Built-in user profile** (session header) | Name, location, broker, current holdings, pet peeves |
| **STOCK_MEMORY.md Patterns** | Workflow preferences (deploy capital, ingest, research) |

### Template sections
```
## Thông tin cơ bản
- Name, location, investment style (Buffett/Munger etc.)
- Broker preferences (main + cross-check)
- Current portfolio state (watchlist only — NOT holdings)

## Giao tiếp (stock context)
- Language, format, tone, templates
- Pet peeves

## Yêu cầu dữ liệu
- Confidence tags
- Data preference (comparisons > absolutes, ratios > raw)

## Trading style
- Capital segregation rules
- Thesis requirements

## Stock workflow ưa thích
- Table of workflows: integrity gate, valuation, deploy capital, BCTC ingest, deep research
```

### After creating
1. Save to vault: `00_CORE_LOGIC/USER.md`
2. Copy to profile: `profiles/<name>/USER.md`
3. Update built-in user profile via `memory(target='user', ...)` — compact, under 1,375 chars
4. Add a line in STOCK_MEMORY.md §Write Governance noting USER.md exists

## Step 6: Verify

Create a temp verification script (`hermes-verify-<topic>.py`) that checks:
- All 4 sources exist and have valid frontmatter
- Vault root path is consistent across all sources
- Built-in memory is §-delimited (no markdown contamination)
- Built-in user profile is under 1,375 chars
- No circular sync paths (vault → memories/MEMORY.md → vault)
- SSOT declaration matches in SOUL.md + STOCK_MEMORY.md

Run, fix any failures, clean up the temp script.
