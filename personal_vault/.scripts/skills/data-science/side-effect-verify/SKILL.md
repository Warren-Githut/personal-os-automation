---
name: side-effect-verify
description: >-
  Verify writes before claiming success. After sync or push.
version: 1.0
tags: [verification, side-effect, gsheet, telegram, git, proof-of-work]
---

# side-effect-verify — Prove the Write Happened

> **Warren caught this bug in-session:** agent reported "✅ synced GSheet + git
> push" but the GSheet OAuth token was expired and `sync_to_gsheet` silently
> failed (exception swallowed by `try/except`, returned 0). The vault write and
> git commit WERE real; the GSheet claim was fabricated. Bố said "con xạo bố".

A parser result with no verification is untrusted (`verify-parser-output` covers
NUMBERS). This skill covers EXTERNAL WRITES — a separate, equally fatal class.

## HARD RULE
Absence of an exception is NOT proof of success. Claim "synced / sent / pushed /
written" ONLY after verifying the EXTERNAL STATE actually changed.

## Per-target checks
- **GSheet append** — after `sync_to_gsheet()`, READ BACK the sheet (query
  existing dates) and assert the target date/row is present. A function that
  returns 0 rows because auth failed is NOT "synced".
- **Telegram send** — assert `send_msg()` returns a non-None `message_id`. That
  proves the API accepted it.
- **git push** — assert local HEAD == `origin/<branch>` (capture `git push`
  returncode 0 AND verify remote). A local commit alone is NOT a push.
- **vault write** — read the file back, assert the new entry / line is present.

## Swallowed-exception trap
`try: sync(); except Exception: print("warn")` hides failure. Treat a swallowed
exception as FAIL — either propagate it or emit "GSheet sync FAILED: <reason>".
Never let a warning-print hide a real error from the report.

## Emit side-effect report
```
SIDE-EFFECT VERIFY [capture-sleep 2026-08-01]:
  vault entry:     PRESENT (line 18)
  GSheet row:      PRESENT | ABSENT (read-back — must check, not assume)
  Telegram confirm: sent msg_id=201
  git:             pushed <sha> == origin/master
  RESULT: PASS | FAIL
```
No SIDE-EFFECT report = the claim is UNTRUSTED. Do not tell Warren it worked.

## Concrete recipes (GSheet / Telegram / git)
See `references/side-effect-verify.md` for copy-paste probes + the
swallowed-exception anti-pattern.

## Integration
- Automation / capture skills (telegram-capture-gate, capture-sleep,
  bctc-pdf-ingest, gsheet-personal-sync) MUST run this gate after any external
  write and include the SIDE-EFFECT report in their delivery.
- Cron jobs that sync must report SIDE-EFFECT result, not just "done".
- Complements `verify-parser-output` (numbers) — both are mandatory before
  claiming success to Warren.
