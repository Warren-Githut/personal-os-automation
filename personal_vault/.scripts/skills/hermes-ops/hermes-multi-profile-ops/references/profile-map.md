# Profile Map — Warren's 3 Hermes Profiles (verified 2026-07-09)

Base: `C:\Users\khoans\AppData\Local\hermes\profiles\`

## Skills directories
- `warren-profile/skills/` — CANONICAL. Real dir. All shared skills live here.
- `stock-profile/skills/` — **symlink → warren-profile/skills**. Edits land in warren-profile.
- `personal_profile/skills/` — Real dir. Independent copies only.

## Shared parser / personal-commands skills (in warren-profile/skills/personal-commands/)
All profiles use these via the warren-profile home:
- `capture-sleep` (health/sleep logs from Telegram)
- `legal-document-ingest`
- `stock-capture` (broker email → vault)
- `bctc-pdf-ingest` (financial statements)
- `personal-morning-brief` / `personal-morning-brief-fixed`
- `personal-weekly-connections`
- `personal-context-update`
- `personal-case-lifecycle`
- `telegram-capture-gate`
- `stock-deploy-capital`

## Shared data-science skills (warren-profile/skills/data-science/)
- `verify-parser-output` — loaded by stock-profile via symlink; personal_profile may carry its own copy.
- `luso-parsers`

## Memory files (vault, NOT profile folder)
Location: `C:\Users\khoans\Documents\Personal_OS\personal_vault\00_CORE_LOGIC\`
- `PERSONAL_MEMORY.md` (SSOT for personal_profile)
- `PERSONAL_USER.md` (Warren profile for personal_profile)
- `PERSONAL_CONTEXT.md`
- `STOCK_MEMORY.md` (SSOT for stock-profile)
- `STOCK_USER.md` (Warren profile for stock-profile)
- `STOCK_CONTEXT.md`

Warren-profile vault (`C:\Users\khoans\Documents\Warren_OS_Local\vault\00_CORE_LOGIC\`):
- `USER.md`, `WARREN_MEMORY.md`, `CONTEXT.md`, `TODAY.md`

## Guard behavior
- `patch` / `write_file` / `skill_manage` from a non-owner profile → soft guard blocks (e.g. editing warren-profile's verify-parser-output from personal_profile session).
- `terminal` writes bypass the guard.
- SOUL.md files are per-profile real files → editable from their own session unguarded.
