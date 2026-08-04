---
date: "2026-06-19"
type: reference
domain: google-calendar
topic: service-account-event-creation
---

# Service Account: Calendar Event Creation

## Credentials

- SA key: `vault/_private/lusine-calendar-sa-key.json`
- SA email: `google-calendar-service-accoun@warren-os.iam.gserviceaccount.com`
- Target calendar: `nguyen.s.khoa@gmail.com` (Warren's work calendar)
- `.env` file: `vault/.env` at vault root

## Required env vars

```
GOOGLE_SA_CREDENTIALS=<path_to_vault/_private/lusine-calendar-sa-key.json>
GOOGLE_CALENDAR_ID=nguyen.s.khoa@gmail.com
```

## Python pattern

```python
from google.oauth2 import service_account
from googleapiclient.discovery import build

SA_KEY = Path(r'vault/_private/lusine-calendar-sa-key.json')
CALENDAR_ID = 'nguyen.s.khoa@gmail.com'
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

creds = service_account.Credentials.from_service_account_file(SA_KEY, scopes=SCOPES)
service = build('calendar', 'v3', credentials=creds)

created = service.events().insert(calendarId=CALENDAR_ID, body=EVENT).execute()
```

## Critical: calendarId

**DO NOT use `calendarId='primary'`.** `primary` = service account's own calendar, which Warren cannot see. Always use `nguyen.s.khoa@gmail.com`.

## CLI wrapper

`vault/scripts/push_gcal.py` wraps this into a CLI:

```bash
cd vault && python scripts/push_gcal.py \
  --summary "vault-structure-audit — Vault Health Check" \
  --date 2026-06-22 --time 18:00 --priority high \
  --rrule "FREQ=WEEKLY;BYDAY=MO" \
  --description "Full details here"
```

## OAuth vs Service Account

| Factor | OAuth | Service Account |
|--------|-------|----------------|
| Browser login | Required (once) | Never |
| Scope | Full Gmail/Drive/Calendar | Calendar only |
| Token refresh | Auto (1 week) | N/A |
| Path issue | `setup.py` looks at wrong HOME | Direct path |
| Reliability | Token path can drift | Stable if SA key path fixed |