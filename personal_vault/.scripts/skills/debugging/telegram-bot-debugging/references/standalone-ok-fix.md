# Standalone "ok" fix — Telegram capture bot

## Symptom
User sends `[capture-sleep] ...` → bot drafts proposal → user types `ok` → bot stays silent, pending hangs forever.

## Real root cause (NOT token sharing)
`process_reply` only matched `m.reply_to_message_id in (proposal_msg_id, source_msg_id)`.
User typed `ok` as a STANDALONE message (no reply thread) → `reply_to_message_id is None` → no match → `getUpdates` consumes the update → it is dropped permanently. Next poll sees `COUNT: 0`.

Changing the bot token does NOT fix this. The handler shape is the bug.

## Fix (verified 2026-07-31, commit f6fdc17)
Match reply OR standalone confirm from the human in the same 1-1 chat:

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
        write_vault(pending["data"])
        send_msg(f"✅ Đã ghi vault {pending['data']['date']} + sync GSheet + git push.", reply_to=prop_id)
        sync_and_commit(pending["data"]["date"])
        save_pending(None)
        return
    elif txt in ("skip", "no", "n"):
        send_msg("⏭️ Đã bỏ qua.", reply_to=prop_id)
        save_pending(None)
        return
```

## Verification that counted as real
- `getUpdates(offset=0)` against live token returned `COUNT: 0` even after reset → confirmed update was consumed, not a token issue.
- Force-run with seeded pending + standalone `ok` via mocked `get_updates` → PASS (logic).
- End-to-end: seeded pending, user sent real `ok` standalone, cron/force-run → vault entry `2026-07-30` written, GSheet synced, git commit `24961ae` pushed. THIS is the proof, not the mocked test.

## Caveat
Standalone match is not thread-scoped: any standalone "ok" in the chat while a pending exists will approve. Fine for single-user capture bot. If multi-user, scope by `source_msg_id`/thread instead.
