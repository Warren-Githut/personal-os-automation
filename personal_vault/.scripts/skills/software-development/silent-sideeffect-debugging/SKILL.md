---
name: silent-sideeffect-debugging
description: Side-effect worked but no reply? Narrow except is the bug.
version: 1.0.0
trigger: User says "it worked but no reply" or "data changed but bot went silent".
---

# Silent Side-Effect Debugging

> Class-level debugging pattern. When an action should produce BOTH an external side-effect
> (DB write, GSheet append, API POST) AND a confirmation message, but only the side-effect
> lands and the user gets silence — the bug is almost always a **narrow exception handler
> swallowing a post-side-effect error**. This skill is the reusable capture of that pattern.

## The Signature Symptom

```
User: "I clicked ok / sent the command / approved it."
System: external state CHANGED (row appears, file written, API data updated)
User: "but the bot/app said nothing — no confirmation, no error."
```

This is NOT "it didn't work." It's "it worked PARTIALLY and the confirmation path died."

## Root Cause (the universal shape)

```
try:
    side_effect()        # ← happens FIRST, lands external state
    local_mutate()       # ← or this
    confirm()            # ← NEVER reached because something above raised
except ImportError:      # ← narrow catch: only ONE error class
    pass                 # ← broad exceptions ESCAPE → confirm() never fires
```

The handler performs the side-effect, then later raises a DIFFERENT exception class than the
one the `except` catches. The exception escapes, the confirmation never sends, but the
side-effect is already durable. The user sees the state change but hears nothing.

## Diagnostic Steps (reproduce → localize → fix)

### 1. Reproduce without the bot/UI
Call the handler function directly with a synthetic state file. Swap the real state file
for a minimal one, invoke the entry point, observe the return value / exception.
- If it returns a confirmation string → the happy path is fine; the bug is in the CALLER's
  exception handling (narrow `except`).
- If it raises an exception that the caller's `except` doesn't catch → you found it.

### 2. Localize the narrow catch
Grep the caller for `except <SingleClass>` around the handler invocation. Common narrow
catches that hide real errors: `except ImportError`, `except KeyError` (when the real error
is a network/`gspread`/`ValueError`), `except FileNotFoundError`.

### 3. Fix — broaden + always surface
```python
try:
    result = handler(text, user_id)
    if result:
        await message.answer(result)
        return
except ImportError:
    await message.answer("⚠️ Handler module missing.")
    return
except Exception as e:
    log.exception("❌ handler crashed")          # retain traceback in logs
    await message.answer(                          # ALWAYS tell the user
        f"⚠️ Lỗi khi xử lý: {type(e).__name__}: {str(e)[:160]}\n"
        f"(Nếu side-effect đã xảy ra mà không có confirm, check duplicate trước khi thử lại.)"
    )
    return
```
- Catch `Exception` (keep `ImportError` as its own branch only for a distinct message).
- `log.exception` so the traceback survives even when the user message is truncated.
- NEVER let a post-side-effect path fail silently — the user MUST see success OR failure.

### 4. Defense-in-depth — durable status flag
Any handler that performs a side-effect then mutates local state MUST set a durable status
flag immediately after the side-effect succeeds, so a retry cannot re-run it.

```python
side_effect()                      # GSheet append
entry["status"] = "approved"       # ← set THIS so _get_latest_pending won't re-pick
```

Without it, a second "ok" re-appends a DUPLICATE row. (Seen 2026-07-26: review bot appended
twice because new-flow entries stayed `status="notified"` after approve.)

## Real Reproduction (L'Usine review bot, 2026-07-26)

Full recipe + exact diff: `references/narrow-except-swallows-sideeffect.md`

TL;DR: `telegram_bot.py` wrapped `handle_review_message` in `try/except ImportError: pass`.
The handler appended to GSheet, then raised a non-ImportError → bot silent, Warren saw the
GSheet row but no "Da post review len GSheet!" confirm. 1:1 with *"bố ok, bot ko trả lời là
đã append vào gsheet."* Fix: broaden to `except Exception` + set `status="approved"`.

## Guard Rules (carry into every side-effecting handler)
1. Catch `Exception` (not just `ImportError`) around any handler that does I/O.
2. `log.exception` so the traceback is retained even when the user message is truncated.
3. Always `message.answer(...)` / return a value on BOTH success and failure — never silent.
4. After a side-effect succeeds, set a durable status flag so a retry cannot re-run it.

## Related
- `debugging-and-error-recovery` — parent methodology (reproduce → localize → fix → guard).
  NOTE: that skill is manually-authored and locked for autonomous curation; this skill
  captures the side-effect-confirmation sub-pattern as a standalone, since the parent could
  not be patched this session.
