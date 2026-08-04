---
name: telegram-sender-e2e-testing
description: "E2E-test no_agent Telegram queue senders safely."
status: active
created: 2026-07-26
version: 1.0
triggers:
  - test no_agent telegram sender
  - e2e test queue sender script
  - add new telegram content from llm cron
  - extend review_telegram_sender.py
  - telegram sender queue mutation test
---

# telegram-sender-e2e-testing

Class-level skill for safely validating `no_agent=True` Telegram sender scripts that mutate a shared queue file, and for the canonical pattern of forwarding new LLM-generated content to Telegram via a no_agent forwarder (instead of giving the LLM cron the token).

## When to use
- You edited `review_telegram_sender.py`, `col_telegram_intake.py`, or any `no_agent` script that reads a queue and calls `sendMessage`.
- You need to add a NEW Telegram-delivered output from an LLM cron (insight block, digest, alert) without violating the safety invariant.

## Hard rule (safety invariant)
The LLM cron MUST NEVER hold the Telegram token. Token lives only in `no_agent=True` deterministic scripts. To deliver new LLM content: LLM writes a new queue field; the no_agent script forwards it. This prevents NOOP-run spam.

## E2E Swap-Test (validate queue mutation + delivery safely)
Never run the sender against live data. Swap in a disposable test queue, run, verify state, restore.

Full recipe + delivery-confirm snippet: `references/e2e-swap-test.md`

Key steps:
1. Backup live queue (`cp` to /tmp).
2. Build minimal test queue (one entry with the fields the script reads, e.g. `approval_message` + `insight_message`), written to `$LOCALAPPDATA/../Temp/` — MSYS `/tmp` is unreliable on Windows and silently drops writes.
3. `mv` live queue aside, `cp` test queue into place.
4. Run script; capture exit code.
5. Verify: `status` flipped, `sent_at`/`insight_sent_at` stamped, source fields popped.
6. Restore live queue (`mv` backup back); `rm` temp.

## Confirm delivery
Webhook-configured bots return empty `getUpdates` — do NOT rely on it. Send a tiny confirmation ping and assert `sendMessage` returns `ok:true` + a real `message_id`. See `references/e2e-swap-test.md`.

## New Telegram field via no_agent forwarder (pattern)
1. LLM writes content into a NEW queue field (e.g. `insight_message`). Never gets the token.
2. Extend the no_agent sender: scan that field when `<field>_sent_at` absent → `send_telegram()` → stamp `<field>_sent_at` + `<field>_message_ids` → pop the field.
3. Silent when the field is absent (no NOOP spam).
Canonical example: `review_telegram_sender.py` forwarding STEP 9 review insights (verified 2026-07-26: msg_id 1130 approval + 1131 insight, queue state correct, live queue restored intact).

## Pitfalls
- Windows MSYS `/tmp` drops writes silently — use `$LOCALAPPDATA/../Temp/` or `$TEMP`.
- `getUpdates` empty on webhook bots — confirm via `sendMessage` return, not polling.
- Forgetting to restore the live queue → real review entries corrupted. Always `mv` backup back.
- no_agent scripts: no emoji in print (mojibake gate); plain text (no parse_mode) for messages quoting vault paths with `_`.

## Related
- `telegram-py-checklist` — format/approval/token/queue gates (manually-authored, protected — read-only).
- `ops-review` — review queue architecture (pinned, protected — read-only).
- `ops-col` — sister COL queue watcher.
