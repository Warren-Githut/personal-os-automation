---
date: "2026-06-19"
type: reference
domain: ops
topic: weekly-calendar-reminder
---

# Weekly Calendar Reminder: system-thinker-structure

Created 2026-06-19 as a recurring event on Warren's Google Calendar.

## Event Details

- **Summary:** `system-thinker-structure — Vault Health Check`
- **Schedule:** Every Monday, 18:00 → 18:15 (Asia/Ho_Chi_Minh)
- **Reminder:** Popup 10 minutes before
- **Calendar:** `nguyen.s.khoa@gmail.com` (Warren's work calendar)
- **Event ID:** `11djgtuvajvomp1hrudvdof4fg`
- **Link:** https://www.google.com/calendar/event?eid=MTFkamd0dXZhanZvbXAxaHJ1ZHZkb2Y0ZmdfMjAyNjA2MjJUMTgwMDAwWiBuZ3V5ZW4ucy5raG9hQG0

## Description (in event body)

Paste-friendly command to run every Monday:

```
/system-thinker-structure --quick --execute
```

## Recreate if deleted

```python
from google.oauth2 import service_account
from googleapiclient.discovery import build
from pathlib import Path
from datetime import datetime, timedelta, timezone

SA_KEY = Path(r'vault/_private/lusine-calendar-sa-key.json')
CALENDAR_ID = 'nguyen.s.khoa@gmail.com'
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

creds = service_account.Credentials.from_service_account_file(SA_KEY, scopes=SCOPES)
service = build('calendar', 'v3', credentials=creds)

today = datetime.now(timezone.utc)
days_ahead = (7 - today.weekday()) % 7
if days_ahead == 0: days_ahead = 7
next_monday = today + timedelta(days=days_ahead)
start = next_monday.replace(hour=18, minute=0, second=0, microsecond=0)

event = {
    'summary': 'system-thinker-structure — Vault Health Check',
    'description': 'MONDAY WEEKLY — Vault Health Check\n\n/system-thinker-structure --quick --execute',
    'start': {'dateTime': start.isoformat(), 'timeZone': 'Asia/Ho_Chi_Minh'},
    'end': {'dateTime': (start + timedelta(minutes=15)).isoformat(), 'timeZone': 'Asia/Ho_Chi_Minh'},
    'recurrence': ['RRULE:FREQ=WEEKLY;BYDAY=MO'],
    'reminders': {'useDefault': False, 'overrides': [{'method': 'popup', 'minutes': 10}]},
    'colorId': '3',
}
created = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
```

## Notes

- Created using service account (not OAuth), see `lusine-google-workspace-ops` skill's `references/service-account-calendar.md`
- First attempt failed (500 error) because `calendarId='primary'` pointed to SA calendar. Fixed by using `nguyen.s.khoa@gmail.com`