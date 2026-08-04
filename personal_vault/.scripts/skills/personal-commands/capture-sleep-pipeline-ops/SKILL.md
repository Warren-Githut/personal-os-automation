---
name: capture-sleep-pipeline-ops
description: "Capture-sleep reliability: ok-match, SA auth, verify gate."
version: 1.0
tags: [telegram, capture-sleep, gsheet, automation, reliability]
---

# Capture-Sleep Pipeline Ops

Class-level reliability playbook for the `telegram_health_poller.py` pipeline:
`[capture-sleep]` tagged Telegram message -> parse -> draft -> Bố "ok" ->
write vault + sync GSheet + git push. Distilled from the 2026-08 debugging
session where the bot ignored Bố's reply and the GSheet sync silently failed.

## When to use
- Debugging why capture-sleep "ignores" Bố's "ok" / never writes the vault
- Debugging why GSheet shows no new rows after a "✅ sync GSheet" message
- Setting up or hardening the Telegram->vault->GSheet automation
- After ANY send/append/push — before telling Bố it worked

## Incident 1 — bot ignores "ok" (root cause: STANDALONE message)
Bố gửi `[capture-sleep] ...`, bot drafts, Bố gõ "ok" as a **plain message** (not a
reply to the draft). `process_reply` only matched `reply_to_message_id` ->
no match -> update consumed by `getUpdates` and dropped forever -> pending stuck.

Fix (in `telegram_health_poller.py`): match `reply_to` in (proposal_id, source_id)
OR a **standalone** message from Bố in the same 1-1 chat (`reply_to is None`,
`chat.id == pending.chat_id`, `from` not a bot), text normalized to ok/yes/okay/y
or skip/no/n. Normalize by lowercasing + stripping non-alphanumerics (drops
emoji/spaces).

**Do NOT** write a "scan chat history" fallback with `getChatHistory` — that method
returns HTTP 404 for bots. Bots only receive via `getUpdates` or webhook.

## Incident 2 — GSheet "synced" but nothing written (root cause: expired OAuth)
Pipeline printed "✅ sync GSheet" every run, but `sync_to_gsheet` threw
`invalid_grant: Token has been expired or revoked` and the `try/except` swallowed
it -> commit message lied. Bố caught the "xạo" twice.

Fixes:
- `sync_and_commit` must print the ACTUAL row count and warn on 0/failure
  (`⚠️ GSheet sync returned 0 rows` / `⚠️ GSheet sync FAILED`). Never bare "✅".
- Switch GSheet auth to **Service Account** (never expires). Full recipe in
  `references/service-account-setup.md`. Key traps:
  - Wrong key file: JSON `client_email` must match the SA shown Enabled in GCP
    console, or you get `account not found`.
  - 403 after auth-OK = sheet not Shared with the SA email (Editor), not a key issue.
  - git-ignore the key with `scripts/config/` (folder), not a bare file entry
    (overridden by `scripts/`).

## Verify-before-claim gate (HARD)
Never report a side-effect succeeded without checking external state:

| Action | Verify by |
|--------|-----------|
| `send_msg` | returned message_id is not None |
| GSheet append | re-read the sheet tab, confirm the new date row exists |
| git push | `git log` on the remote / `git ls-remote` |
| vault write | re-open file, grep for the new entry |

Run verification via a temp `hermes-verify-*.py` script, then delete it. Ad-hoc
verify, not suite green.

## Boundaries
- One consumer per bot token (no 2 processes polling the same token)
- Never claim success from a return code / commit message alone
- Prefer Service Account over OAuth for cron/24-7 syncs
- Never commit the SA JSON key

## References
- `references/service-account-setup.md` — GCP SA creation, google_api.py branch,
  sheet share, git-ignore, wrong-key trap, ad-hoc verify snippet.
