---
name: safe-automation-debugging
description: Debug automations without corrupting state or faking writes.
---

# Safe Automation Debugging

Debug automations that write to vault / GSheet / Telegram / DB. The #1 failure mode
in this class is **debugging by writing to production** — which dirties state, breaks
dedup, and makes the bug you're hunting look fixed (or unfixed) for the wrong reason.

## When to load
- Diagnosing why an automation dropped / duplicated / silently failed a write.
- Before reporting ANY external-write success (vault entry, GSheet row, git push, Telegram send).
- Reproducing a parser/cron failure locally.

## Core rules (HARD)

### 1. Verify-before-claim
Never report "synced / written / pushed / sent" without **running it + read-back evidence**.
- GSheet: after `sync_to_gsheet()`, call read-back (`_gsheet_read_dates`) and assert the date/row exists.
- Vault: `grep`/`read_file` the actual entry, don't trust the print statement.
- Telegram send: a returned `message_id > 0` means sent; for visibility, confirm the message is NOT a reply-hidden (see references).
- Git: `git log --oneline -1` to confirm the commit + `git status` clean.

Claiming success from a print string alone = lying. Bố will catch it ("con xạo").

### 2. No-real-writes-during-debug
NEVER call `write_vault` / `sync_and_commit` / `send_msg` FOR REAL while diagnosing.
- It dirties vault/GSheet/Telegram and — critically — a fake entry makes `is_duplicate()`
  return True, so the REAL message later looks like a dup and gets **dropped**.
- Use one of:
  - **Mock** the side-effect function (e.g. `p.send_msg = lambda *a, **k: 999`) and capture call args.
  - **Temp copy** of the target file; operate on the copy, diff, discard.
  - **Ad-hoc verify script** in `%TEMP%` named `hermes-verify-*.py`, run, then delete.
- After ANY manual real write during a test, immediately `git checkout -- <file>` to restore.

### 3. Don't guess the backend without evidence
"If it's a Telegram race / shared token / cron collision" are guesses until proven.
- Find what's actually consuming updates: `netstat -ano | findstr :PORT`, map PID → process via `tasklist` / PowerShell `Get-CimInstance`.
- Trace the real token: read the bot `.env`, never assume which bot is live.
- Real root causes are usually simple (standalone message not matched, draft sent as reply and hidden).

### 4. Ad-hoc verify, not suite-green
For one-off verification write a temp `hermes-verify-*.{py}` that mocks side-effects, asserts,
prints `PASS/FAIL`, then clean it up. Do NOT present this as a green test suite — say
"ad-hoc verify (not suite green)" so the claim level is honest.

## Debug sequence
1. **Preserve evidence** — capture current state (pending json, getUpdates count, vault hits) BEFORE touching anything.
2. **Reproduce** against a mock/fake, not production.
3. **Localize** — read the exact function source (`inspect.getsource`), don't guess.
4. **Fix** minimally; re-run mock verify.
5. **Verify on real** only at the end, with read-back, then commit scoped.

## Pitfalls (from capture-sleep case — see references/)
- **Standalone "ok" dropped**: `process_reply` only matched `reply_to_message_id`; Bố typed "ok" standalone → update consumed + dropped. Fix: match standalone msg from Bố in same 1-1 chat.
- **Draft sent as reply → invisible**: `send_msg(draft, reply_to=msg_id)` landed as a reply, hidden on Telegram. Fix: send draft as a standalone message (`send_msg(draft)`, no reply_to).
- **GSheet OAuth expired** → silent skip. Fix: Service Account (long-lived). See references for setup.
- **Cron window** `*/2 6-13` only runs 06:00–13:00. Outside that, manual force-run is required; don't assume "auto".
- **Fake debug write breaks dedup**: writing a test entry makes the real one look duplicated → dropped.

## References
- `references/capture-sleep-root-causes.md` — concrete reproduction recipes + the Service Account setup for GSheet.
