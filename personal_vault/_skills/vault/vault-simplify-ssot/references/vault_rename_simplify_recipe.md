# Vault Rename / Simplify — Reusable Recipe (condensed, 2026-07-25)

## Problem solved this session
Warren asked to (a) rename agent "Con" from HORION -> **GG** (keep system name "Hermes"), and (b) simplify `00_CORE_LOGIC` (dedup WARREN_MEMORY, sync ANCHORS, fix conflicts). Two tool traps surfaced that are NOT yet covered by the MSYS workaround:

### Trap 1 — `search_files` GHOST INDEX
- Ran `search_files(target='files', pattern='*')` in `00_CORE_LOGIC` -> returned `COST_LOG.md` + `AUTOMATION_HEALTH.md`.
- `terminal ls` / `find` ground-truth -> those 2 files DO NOT EXIST (only 8 real files).
- Tool returned **phantom** entries (stale index). Unlike the known "empty/IO error" mode, the tool *succeeds* with wrong data.
- **Rule:** never trust `search_files` for structural discovery. Always `ls`/`find`/`grep` via terminal.

### Trap 2 — UNBOUNDED VAULT GREP EXPLODES
- Ran `grep -r "HORION" vault` -> **640,820 chars**, all from `_archives/` (`sessions_cron_*.jsonl`, `soul`/`skills` backups) + `.smart-env/*.ajson` + dead session logs.
- Timeout 60s, output useless, risk of mangling internal Hermes files.
- **Rule:** bound grep to active folders; never `grep -r` the whole vault.

## Reusable bounded-grep command (copy-paste)
```bash
cd /c/Users/khoans/Documents/Warren_OS_Local
# 1. active md only (exclude archives/smart-env/sessions)
grep -rln "TỪ_KHÓA" vault/00_CORE_LOGIC vault/10_OPERATION_DATA vault/30_KNOWLEDGE_BASE \
  vault/_cases vault/_inbox vault/_ideas vault/_growth vault/_journal 2>/dev/null
# 2. .scripts parser (dotfolder -- search_files blind)
grep -rln "TỪ_KHÓA" vault/.scripts 2>/dev/null
# 3. system files (SOUL/AGENTS live OUTSIDE vault repo)
grep -n "TỪ_KHÓA" /c/Users/khoans/AppData/Local/hermes/profiles/warren-profile/SOUL.md 2>/dev/null
# 4. verify residual (must be EXIT=1)
grep -rn "TỪ_KHÓA_CŨ" <bounded scope>; echo "EXIT=$?"
```

## Rename execution checklist (proven)
1. Bounded grep -> list every active occurrence + file.
2. `read_file` each before patching (ground truth).
3. Patch (batch parallel if independent).
4. Re-grep -> confirm 0 residuals (EXIT=1).
5. Memory tool: if removing entries -> `memory action=remove` -> **staged pending** (Warren must `/memory approve`; never auto-delete).
6. Commit-Push Gate (SOUL §5.3): print Q1/Q2, wait for Warren "ok".

## Rename map applied (HORION -> GG) — template for future renames
| Where | Change |
|-------|--------|
| USER.md (profile) | "HORION đọc/hướng dẫn" -> "GG (Hermes) đọc/hướng dẫn" x2 |
| USER.md §3 | "với HORION" -> "với GG (Hermes)" |
| USER.md §3 Xưng hô | "HORION là Con" -> "GG (Hermes) là Con" |
| USER.md §4 | row "Hermes -> Warren: mày/tao" -> "Bố/Con, dạ thưa" (deleted conflict with BỐ/CON rule) |
| USER.md §4 | "HORION -> Warren" -> "GG -> Warren (Bố)" |
| USER.md §4 tone block | "HORION tone" -> "GG (Hermes) tone"; "Warren là Bố, HORION là Con" -> "GG (Hermes) là Con" |
| System name "Hermes" | UNTOUCHED (SOUL §5 hard constraint: profile/bot/skills/cron/runtime). Only the *call-name* Con changed. |
| `_archives/` + `.smart-env/` | LEFT AS-IS (Warren: "HORION đã archive"). Do not touch dead backups. |

## Verify output (this session, all PASS)
- `grep -rn "HORION\|mày/tao" <active vault>` -> EXIT=1 (0 matches)
- `## 🔄 Chu kỳ này` in WARREN_MEMORY -> removed (moved to `_inbox/warren_memory_raw.md` per its own rule)
- ANCHORS A11 (GSheet Guard) + A12 (Data Latency) added -> 4 refs
- WARREN_MEMORY 178->175 lines; frontmatter dates synced to 2026-07-25
