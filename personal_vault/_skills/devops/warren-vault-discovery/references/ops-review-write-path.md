# ops-review GSheet Write Path (concrete)

Source files (warren-profile, NOT editable from personal_profile session):
- Skill: `AppData/Local/hermes/profiles/warren-profile/skills/ops/ops-review/SKILL.md` (v2.7)
- Handler: `Warren_OS_Local/vault/.scripts/review_response_handler.py`
- Parser (readonly): `Warren_OS_Local/vault/10_OPERATION_DATA/.parsers/google_review_parser.py`

## The readonly-vs-write scope trap (P2)
- `google_review_parser.py` reads the GSheet with scope `spreadsheets.readonly`
  and uses SA key `vault/.private/lusine-calendar-sa-key.json`.
- `review_response_handler._append_to_gsheet()` uses the SAME SA key but with
  scope `https://www.googleapis.com/auth/spreadsheets` (WRITE). It does
  `values().update(range='05_Google_Review_Weekly_Log!A{last_row}', RAW)`.
- Conclusion: the pipeline CAN write. A readonly parser scope does NOT imply
  the pipeline is unwritable. Check the actual write function, not the parser.

## SSOT GSheet
- Spreadsheet ID: `1ZtIocc_Ic1z-tO1JGd4ZLnRB_7ZHHkvpJ5emaWJyeEE`
- Tab: `05_Google_Review_Weekly_Log` (gid `762945748`)
- 17 columns A:Q. The handler appends a `csv_row` list of 17 strings.

## Two intake channels, one write path
1. **Telegram** `[ops-review]` → review-queue-watcher cron parses → builds
   `csv_row` → `review-telegram-sender` asks Warren to approve on Telegram →
   Warren replies "ok" → `handle_review_message("ok")` → `_append_to_gsheet`.
2. **Hermes chat paste (Manual Chat Intake, SKILL §435-481)** → GG parses inline
   → presents Part 1/3/4 → Warren replies "ok" → GG runs Direct Chat Approval
   (Step 10): build entry dict, call `_append_to_gsheet(csv_row, raw_text)`
   directly, then append to `review_queue.json` history. No `approval_message`
   field, no Telegram send, so `verify_review_entry.py` is SKIPPED.

## Direct append invocation (chat-paste flow)
```bash
cd /c/Users/khoans/Documents/Warren_OS_Local/vault/.scripts
python3 -c "
import sys; sys.path.insert(0, '.')
from review_response_handler import _load_queue, _append_to_gsheet
# target = entry with the csv_row to append
success, info = _append_to_gsheet(target['csv_row'])
print(f'success={success}, info={info}')
"
```

## Guards inside `_append_to_gsheet`
- `validate_review_entry()`: BLOCKS if ★ glyph count in raw_text != rating in
  csv_row[3]; non-blocking WARNING if competitor brand cited.
- Writes a temp .py in `.scripts/`, runs, then `rm -f` (never leave scratch).
