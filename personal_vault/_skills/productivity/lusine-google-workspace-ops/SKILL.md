---
name: lusine-google-workspace-ops
description: "L'Usine-aware Google Workspace setup and auth shortcut for Warren Ops sessions."
trigger: "/lusine-google-workspace-ops"
---

# L'Usine Google Workspace Ops

Khi cần dùng Google Calendar / Workspace trong môi trường L'Usine, dùng flow rút gọn này thay vì hướng dẫn user tự tạo OAuth client.

## Trigger

- Cần Calendar event, Drive upload, Sheets/Docs CRUD
- Token hiện tại thiếu hoặc chưa authenticate

## Pre-flight: Check ALL profiles for existing tokens

**Khi user nói "có OAuth rồi" nhưng `--check` ở profile hiện tại báo NOT_AUTHENTICATED:**

```bash
# Tìm token ở mọi profiles — ko chỉ profile hiện tại
find ~/AppData/Local/hermes/profiles -name "google_token.json" 2>/dev/null
find ~/AppData/Local/hermes -name "google_client_secret.json" 2>/dev/null
```

Nếu tìm thấy token ở profile khác:
1. Copy token: `cp <profile>/google_token.json <current-profile>/google_token.json`
2. Copy client secret (nếu có): `cp <path>/google_client_secret.json <current-profile>/`
3. Re-run `python setup.py --check`

Chỉ revoke + re-auth nếu token THIẾU scope cần thiết (vd: thiếu calendar scope).

## Rule: Check vault first

Luôn ưu tiên kiểm tra private vault:

```
vault/_private/
```

Nếu có sẵn file `client_secret_...apps.googleusercontent.com.json`, copy thẳng về và chạy setup:

```bash
$HERMES_HOME=/c/Users/khoans/AppData/Local/hermes/profiles/lusine-profile/home
mkdir -p "$HERMES_HOME/.hermes"
cp "C:/Users/khoans/Documents/Warren_OS_Local/vault/_private/<file>" "$HERMES_HOME/.hermes/google_client_secret.json"
```

Sau đó tiếp tục auth flow bình thường.

## Auth flow

```bash
python ${HERMES_HOME}/skills/productivity/google-workspace/scripts/setup.py --client-secret "$HERMES_HOME/.hermes/google_client_secret.json"
python ${HERMES_HOME}/skills/productivity/google-workspace/scripts/setup.py --auth-url
# gửi URL cho user duyệt, nhận lại URL hoặc code
python ${HERMES_HOME}/skills/productivity/google-workspace/scripts/setup.py --auth-code "<url_or_code>"
python ${HERMES_HOME}/skills/productivity/google-workspace/scripts/setup.py --check
```

## Alternative: Service Account (Calendar + Sheets)

L'Usine operations dùng **service account** (không phải OAuth) cho Calendar events **và Google Sheets**. Flow này nhanh hơn, ko cần browser auth. Dùng `vision_analyze` để kiểm tra path key.

### SA key actual path (verified 2026-06-30)

The SA key is NOT at vault/_private/ as previously documented. It lives at:

```
%LOCALAPPDATA%\hermes\google_service_account.json
# Resolves to: C:\Users\khoans\AppData\Local\hermes\google_service_account.json
```

Python load pattern (correct for this environment):
```python
from pathlib import Path
import os
SA_KEY = Path(os.environ['LOCALAPPDATA']) / 'hermes' / 'google_service_account.json'
```

### SA key limitation: CANNOT create new sheets

The service account has `spreadsheets` scope but NOT `drive` or `drive.file` scope. This means:

| Operation | Works? | Error if fails |
|-----------|--------|---------------|
| Read/write existing LU_COL_ENGINE_V4 sheet | ✅ Yes | — |
| Add a NEW tab to existing LU_COL_ENGINE_V4 | ✅ Yes | — |
| CREATE a brand new spreadsheet | ❌ No | 403 "The caller does not have permission" |

**Workaround:** When you need a new tracking sheet, add a tab to the existing LU_COL_ENGINE_V4 sheet:
```python
# Add a tab
body = {'requests': [{'addSheet': {'properties': {'title': 'Quick Wins Tracker'}}}]}
sheets.spreadsheets().batchUpdate(spreadsheetId=SHEET_ID, body=body).execute()

# Populate it
values = [['Date', 'Day', 'Covers', 'Target'], ...]
body = {'values': values}
sheets.spreadsheets().values().update(
    spreadsheetId=SHEET_ID, range="'Quick Wins Tracker'!A1:D40",
    valueInputOption='RAW', body=body,
).execute()
```

### OAuth token expiry pitfall

- **OAuth token expiry pitfall** — The user OAuth token at `warren-profile/google_token.json` (NOT `%LOCALAPPDATA%/hermes/` — that's the SA key path):
  - Has scopes for spreadsheets, drive, calendar, gmail
  - Uses `'token'` key (NOT `'access_token'`) — `Credentials.from_authorized_user_info()` handles this
  - **Likely expired** with refresh failing: "invalid_grant: Token has been expired or revoked"
  - Cannot be refreshed without user re-authentication via browser → run `vault/scripts/google_reauth.py` (opens browser, consent, overwrites token). **Cannot verify headless** — pass = Warren sees `REAUTH OK`.
  - 🔴 **Fallback to SA for CALENDAR is WRONG** (learned 2026-07-10): SA-created events land under SA identity, NOT Warren's `nguyen.s.khoa@gmail.com` calendar → Warren can't see them. Use OAuth for any user-visible calendar event. SA is fine for Sheets (data layer) only.

### 🔴 SA-created calendar events may be INVISIBLE to Warren (learned 2026-07-10)
`service_account.Credentials` + `events().insert(calendarId="nguyen.s.khoa@gmail.com")` — SA key can **read** that calendar (list succeeds) but a create is attributed to the SA, not Warren, UNLESS the SA is ACL-shared on the calendar or domain-wide delegation with `subject=` is set. In the 2026-07-10 session the SA list worked but a create would NOT appear in Warren's view. **Rule:** user-visible calendar events → OAuth only. Never silently fall back to SA for calendar creation.

### 🔴 OAuth re-auth flow (script pattern, verified 2026-07-10)
```python
# vault/scripts/google_reauth.py
import os, json
from google_auth_oauthlib.flow import InstalledAppFlow
HOME = r"C:/Users/khoans/AppData/Local/hermes/profiles/warren-profile"
CLIENT = os.path.join(HOME, "google_client_secret.json")
TOKEN  = os.path.join(HOME, "google_token.json")
SCOPES = ["https://www.googleapis.com/auth/calendar"]
cfg = json.load(open(CLIENT, encoding="utf-8"))
cfg = cfg.get("installed") or cfg.get("web") or cfg
flow = InstalledAppFlow.from_client_config(cfg, SCOPES)
flow.redirect_uri = "http://localhost:8080/"
creds = flow.run_local_server(port=8080, prompt="consent")
json.dump({"token":creds.token,"refresh_token":creds.refresh_token,"token_uri":creds.token_uri,
           "client_id":creds.client_id,"client_secret":creds.client_secret,
           "scopes":creds.scopes,"expiry":creds.expiry.isoformat() if creds.expiry else None},
          open(TOKEN,"w",encoding="utf-8"), indent=2, ensure_ascii=False)
# TOKEN keys written == keys read by create_oil_calendar_event.py (token, refresh_token,
# token_uri, client_id, client_secret) — verified compatible, no consumer change needed.
```
Run: `python3 vault/scripts/google_reauth.py` → browser → login `nguyen.s.khoa@gmail.com` → consent → `REAUTH OK`. Needs `google_auth_oauthlib` (Hermes venv has it). Port 8080 free.

### Idempotent create (check-before-insert, learned 2026-07-10)
Always `events().list()` + grep `summary` BEFORE insert. If found → `events().update()` (merge desc); else insert. Stops duplicate reminders on re-run.
```python
existing = [e for e in svc.events().list(calendarId=CAL_ID, timeMin="2026-01-01T00:00:00+07:00",
                                         singleEvents=False, maxResults=100).execute().get("items",[])
            if "P&L Breakdown" in e.get("summary","")]
if existing:
    eid = existing[0]["id"]; ev = svc.events().get(calendarId=CAL_ID, eventId=eid).execute()
    ev["description"] = NEW_DESC
    svc.events().update(calendarId=CAL_ID, eventId=eid, body=ev).execute()
else:
    svc.events().insert(calendarId=CAL_ID, body=EVENT).execute()
```

- **Multi-profile token copy** — Token từ profile A (warren-profile/personal_profile) có thể copy sang profile B (stock-profile) nếu cùng Google account. Cách làm:
  ```bash
  find ~/AppData/Local/hermes/profiles -name "google_token.json"
  cp <src>/google_token.json <dst>/google_token.json
  cp <src>/google_client_secret.json <dst>/google_client_secret.json
  python setup.py --check  # should now show AUTHENTICATED (partial)
  ```
  Nếu thiếu scope (partial) thì revoke + re-auth trên profile đích với `--auth-url`.

### Sheets read/write via Service Account (verified 2026-06-24)

```python
from google.oauth2 import service_account
from googleapiclient.discovery import build
from pathlib import Path

SA_KEY = Path(r'vault/_private/lusine-calendar-sa-key.json')
SHEET_ID = '1ZtIocc_Ic1z-tO1JGd4ZLnRB_7ZHHkvpJ5emaWJyeEE'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

creds = service_account.Credentials.from_service_account_file(SA_KEY, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)

# Read
result = service.spreadsheets().values().get(
    spreadsheetId=SHEET_ID,
    range="'02_MASTER_CPH'!A1:I10"
).execute()

# Write/update
body = {'values': [['202605', 'LU3', '82521', ...]]}
result = service.spreadsheets().values().update(
    spreadsheetId=SHEET_ID,
    range="'02_MASTER_CPH'!A3:I5",
    valueInputOption='RAW',
    body=body,
).execute()
```

### CLI (via push_gcal.py wrapper)
> ⚠️ **`push_gcal.py` uses a SERVICE ACCOUNT** — events it creates are INVISIBLE to Warren (land under SA identity, not `nguyen.s.khoa@gmail.com`). DO NOT use it for any user-visible reminder. For Warren-visible events, write an OAuth script (load `warren-profile/google_token.json`, `calendarId='nguyen.s.khoa@gmail.com'`) — see the OAUTH re-auth flow pattern above and `create_pl_calendar_event.py` / `create_hr_weekly_event.py` as proven examples.

```bash
cd vault && python scripts/push_gcal.py \
  --summary "Event title" \
  --date 2026-06-22 --time 18:00 --priority high \
  --rrule "FREQ=WEEKLY;BYDAY=MO"
```

### Python pattern

```python
from google.oauth2 import service_account
from googleapiclient.discovery import build
from pathlib import Path

SA_KEY = Path(r'vault/_private/lusine-calendar-sa-key.json')
CAL_ID = 'nguyen.s.khoa@gmail.com'
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

creds = service_account.Credentials.from_service_account_file(SA_KEY, scopes=SCOPES)
service = build('calendar', 'v3', credentials=creds)

event = {
    'summary': 'Title',
    'start': {'dateTime': '2026-06-22T18:00:00+07:00', 'timeZone': 'Asia/Ho_Chi_Minh'},
    'end': {'dateTime': '2026-06-22T18:15:00+07:00', 'timeZone': 'Asia/Ho_Chi_Minh'},
    'recurrence': ['RRULE:FREQ=WEEKLY;BYDAY=MO'],
}
created = service.events().insert(calendarId=CAL_ID, body=event).execute()
link = created.get('htmlLink')
eid  = created.get('id')
```

### Update / merge a step into an existing event (don't create duplicates)
When a follow-up already has a calendar event and a NEW step must be added (e.g. reschedule + new confirm-fee task), **modify the existing event** via get → update, NOT a second insert.
```python
eid = '<existing eventId>'   # from prior insert() response, or events().list() lookup
ev = service.events().get(calendarId=CAL_ID, eventId=eid).execute()
ev['description'] = ev['description'] + '\n\nNEW STEP: ...'
ev['summary'] = '...'  # optional rename
updated = service.events().update(calendarId=CAL_ID, eventId=eid, body=ev).execute()
# VERIFY
v = service.events().get(calendarId=CAL_ID, eventId=eid).execute()
assert 'NEW STEP' in v['description']
```
- **Why:** inserting a 2nd event for the same follow-up creates duplicate reminders. Merge instead.
- **Verify after update** same as insert: readback get() + assert keyword present.
- SA key at `%LOCALAPPDATA%/hermes/google_service_account.json` works for BOTH insert and update (verified: rebooked copyright event + merged W6 step into it, session 2026-07-09).

### 🚫 DO NOT use `calendarId='primary'`

`primary` = service account's own calendar — Warren CANNOT see it. Always use `nguyen.s.khoa@gmail.com`.

Scope: `calendar.events` (CRUD) is sufficient, no need for full `calendar` scope.

### Recurring event verification (learned 2026-07-07)
After `events().insert()`, DON'T trust "exit 0" — verify the event actually exists with a `events().get(calendarId=CAL_ID, eventId=created['id'])` call and assert: summary contains expected keyword, start/end `dateTime` match spec, `recurrence` == expected RRULE, `reminders.overrides` present, description length > 100. Write the verify as a temp `hermes-verify-` script, run, then delete. This is the calendar equivalent of the parser ad-hoc verify discipline — catches silent failures (wrong calendar, dropped fields).

### Warren-facing event description pattern
Warren is non-IT. The event `description` MUST include: (1) what data to fetch, (2) the exact CLI command to paste to Hermes, (3) what Hermes does automatically, (4) the dashboard/file path to open. Use copy-paste-ready blocks, Vietnamese, conclusion-first. Non-IT user = no jargon.

### RRULE monthly by day
`RRULE:FREQ=MONTHLY;BYMONTHDAY=8` fires every 8th. For "day 5" use `BYMONTHDAY=5`. Do NOT use `COUNT=12` unless Warren wants it to auto-expire — omit COUNT for a permanent recurring reminder.

### 🔴 Make a Warren-visible event RECURRING (google_api.py has no recurrence flag)
`google_api.py calendar create` supports NO `--recurrence`/`RRULE` arg (verified 2026-07-15).
To create a **recurring Warren-visible** event: (1) `calendar create` once via OAuth (lands on
`nguyen.s.khoa@gmail.com`), then (2) PATCH `recurrence` with a direct Calendar API call using the
stored refresh token. Full verified template: `references/oauth-recurring-event-patch.md`.
Key steps: refresh access_token from `google_token.json`+`google_client_secret.json` →
`PATCH https://www.googleapis.com/calendar/v3/calendars/primary/events/<EID>` with body
`{"recurrence":["RRULE:FREQ=WEEKLY;BYDAY=TU"]}` → assert `recurrence` in the response. NEVER use SA for this.

### When to use which

| Approach | When | Setup needed |
|----------|------|-------------|
| **OAuth** (default flow) | Gmail/Drive/Docs full access, or when SA key lacks required scope | Google Cloud Console + browser auth |
| **Service Account** | Calendar events + **Google Sheets read/write** (CPH updates, COL log, dashboard data) | SA key already in vault/_private/ |

### Pitfalls

- **Calendar link 500 error** → Check `calendarId`. `primary` always fails for users. Must be user's email.
- **SA key not found at vault/_private/** → The SA key is NOT at `vault/_private/lusine-calendar-sa-key.json`. It's at `%LOCALAPPDATA%/hermes/google_service_account.json`. Search for it with `find /c/Users/khoans -name "*google_service_account*"`.
- **SA key lacks Sheets scope** → If `spreadsheets` scope returns 403, the SA key needs `spreadsheets` scope enabled in Google Cloud Console → APIs & Services → Enable APIs. The SA key at this path was verified working for Sheets on 2026-06-24.
- **OAuth path mismatch** — `google_token.json` exists at `~/.hermes/` but `setup.py --check` looks in `profiles/*/home/`. Use service account for calendar instead.
- **Scope confusion** — `calendar.events` ≠ `calendar`. If you need event CRUD only, use `calendar.events`. Full `calendar` scope gives access to settings, ACL, etc.
- **Recurring events need RRULE** — Use RFC 5545 format: `FREQ=WEEKLY;BYDAY=MO`. Non-recurring events omit this field.
- **Scope substring check** — `'spreadsheets' in scopes_list` always fails because scopes are full URLs. Use `any('spreadsheets' in s for s in scopes_list)`.
- **CPH sheet range** — Must use `A1:I` (9 columns), NOT `A1:H`. Column I holds Cleaner CPH; cutting it off makes all Cleaner rates `None`.
- **CPH comma handling** — CPH values like `'81,173'` must be `.replace(',', '')` before `float()`. See `references/lusine-sheets-structure.md` for all Sheets-specific gotchas.
- **Hourly Revenue column layout** — Tab `09_Hourly_Cover_Revenue_Log` có column layout bất thường do merged cells. Xem `references/hourly-revenue-column-layout.md` cho column mapping + parsing rules.
- **🔴 MSYS path conversion breaks Python script paths (learned 2026-07-17)**: On this Windows host, `terminal` runs via git-bash/MSYS. Using `$HOME` or `/c/Users/...` style paths in a Python invocation string gets double-converted — e.g. `$HOME/.hermes/skills/...` resolves to `/c/Users/khoans` (drops `AppData/Local/hermes/profiles/warren-profile`), and `/c/Users/khoans/...` becomes `\\c\\Users\\khoans\\...` (Python `FileNotFoundError`). **Fix:** always pass **native Windows paths** (`C:/Users/khoans/AppData/Local/hermes/profiles/warren-profile/...`) to `python` in terminal calls. Inside the Python script itself, `Path(r"C:/Users/...")` or `os.environ["LOCALAPPDATA"]` work fine — only the *shell-level* invocation string needs native form. Verified: `python C:/Users/khoans/AppData/Local/hermes/profiles/warren-profile/skills/productivity/google-workspace/scripts/setup.py --check` → `AUTHENTICATED`, whereas the MSYS-style equivalent failed.

## References

- `references/oauth-recurring-event-patch.md` — make a Warren-visible OAuth event recurring via direct API PATCH (google_api.py lacks --recurrence)
- `references/service-account-calendar.md` — service account event creation guide
- `references/lusine-sheets-structure.md` — L'Usine sheet tabs, CPH parsing gotchas (9-column range, comma handling), COL append pattern
