---
name: personal-telegram-automation
description: "Personal_OS Telegram capture-sleep and automation debugging."
version: 1.0
tags: [telegram, automation, cron, capture, personal_os]
---

# Personal Telegram Automation

## Purpose
Class-level guidance for reliable Telegram automation in Personal_OS, with emphasis on capture-sleep and poller debugging.

## Canonical Bot Selection

Lock one Telegram bot as canonical for Personal_OS capture/notify flows.

Rules:
- Use only `LUsinePersonalBot/.env` for token in Personal_OS vault scripts.
- Do not fall back to Hermes `.env`, `os.getenv("TELEGRAM_BOT_TOKEN")`, or other bots.
- Verify identity with `/getMe` before wiring a new flow.

Evidence:
- canonical bot id: `8426571365`
- canonical username: `personal_life_botbot`
- canonical link: `https://t.me/personal_life_botbot`

Mismatch signal:
- If Hermes gateway logs show a different bot id/token than `8426571365`, treat that as backend/auth mismatch, not poller script issue.

## Cron Wrapper Pattern

Hermes cron requires task entrypoints under `~/.hermes/scripts/`.
Keep real logic in `personal_vault/scripts/` so it can import vault-local modules.

Pattern:
1. Wrapper script calls vault script with `--once`.
2. In cron:
   - use existing wrapper or absolute vault script path
   - set `workdir` to the script cwd
   - set `no_agent: true`
   - do not assume nested `scripts/scripts/...`

## Confirmation Gate Flow

States: `awaiting_approval` -> `approved` / `skipped`

Flow:
1. New tagged message -> parse -> draft -> proposal message
2. Save pending state file with `proposal_msg_id`
3. Next poll:
   - look for replies to `proposal_msg_id`
   - `ok` -> write vault entry -> send confirmation -> clear pending
   - `skip` -> clear pending
4. Timeout auto-clear only if explicitly approved.

## Debug Evidence Path

Order of inspection:
1. Script state: `.telegram_offset.json`, `.telegram_pending.json`
2. Run one poll cycle directly with actual environment
3. Check Telegram queue with canonical token via `getUpdates`
4. Check Hermes gateway logs only if script side is clean

Interpretation rules:
- Script `--once` returns 0 and pending is False -> script did not see a reply to process
- `getUpdates` returns 0 updates while user says they replied -> delivery/routing/auth issue, not a parser bug
- Do not conclude script failure from tool-side evidence alone when vault/GSheet side may still succeed

## Verification Gates

Before reporting success or failure:
- confirm pending state after run
- confirm vault entry or GSheet row count changed
- confirm Telegram send response id, not just stdout
- clean temp verify scripts after use

## Pitfalls

- Multiple Telegram tokens/configs create silent routing mismatches.
- Double `scripts` paths in cron config cause executable-not-found failures.
- `getUpdates` returning 0 does not prove the user did not send.
- Auto timeout pending without approval breaks confirmation trust.
- `reply_to_message_id` must come from the proposal, not only the source message.
