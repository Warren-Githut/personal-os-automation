---
name: telegram-bot-debugging
description: "Debug Telegram bot failures: getUpdates drop, mock≠real."
---

# Telegram Bot Debugging

## When to use
- A Telegram bot automation "doesn't respond" to user replies/approvals.
- A fix verified by mocked tests still fails in production.
- Diagnosing why `getUpdates` returns empty despite the user confirming they sent a message.

## Hard facts (verify before assuming)
1. **`getChatHistory` does NOT exist in Telegram Bot API** — calling it returns `HTTP 404`. It is a user-account (MTProto) method, NOT bot. Bots receive messages ONLY via `getUpdates` (long-poll) or a webhook. Any "scan chat history" fallback for a bot is fundamentally wrong.
2. **`getUpdates` is single-consumer per bot token.** Only ONE process should poll a given token. If two processes poll the same token, updates are split round-robin — one consumer gets the message, the other gets `null`. Unmatched updates are consumed and LOST permanently (they never reappear, even after resetting offset).
3. **Resetting offset to 0 does NOT recover lost updates.** It only changes where the next poll starts. If `getUpdates(offset=0)` returns `COUNT: 0`, the updates were already consumed by another consumer (or the handler didn't match the user's actual message shape).

## Root-cause patterns (most common)
- **Handler shape mismatch (real bug):** Code matches only `reply_to_message_id`, but the user sends a STANDALONE message (no reply). The update is consumed, doesn't match, and is dropped. Fix: also match standalone messages from the user in the same 1-1 chat.
- **Two consumers:** Another process (cron duplicate, long-running `pythonw`, or a second Hermes session) polls the same token. Verify with `netstat -ano | findstr 149.154` → `tasklist` / `Get-CimInstance Win32_Process` on the PID → check its command line and `.env` for the token.
- **Wrong token assumption:** Don't assume a process "eats updates" without evidence. Check actual config files (not just `config.yaml`) — tokens may be in `LUsine*/.env`, `hermes/.env`, etc.

## Debug runbook
1. Read pending state: `cat .telegram_pending.json` (proposal_msg_id, source_msg_id, chat_id).
2. Reset offset: write `{"offset": 0}` to `.telegram_offset.json`.
3. Run poller once: `python3 telegram_health_poller.py --once`.
4. Manually probe: `getUpdates(offset=0, timeout=0, limit=50)` via `tg_api`. If `COUNT: 0` → updates already consumed (see patterns above).
5. Check consumers: `netstat -ano | findstr 149.154` → map PID → process command line.
6. Confirm token source: grep all `LUsine*/.env` + `hermes/.env` for the bot token.

## Verification discipline (CRITICAL)
- A TDD test with **mocked** `get_updates`/`tg_api` returning fake data proves the logic runs — it does NOT prove the real flow works.
- MOCK-PASSING ≠ REAL-WORKING. An agent previously reported "verify PASS" for a `getChatHistory` fallback that 404s against the live API. That is a false positive.
- To verify for real: seed a pending, then either (a) test against the live API with a real message from the user, or (b) explicitly assert the API method exists (`getUpdates` only) before building a fallback on it.
- Use `verify-parser-output` gate, but feed it REAL side effects or clearly label mocks as non-production proof.
- **User frustration signal (HIGH PRIORITY):** When the user says "làm việc nghiêm túc", "root cause là gì", "con lộn xộn à", or "vì sao con lại [làm X] không phải [Y]" — STOP producing more mocked-green tests and go straight to LIVE-API evidence. An ad-hoc script that monkeypatches `get_updates`/`tg_api` and prints "RESULT: PASS" is NOT proof and reads as sloppy. Prove the real flow with `getUpdates(offset=0)` against the actual bot token, or a real user message end-to-end.
- **Decision discipline:** Do NOT run two parallel fix directions (e.g. "change bot token" AND "fix handler logic") without an explicit user decision. If you wrote a spec for direction A but pivot to B, SAY SO and get a yes/no. Silent pivot = "lộn xộn". Pick one, finish it, verify for real, then report which bot/token is actually in use.

## Concrete fix: standalone-message match
Root cause for "user typed ok but bot stayed silent": handler only matched `reply_to_message_id`, user sent STANDALONE (reply_to=None). The update is consumed, doesn't match, dropped. Fix pattern:
```python
prop_id = pending["proposal_msg_id"]
src_id = pending.get("source_msg_id")
chat_id = pending.get("chat_id")
for u in updates:
    m = u.get("message", {})
    rid = m.get("reply_to_message_id")
    is_reply_match = rid in (prop_id, src_id)
    is_standalone = (
        rid is None
        and chat_id is not None
        and m.get("chat", {}).get("id") == chat_id
        and not m.get("from", {}).get("is_bot")
    )
    if not (is_reply_match or is_standalone):
        continue
    txt = normalize_reply(m.get("text", "") or "")
    if txt in ("ok", "yes", "okay", "y"):
        # approve
    elif txt in ("skip", "no", "n"):
        # discard
```
Note: this makes the bot respond to ANY standalone "ok" in the 1-1 chat while a pending exists — acceptable for a single-user capture bot, but be aware it is not thread-scoped.

See `references/standalone-ok-fix.md` for the full symptom→root-cause→verified-fix writeup (commit f6fdc17).

## Pitfalls
- Don't build fallbacks on Bot API methods that don't exist (curl/check the method first).
- Don't present mocked-test green as production evidence to the user.
- Don't assume "another process eats updates" — prove it with netstat + PID + token check.
- Don't change bots/tokens as a fix when the real bug is handler shape mismatch.

## Overlap
- Complements `telegram-capture-gate` (capture design), `debugging-and-error-recovery` (general), `verify-parser-output` (verification gate). Those are not editable here; this skill holds the Telegram-specific failure modes.
