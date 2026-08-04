# Make an OAuth (Warren-visible) Calendar event RECURRING via direct API PATCH

> `google_api.py calendar create` has **NO `--recurrence` flag** (verified 2026-07-15).
> If you need a repeating Warren-visible event, create it once via `google_api.py calendar create`
> (so it lands on `nguyen.s.khoa@gmail.com` via OAuth), then PATCH `recurrence` with this script.
> NEVER use the Service Account for calendar events — SA events are invisible to Warren.

## Prereqs
- `warren-profile/google_token.json` exists (OAuth, key `token` + `refresh_token`).
- `warren-profile/google_client_secret.json` exists (OAuth client).
- Calendar scope present (check: `setup.py --check`; calendar scope is in the default SCOPES list).

## Verified template (2026-07-15, real run)
```python
import json, urllib.request, urllib.parse, os
from pathlib import Path

HOME = Path(os.environ.get("HERMES_HOME",
            Path.home() / ".hermes" / "profiles" / "warren-profile"))
tok = json.loads((HOME / "google_token.json").read_text(encoding="utf-8"))
sec = json.loads((HOME / "google_client_secret.json").read_text(encoding="utf-8"))
ci = sec.get("client_id") or sec.get("installed", {}).get("client_id")
cs = sec.get("client_secret") or sec.get("installed", {}).get("client_secret")
refresh = tok.get("refresh_token")
assert refresh, "NO REFRESH TOKEN"

# 1) refresh access token
data = urllib.parse.urlencode({
    "client_id": ci, "client_secret": cs,
    "refresh_token": refresh, "grant_type": "refresh_token"
}).encode()
req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data, method="POST")
access = json.loads(urllib.request.urlopen(req, timeout=20).read())["access_token"]

# 2) PATCH recurrence onto an existing event
EID = "<eventId from calendar create response>"
url = f"https://www.googleapis.com/calendar/v3/calendars/primary/events/{EID}?access_token={access}"

desc = "..."  # your Warren-facing description (Vietnamese, copy-paste-ready)
body = {
    "summary": "Tuesday Skills Audit (Hermes) - weekly",
    "description": desc,
    "recurrence": ["RRULE:FREQ=WEEKLY;BYDAY=TU"]
}
req2 = urllib.request.Request(url, data=json.dumps(body).encode(), method="PATCH",
                               headers={"Content-Type": "application/json"})
r2 = json.loads(urllib.request.urlopen(req2, timeout=20).read())
print("recurrence:", r2.get("recurrence"))
print("next start:", r2.get("start", {}).get("dateTime"))
```

## Notes
- `calendars/primary` resolves to Warren's primary calendar for the authenticated OAuth user — safe here.
- RRULE: weekly Tuesday = `FREQ=WEEKLY;BYDAY=TU`. Omit `COUNT` for permanent.
- VERIFY after PATCH: `events().get()` assert `recurrence` == expected RRULE (don't trust exit 0).
- Keep the script as a temp `hermes-verify-*.py`, run, then `rm` it.
- `calendarId` for insert: use `nguyen.s.khoa@gmail.com` (or `primary` for the OAuth user) — NOT the SA key.
