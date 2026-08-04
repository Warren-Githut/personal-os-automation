---
name: approval-gate-debug
description: "Debug Telegram approval flows when ok/skip/reply stalls."
tags: [debug, automation, telegram, approval-gate]
---

# Approval Gate Debug

## When to use

- Approval-gated draft flow appears stuck after user replies `ok`/`skip`/`edit`.
- Telegram poller cron shows `error`, but stderr/delivery error is hidden.
- User says “bot did not reply after `ok`”/“no Telegram feedback”, even though the poller script ran successfully.
- Skill docs reference one canonical script path, while wrapper/state files live elsewhere.

## Core technique

Use a **deterministic monkeypatch verify script**:

1. Import the real target module under test.
2. Replace side-effect surface with fakes: `get_updates`, `send_msg`, `write_vault`, `sync_and_commit`.
3. Seed pending state matching real schema (`proposal_msg_id`, `source_msg_id`, `data`, `ts`).
4. Call the exact handler path the cron runs (`poll_once`, `process_reply`, etc.).
5. Assert the full chain: reply accepted -> vault write -> notify -> sync/commit -> pending cleared.

## Verification recipe

| Step | Action |
|------|--------|
| A | Seed fake pending with `proposal_msg_id`, `source_msg_id`, `data`, `ts`. |
| B | Inject fake updates with matching `reply_to_message_id` and normalized `ok`/`skip`/`edit ...`. |
| C | Run the handler. |
| D | Assert success send text present, vault write once, sync/commit once, pending cleared. |
| E | Emit `VERIFY_RESULT: PASS|FAIL` and print observed call list. |
+
+### When user reports “no Telegram reply after `ok`”
+
+| Check | What it tells you |
+|-------|-------------------|
+| Poller `--once` log | Confirms whether the script saw updates at all. |
+| `.telegram_pending.json` after `--once` | If still `awaiting_approval` → reply was not consumed by handler. |
+| `getUpdates(offset=0)` empty | Either bot did not receive the reply, or it was consumed elsewhere. |
+| `send_msg` success, but Warren sees nothing | Delivery-side failure: Hermes Telegram platform/auth/reconnect issue. |
+
 ## Telegram-specific pitfalls

- **Envelope vs payload:** Real Telegram updates are `update -> message -> message_id/text/reply_to_message_id`. Handlers must read from `update.get("message")`, not treat `msg` as if `message_id` is top-level.
- **Path drift:** Skill docs often reference one path, while cron wrappers or state files live elsewhere. Inspect the filesystem before changing code.
- **Wrapper mismatch:** `no_agent=True` cron jobs may run a wrapper in `~/.hermes/scripts/` that calls the real script elsewhere. Verify the wrapper target exists before debugging wrapper logic.
- **Cron stderr blindness:** Job state may be `error` with no `last_delivery_error`. Reproduce manually in foreground first; only then inspect runtime logs.
- **State-file location:** Offset/pending JSON should sit beside the real script. Stale skill paths can still create/look for hidden files in old locations.

## Reusable probe pattern

```python
import unittest.mock
import telegram_health_poller as poller

fake_updates = [
  {"update_id": 12345, "message": {"message_id": 114, "text": "ok", "reply_to_message_id": 113}}
]

with unittest.mock.patch.object(poller, "get_updates", lambda offset: fake_updates), \
     unittest.mock.patch.object(poller, "send_msg", lambda text, reply_to=None: 115), \
     unittest.mock.patch.object(poller, "write_vault", lambda d: None), \
     unittest.mock.patch.object(poller, "sync_and_commit", lambda date: None):
  poller.save_pending({...})
  poller.poll_once()
```

## After verification

- Keep temp verify script under a `hermes-verify-` prefix.
- Remove it after the run; do not leave it in the repo.
- If PASS, manual run is the next step. If manual run still fails, suspect auth/network/env rather than handler logic.
