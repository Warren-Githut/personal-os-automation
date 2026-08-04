---
name: gsheet-personal-sync
description: "Sync Personal_OS vault data (sleep logs, etc.) to Warren's Google Sheets. Covers tab-title resolution, idempotent append, Drive hard-delete, and OAuth re-auth after token revocation. Use when pushing vault data to GSheets or debugging google-workspace calls. The bundled `google-workspace` skill is protected — this captures the working extras."
version: 1.0
tags: [google, sheets, drive, automation, personal_os]
---

# GSheet Personal Sync

Working patterns for syncing Personal_OS vault data to Warren's Google Sheets,
distilled from real debugging (2026-07). The parent `google-workspace` skill is
bundled/protected, so the extras live here.

## When to use
- Pushing vault logs (e.g. `10_PULSE/051_Sleep_Log.md`) to a GSheet tab
- Debugging `sheets get` "Unable to parse range" or `drive delete` 403
- Recovering after `invalid_grant` / token revoked

## Core patterns (see references/working-patterns.md)
1. **Tab title, not GID** — ranges must use the tab TITLE (`'W-capture-sleep'!A1:H30`), not the numeric GID. Resolve via `spreadsheets().get()`.
2. **Idempotent append** — read column A for existing keys, append only missing rows.
3. **Drive hard-delete** — CLI `drive delete` trashes via `files().update` and 403s if Drive API disabled; call `files().delete(fileId)` directly, or enable Drive API first.
4. **Re-auth after revocation** — `setup.py --auth-url` takes NO `--services`/`--format` flags (rejected); run it bare, approve, paste full redirect URL to `--auth-code`.

## Pitfalls
- **NEVER test a live GSheet/vault write with fabricated data** — it pollutes both and forces manual cleanup. Verify the sync path idempotently: on an up-to-date sheet, `sync_to_gsheet()` must return 0 rows and touch nothing.
- Confirmation gate: a non-interactive script cannot prompt. Encode the "ask Warren first" rule as an explicit opt-in flag (e.g. `--sync-gsheet`); Hermes only passes it on a turn Warren explicitly approved a GSheet write.

## References
- `references/working-patterns.md` — quoted snippets for tab-title, idempotent append, Drive hard-delete, re-auth.
