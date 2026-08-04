---
name: telegram-bot-reliability
description: Telegram poller reliability — consumer race, verify gate.
---

# Telegram Bot Reliability

## When to use
- Building or debugging a Telegram bot poller / capture-sleep / approval gate
- Bot "ignores" a user reply, or a draft is sent but confirm never arrives
- Symptom: `getUpdates` returns empty even though the user sent a message
- After ANY Telegram send / GSheet append / git push — before reporting success

## Core rules

### 1. One consumer per bot token (HARD)
Telegram Bot API delivers each update to **only one** `getUpdates` caller. If two
processes poll the same token, updates get split or silently consumed — the other
process sees `getUpdates` return empty.

- Do NOT run a long-poll poller AND a cron `--once` poller on the same token
- Do NOT let Hermes Gateway poll a token your script also polls
- Debug "who eats my updates": `netstat -ano | findstr 149.154`, then
  `Get-CimInstance Win32_Process -Filter "ProcessId=PID" | Select CommandLine`
  to see which script owns the connection

### 2. Reply matching must handle STANDALONE messages (HARD)
Users often send "ok" / "skip" as a **plain message**, not a reply to the draft.
`reply_to_message_id` will be `None` → a matcher that only checks `reply_to` drops
the confirmation and the update is consumed forever.

Match by: `chat_id` + `from.id` (human, not bot) + normalized text, OR `reply_to`
in (proposal_id, source_id). Accept variants: ok/yes/okay/y and skip/no/n.
Normalize by lowercasing and stripping non-alphanumerics (drops emoji/spaces).

### 3. getChatHistory is NOT a Bot API method (404 trap)
`tg_api("getChatHistory", ...)` returns HTTP 404. Bots cannot read chat history
via the Bot API. The only ways to receive messages are `getUpdates` (long-poll) or
a webhook. Do NOT write a "scan history" fallback using getChatHistory — it will
always 404 and silently fail. Fix the consumer race (rule 1) instead.

### 4. Verify-before-claim gate (HARD — user-correction driven)
After ANY action with a real-world consequence, verify the ACTUAL external state
before telling the user it worked. Claiming success from a return code or a
printed string is not verification.

| Action | Verify by |
|--------|-----------|
| `send_msg` | returned message_id is not None AND (optionally) re-read chat |
| GSheet append | re-read the sheet tab, confirm the new date row exists |
| git push | `git log` / `git status` on the remote, or `git ls-remote` |
| vault write | re-open the file, grep for the new entry |

**The "xạo" trap (real incident):** a pipeline printed "✅ sync GSheet" every run,
but the OAuth token had expired (`invalid_grant: Token has been expired or
revoked`). The `try/except` swallowed the error and returned 0, so the commit
message lied. Fix: make `sync_and_commit` surface the failure, and re-read the
sheet before claiming sync.

### 5. Decision clarity (user-correction driven)
When multiple approaches exist (e.g. "keep old bot" vs "create new bot"), PICK ONE,
state it, and do not leave the choice ambiguous. Do not start work on path A while
the user thinks you are on path B. If you decide to abandon a planned change
(e.g. bot migration), say so explicitly and why.

## Debug recipe (order)
1. `getMe` — token valid?
2. `getUpdates(offset=0, limit=50)` — does the user's message appear? If empty →
   consumed by another process (rule 1) or already dropped.
3. Check pending state file — is a draft awaiting approval?
4. Check `send_msg` return — did the bot actually send?
5. For GSheet: re-read the tab; if token error, switch to Service Account.

## Boundaries
- Never claim a side-effect succeeded without verifying external state
- Never long-poll a token that another process also polls
- Don't use getChatHistory in bot code
- Prefer Service Account JSON key over OAuth for cron/24-7 automations (no expiry)
