# Narrow `except` Swallows Side-Effect Confirmations (Pitfall + Recipe)

**Symptom:** An action should produce an external side-effect (DB write, GSheet append, API POST) AND a confirmation message. The side-effect happens, but no confirmation appears — the system "silently succeeded then went quiet." User can't tell if it worked.

**Root cause:** A caller wraps a handler in a narrow `try/except` that only catches one error class (e.g. `except ImportError`), but the handler performs the side-effect FIRST, then later raises a DIFFERENT exception (network error, `KeyError`, `gspread.Error`, `ValueError`). The broad exception escapes the narrow handler → propagates up → the confirmation/answer never fires. The side-effect already landed, so the user sees data change but no message.

## Real example (2026-07-26, L'Usine review-approval Telegram bot)

`telegram_bot.py` wrapped the review-approval handler:
```python
try:
    from review_response_handler import handle_review_message as handle_review_approval
    review_result = handle_review_approval(text, message.from_user.id)
    if review_result:
        await message.answer(review_result)
        return
except ImportError:
    pass   # ← ONLY catches ImportError; everything else escapes
```

The handler (`review_response_handler.handle_review_message("ok")`) flow:
1. Loads queue, finds latest pending review entry (status="notified").
2. `_append_to_gsheet(csv_row, raw_text)` → **GSheet row appended (side-effect DONE)**.
3. Mutates `review_pending["approved_at"]` / `approved_by` in-place.
4. `_save_queue(review_queue)` → atomic write.
5. Returns confirm string `"Da post review len GSheet!..."`.

If any exception fired at step 3–5 (or even inside `_append_to_gsheet` after a partial write), it was NOT an `ImportError` → escaped → `message.answer` never called. Warren saw the GSheet row appear but got no Telegram confirmation. Exact 1:1 with the report: *"bố ok, bot ko trả lời là đã append vào gsheet."*

**Second bug found in same flow:** the new-flow entry lives in `history[]` (status="notified"), not `pending[]`. After approve, the code only set `approved_at`/`approved_by` but NOT `status="approved"`. `_get_latest_pending` re-picks any entry with `status=="notified" and not approved_at` → a second "ok" re-appended a DUPLICATE GSheet row.

## Fix applied
`telegram_bot.py` — broaden the catch + always surface:
```python
try:
    from review_response_handler import handle_review_message as handle_review_approval
    review_result = handle_review_approval(text, message.from_user.id)
    if review_result:
        await message.answer(review_result)
        return
except ImportError:
    await message.answer("⚠️ Review handler module không load được (ImportError).")
    return
except Exception as e:
    log.exception("❌ Review approval handler crashed")
    await message.answer(
        f"⚠️ Lỗi khi duyệt review: {type(e).__name__}: {str(e)[:160]}\n"
        f"Nếu GSheet đã append rồi mà bot không confirm, check duplicate trước khi 'ok' lại."
    )
    return
```

`review_response_handler.py` — set durable status after side-effect:
```python
review_pending["approved_at"] = _now()
review_pending["approved_by"] = "Telegram"
review_pending["status"] = "approved"  # so _get_latest_pending won't re-pick it
```

## Reproduction recipe (reusable)
Swap the real queue for a synthetic one, call the handler directly (no bot needed):
```python
# backup
import shutil, json, os, sys
Q = r"C:\Users\khoans\Documents\Warren_OS_Local\vault\_inbox\review_queue.json"
shutil.copy(Q, "/tmp/rq_real.json")
sys.path.insert(0, r"C:\Users\khoans\Documents\Warren_OS_Local\vault\.scripts")
import review_response_handler as r

# build 1 notified-unapproved entry with a VALID csv_row (rating must match ★ count)
test = {"pending": [], "history": [{
    "id": "DIAG", "status": "notified", "store": "LU3", "rating": "5",
    "reviewer": "Test",
    "csv_row": ["2026-07-26","LU3","Test","5","Google","Good review","No"]*2,
    "raw_text": "★★★★★ LU3 very good",
    "approval_message": "x", "sent_at": "2026-07-26T08:00:00", "insight_message": "x"
}]}
json.dump(test, open(os.environ["TEMP"]+"/rq_diag.json","w",encoding="utf-8"), ensure_ascii=False, indent=2)
shutil.move(Q, "/tmp/rq_real_swap.json"); shutil.copy(os.environ["TEMP"]+"/rq_diag.json", Q)

print(repr(r.handle_review_message("ok", 2117653672)))   # RUN 1 → confirm
print(repr(r.handle_review_message("ok", 2117653672)))   # RUN 2 → must be "Khong co gi dang cho approve" (no dup)

shutil.move("/tmp/rq_real_swap.json", Q)  # restore
```
Note: `csv_row` rating field (index 3) MUST equal the ★ count in `raw_text` or the validator BLOCKS (returns an error string, not a crash — that path is safe). Use a matching rating+stars to exercise the happy/append path.

## Guard rules (carry into any side-effecting handler)
1. Catch `Exception` (not just `ImportError`) around any handler that performs I/O.
2. `log.exception` so the traceback is retained even when the user message is truncated.
3. Always `message.answer(...)` on BOTH success and failure — never silent.
4. After a side-effect succeeds, set a durable status flag so a retry cannot re-run it.
